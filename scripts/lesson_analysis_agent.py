import concurrent.futures
import json
import shutil
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import pipeline_contracts as contracts  # noqa: E402
import run_gemini_cli_pipeline as gemini_pipeline  # noqa: E402


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def section_dir(run_root: Path, section: dict) -> Path:
    lesson_dir = run_root / "sections" / contracts.sanitize_name(section["card_file"])
    lesson_dir.mkdir(parents=True, exist_ok=True)
    return lesson_dir


def build_lesson_status(run_id: str, lesson_id: str, started_at: str, input_refs: list[str], output_refs: list[str]) -> dict:
    return {
        "schema_version": contracts.SCHEMA_VERSION,
        "stage": "lesson_analysis_agent",
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
        "model": None,
        "attempt_count": 0,
        "validation_errors": [],
    }


def build_lesson_review(lesson_id: str, analysis: dict) -> dict:
    findings = []
    warnings = []
    blocking_issues = []
    decision = "pass"

    if not analysis.get("learning_goals"):
        blocking_issues.append("learning_goals is empty")
    if not analysis.get("key_concepts"):
        blocking_issues.append("key_concepts is empty")
    if not analysis.get("source_page_refs"):
        blocking_issues.append("source_page_refs is empty")
    if not analysis.get("misconceptions"):
        warnings.append("misconceptions is empty")
        findings.append(
            {
                "severity": "warning",
                "message": "오개념 후보가 비어 있습니다.",
                "evidence_refs": [],
            }
        )
    if analysis.get("notes"):
        findings.append(
            {
                "severity": "info",
                "message": analysis["notes"],
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

    return {
        "schema_version": contracts.SCHEMA_VERSION,
        "stage": "review_lesson_agent",
        "lesson_id": lesson_id,
        "status": status,
        "decision": decision,
        "findings": findings,
        "blocking_issues": blocking_issues,
        "warnings": warnings,
    }


def process_section(
    *,
    section: dict,
    run_root: Path,
    run_id: str,
    source_dir: Path,
    schedule_draft: dict,
    textbook_context: dict,
    gemini_bin: str,
    gemini_model: str | None,
    extensions: list[str],
    approval_mode: str,
    debug_artifacts: bool,
    gemini_timeout_sec: int,
) -> dict:
    lesson_dir = section_dir(run_root, section)
    started_at = contracts.utc_now()
    baseline_path = source_dir / "local_baseline" / f"{section['card_file']}.lesson_analysis.json"
    baseline_analysis = read_json(baseline_path)

    analysis_path = lesson_dir / "lesson_analysis.json"
    ai_path = lesson_dir / "lesson_analysis_ai.json"
    review_path = lesson_dir / "lesson_review.json"
    status_path = lesson_dir / "lesson_analysis.status.json"

    status = build_lesson_status(
        run_id=run_id,
        lesson_id=section["sheet_name"],
        started_at=started_at,
        input_refs=[
            str(source_dir / "schedule_draft.json"),
            str(source_dir / "textbook_context.json"),
            str(baseline_path),
        ],
        output_refs=[str(ai_path), str(analysis_path), str(review_path)],
    )
    status["model"] = gemini_model or gemini_bin
    contracts.write_json(status_path, status)

    fallback_used = False
    warning_used = False
    try:
        prompt_context = gemini_pipeline.build_section_prompt_context(textbook_context, section["sheet_name"])
        contracts.write_json(lesson_dir / "lesson_analysis.context.json", prompt_context)
        prompt = gemini_pipeline.build_lesson_prompt(section, baseline_analysis, schedule_draft, prompt_context)
        (lesson_dir / "lesson_analysis.prompt.md").write_text(prompt, encoding="utf-8")
        status["attempt_count"] = 1
        lesson_ai, _ = gemini_pipeline.invoke_gemini_json(
            prompt=prompt,
            artifact_dir=lesson_dir,
            stem="lesson_analysis_ai",
            gemini_bin=gemini_bin,
            gemini_model=gemini_model,
            gemini_extensions=extensions,
            approval_mode=approval_mode,
            debug_artifacts=debug_artifacts,
            timeout_sec=gemini_timeout_sec,
        )
        contracts.write_json(ai_path, lesson_ai)
        normalized = gemini_pipeline.normalize_lesson_analysis(lesson_ai, baseline_analysis)
        status["status"] = "succeeded"
    except Exception as exc:
        fallback_used = True
        status["status"] = "failed_fallback_used"
        status["fallback_used"] = True
        status["errors"].append(str(exc))
        normalized = json.loads(json.dumps(baseline_analysis, ensure_ascii=False))
        normalized["notes"] = f"{normalized.get('notes', '')} Gemini fallback used: {exc}".strip()
        shutil.copy2(baseline_path, analysis_path)
    else:
        contracts.write_json(analysis_path, normalized)

    review = build_lesson_review(section["sheet_name"], normalized)
    warning_used = review["decision"] != "pass"
    contracts.write_json(review_path, review)

    status["finished_at"] = contracts.utc_now()
    if review["decision"] == "blocked":
        status["status"] = "blocked"
        status["warnings"].append("lesson review blocked downstream progression")
    elif review["decision"] == "pass_with_warning" and status["status"] == "succeeded":
        status["status"] = "succeeded_with_warning"
    contracts.write_json(status_path, status)

    return {
        "analysis_path": analysis_path,
        "review_path": review_path,
        "fallback_used": fallback_used,
        "warning_used": warning_used,
        "lesson_id": section["sheet_name"],
    }


def execute_lesson_analysis(
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
    source_dir = run_root / "source"
    runtime_config = read_json(source_dir / "runtime_config.json")
    schedule_draft = read_json(source_dir / "schedule_draft.json")
    textbook_context = read_json(source_dir / "textbook_context.json")
    extensions = gemini_extensions or ["stitch-skills"]

    analyses = []
    review_paths = []
    fallback_count = 0
    warning_count = 0

    ordered_results: dict[str, dict] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, max_workers)) as executor:
        futures = {
            executor.submit(
                process_section,
                section=section,
                run_root=run_root,
                run_id=run_id,
                source_dir=source_dir,
                schedule_draft=schedule_draft,
                textbook_context=textbook_context,
                gemini_bin=gemini_bin,
                gemini_model=gemini_model,
                extensions=extensions,
                approval_mode=approval_mode,
                debug_artifacts=debug_artifacts,
                gemini_timeout_sec=gemini_timeout_sec,
            ): section["sheet_name"]
            for section in runtime_config["sections"]
        }
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            ordered_results[result["lesson_id"]] = result

    for section in runtime_config["sections"]:
        result = ordered_results[section["sheet_name"]]
        analyses.append(result["analysis_path"])
        review_paths.append(result["review_path"])
        if result["fallback_used"]:
            fallback_count += 1
        if result["warning_used"]:
            warning_count += 1

    return {
        "analysis_paths": analyses,
        "review_paths": review_paths,
        "fallback_count": fallback_count,
        "warning_count": warning_count,
    }
