import concurrent.futures
import json
import shutil
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import generate_activity_plan as local_activity_builder  # noqa: E402
import pipeline_contracts as contracts  # noqa: E402
import run_gemini_cli_pipeline as gemini_pipeline  # noqa: E402


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_activity_status(run_id: str, lesson_id: str, started_at: str, input_refs: list[str], output_refs: list[str]) -> dict:
    return {
        "schema_version": contracts.SCHEMA_VERSION,
        "stage": "activity_plan_agent",
        "lesson_id": lesson_id,
        "status": "running",
        "run_id": run_id,
        "started_at": started_at,
        "finished_at": None,
        "input_refs": input_refs,
        "output_refs": output_refs,
        "fallback_used": False,
        "warnings": [],
        "errors": [],
        "attempt_count": 0,
        "repair_attempted": False,
        "validation_errors": [],
    }


def build_activity_review(lesson_id: str, plan: dict, analysis: dict) -> dict:
    findings = []
    warnings = []
    blocking_issues = []
    decision = "pass"

    activities = plan.get("activities", [])
    if not activities:
        blocking_issues.append("activities is empty")

    for index, activity in enumerate(activities, start=1):
        if not activity.get("source_refs"):
            blocking_issues.append(f"activity[{index}] source_refs is empty")
        if not activity.get("student_writing_zones"):
            blocking_issues.append(f"activity[{index}] student_writing_zones is empty")
        if activity.get("lesson_flow_stage") not in {"before", "during", "after"}:
            blocking_issues.append(f"activity[{index}] lesson_flow_stage is invalid")
        if activity.get("object_role") not in {
            "learning_note",
            "activity_area",
            "reference_material",
            "worksheet",
            "ai_courseware",
        }:
            blocking_issues.append(f"activity[{index}] object_role is invalid")
        if activity.get("prompt_text", "").strip() == analysis.get("lesson_title", "").strip():
            warnings.append(f"activity[{index}] prompt_text too close to lesson title")
            findings.append(
                {
                    "severity": "warning",
                    "message": "활동 문구가 차시명을 거의 그대로 반복합니다.",
                    "evidence_refs": [activity.get("activity_id", f"activity-{index}")],
                }
            )

    lesson_flow_stages = {activity.get("lesson_flow_stage") for activity in activities}
    if "during" not in lesson_flow_stages:
        warnings.append("No during-stage activity was generated")
        findings.append(
            {
                "severity": "warning",
                "message": "수업 중 활동이 보이지 않습니다.",
                "evidence_refs": [],
            }
        )

    if blocking_issues:
        decision = "blocked"
    elif warnings:
        decision = "pass_with_warning"

    status = "succeeded" if decision == "pass" else "succeeded_with_warning"
    if decision == "blocked":
        status = "blocked"

    if plan.get("notes"):
        findings.append(
            {
                "severity": "info",
                "message": plan["notes"],
                "evidence_refs": [],
            }
        )

    return {
        "schema_version": contracts.SCHEMA_VERSION,
        "stage": "review_activity_agent",
        "lesson_id": lesson_id,
        "status": status,
        "decision": decision,
        "findings": findings,
        "blocking_issues": blocking_issues,
        "warnings": warnings,
    }


def process_lesson_dir(
    *,
    lesson_dir: Path,
    run_id: str,
    extensions: list[str],
    gemini_bin: str,
    gemini_model: str | None,
    approval_mode: str,
    debug_artifacts: bool,
    gemini_timeout_sec: int,
) -> dict:
    analysis_path = lesson_dir / "lesson_analysis.json"
    analysis = read_json(analysis_path)
    lesson_id = analysis["lesson_id"]
    started_at = contracts.utc_now()

    plan_path = lesson_dir / "activity_plan.json"
    ai_path = lesson_dir / "activity_plan_ai.json"
    review_path = lesson_dir / "activity_review.json"
    status_path = lesson_dir / "activity_plan.status.json"

    status = build_activity_status(
        run_id=run_id,
        lesson_id=lesson_id,
        started_at=started_at,
        input_refs=[str(analysis_path)],
        output_refs=[str(ai_path), str(plan_path), str(review_path)],
    )
    contracts.write_json(status_path, status)

    fallback_used = False
    warning_used = False
    try:
        prompt = gemini_pipeline.build_activity_prompt(analysis)
        (lesson_dir / "activity_plan.prompt.md").write_text(prompt, encoding="utf-8")
        status["attempt_count"] = 1
        activity_ai, _ = gemini_pipeline.invoke_gemini_json(
            prompt=prompt,
            artifact_dir=lesson_dir,
            stem="activity_plan_ai",
            gemini_bin=gemini_bin,
            gemini_model=gemini_model,
            gemini_extensions=extensions,
            approval_mode=approval_mode,
            debug_artifacts=debug_artifacts,
            timeout_sec=gemini_timeout_sec,
        )
        contracts.write_json(ai_path, activity_ai)
        try:
            normalized = gemini_pipeline.normalize_activity_plan(activity_ai, analysis)
            status["status"] = "succeeded"
        except Exception as validation_exc:
            status["repair_attempted"] = True
            status["validation_errors"].append(str(validation_exc))
            repair_prompt = gemini_pipeline.build_activity_repair_prompt(analysis, activity_ai, str(validation_exc))
            (lesson_dir / "activity_plan.repair.prompt.md").write_text(repair_prompt, encoding="utf-8")
            status["attempt_count"] = 2
            repaired_ai, _ = gemini_pipeline.invoke_gemini_json(
                prompt=repair_prompt,
                artifact_dir=lesson_dir,
                stem="activity_plan_ai_repair",
                gemini_bin=gemini_bin,
                gemini_model=gemini_model,
                gemini_extensions=extensions,
                approval_mode=approval_mode,
                debug_artifacts=debug_artifacts,
                timeout_sec=gemini_timeout_sec,
            )
            contracts.write_json(lesson_dir / "activity_plan_ai_repair.json", repaired_ai)
            normalized = gemini_pipeline.normalize_activity_plan(repaired_ai, analysis)
            status["status"] = "succeeded_with_warning"
    except Exception as exc:
        fallback_used = True
        status["status"] = "failed_fallback_used"
        status["fallback_used"] = True
        status["errors"].append(str(exc))
        normalized = local_activity_builder.build_activity_plan(analysis)
        normalized["notes"] = f"Gemini fallback used: {exc}"
        contracts.write_json(plan_path, normalized)
    else:
        contracts.write_json(plan_path, normalized)

    review = build_activity_review(lesson_id, normalized, analysis)
    warning_used = review["decision"] != "pass"
    contracts.write_json(review_path, review)

    status["finished_at"] = contracts.utc_now()
    if review["decision"] == "blocked":
        status["status"] = "blocked"
        status["warnings"].append("activity review blocked downstream progression")
    elif review["decision"] == "pass_with_warning" and status["status"] == "succeeded":
        status["status"] = "succeeded_with_warning"
    contracts.write_json(status_path, status)

    return {
        "plan_path": plan_path,
        "review_path": review_path,
        "fallback_used": fallback_used,
        "warning_used": warning_used,
        "lesson_id": lesson_id,
    }


def execute_activity_planning(
    *,
    run_root: Path,
    run_id: str,
    gemini_bin: str = "gemini",
    gemini_model: str | None = None,
    gemini_extensions: list[str] | None = None,
    approval_mode: str = "yolo",
    debug_artifacts: bool = False,
    gemini_timeout_sec: int = 90,
    max_workers: int = 2,
) -> dict:
    sections_root = run_root / "sections"
    extensions = gemini_extensions or ["stitch-skills"]

    plan_paths = []
    review_paths = []
    fallback_count = 0
    warning_count = 0

    lesson_dirs = sorted(path for path in sections_root.iterdir() if path.is_dir())
    ordered_results: dict[str, dict] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, max_workers)) as executor:
        futures = {
            executor.submit(
                process_lesson_dir,
                lesson_dir=lesson_dir,
                run_id=run_id,
                extensions=extensions,
                gemini_bin=gemini_bin,
                gemini_model=gemini_model,
                approval_mode=approval_mode,
                debug_artifacts=debug_artifacts,
                gemini_timeout_sec=gemini_timeout_sec,
            ): lesson_dir.name
            for lesson_dir in lesson_dirs
        }
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            ordered_results[result["lesson_id"]] = result

    for lesson_dir in lesson_dirs:
        lesson_id = read_json(lesson_dir / "lesson_analysis.json")["lesson_id"]
        result = ordered_results[lesson_id]
        plan_paths.append(result["plan_path"])
        review_paths.append(result["review_path"])
        if result["fallback_used"]:
            fallback_count += 1
        if result["warning_used"]:
            warning_count += 1

    return {
        "plan_paths": plan_paths,
        "review_paths": review_paths,
        "fallback_count": fallback_count,
        "warning_count": warning_count,
    }
