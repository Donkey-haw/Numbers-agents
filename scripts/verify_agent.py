import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import agent_runtime  # noqa: E402
import generate_numbers_lesson as textbook  # noqa: E402
import pipeline_contracts as contracts  # noqa: E402
import render_pipeline_support as render_support  # noqa: E402
import run_gemini_cli_pipeline as gemini_pipeline  # noqa: E402


def build_verify_rule_review(output_file: Path) -> dict:
    findings = []
    blocking_issues = []
    warnings = []

    if not output_file.exists():
        blocking_issues.append(f"final output does not exist: {output_file}")
    else:
        findings.append(
            {
                "severity": "info",
                "message": "최종 Numbers 파일이 생성되어 있습니다.",
                "evidence_refs": [str(output_file)],
            }
        )

    decision = "pass"
    status = "succeeded"
    if blocking_issues:
        decision = "blocked"
        status = "blocked"
    elif warnings:
        decision = "pass_with_warning"
        status = "succeeded_with_warning"

    return {
        "schema_version": contracts.SCHEMA_VERSION,
        "stage": "review_verify_rule_agent",
        "lesson_id": None,
        "status": status,
        "decision": decision,
        "findings": findings,
        "blocking_issues": blocking_issues,
        "warnings": warnings,
    }


def validate_review_result(payload: dict) -> None:
    schema = gemini_pipeline.load_schema(PROJECT_ROOT / "schemas" / "review_result.schema.json")
    gemini_pipeline.ensure_required_fields(payload, schema["required"], "review_result")
    if payload.get("decision") not in contracts.REVIEW_DECISION_VALUES:
        raise ValueError("review_result.decision is invalid")
    if payload.get("status") not in contracts.STAGE_STATUS_VALUES:
        raise ValueError("review_result.status is invalid")


def build_verify_ai_review_prompt(*, output_file: Path, verify_rule_review: dict, run_manifest: dict) -> str:
    compact_manifest = {
        "run_id": run_manifest.get("run_id"),
        "final_status": run_manifest.get("final_status"),
        "selected_unit": run_manifest.get("selected_unit"),
        "stage_summary": run_manifest.get("status_summary", []),
    }
    task_prompt = (
        "너의 역할은 최종 verify 결과를 사후 검토하는 review-only agent다.\n"
        "파일을 수정하거나 다시 생성하지 마라.\n"
        "review_result JSON 하나만 반환하라.\n"
        "마크다운, 설명문, 코드블록 없이 JSON object 하나만 반환하라.\n"
        "stage는 review_verify_agent로 써라.\n"
        "decision은 pass, pass_with_warning, needs_revision, blocked 중 하나여야 한다.\n"
        "status는 succeeded, succeeded_with_warning, blocked 중 하나여야 한다.\n"
        "findings의 각 항목은 severity, message, evidence_refs만 가져야 한다.\n\n"
        "Final output path:\n"
        + str(output_file)
        + "\n\nRule review:\n"
        + gemini_pipeline.json.dumps(verify_rule_review, ensure_ascii=False, indent=2)
        + "\n\nRun manifest summary:\n"
        + gemini_pipeline.json.dumps(compact_manifest, ensure_ascii=False, indent=2)
        + "\n\nSchema:\n"
        + gemini_pipeline.read_text(PROJECT_ROOT / "schemas" / "review_result.schema.json")
    )
    return agent_runtime.build_agent_prompt(agent_name="verify_agent", task_prompt=task_prompt)


def build_verify_ai_review_fallback(verify_rule_review: dict, exc: Exception) -> dict:
    review = {
        "schema_version": contracts.SCHEMA_VERSION,
        "stage": "review_verify_agent",
        "lesson_id": None,
        "status": verify_rule_review["status"],
        "decision": verify_rule_review["decision"],
        "findings": list(verify_rule_review.get("findings", [])),
        "blocking_issues": list(verify_rule_review.get("blocking_issues", [])),
        "warnings": list(verify_rule_review.get("warnings", [])),
    }
    review["findings"].insert(
        0,
        {
            "severity": "info",
            "message": f"AI verify review fallback used: {exc}",
            "evidence_refs": [],
        },
    )
    return review


def execute_verify(
    *,
    run_root: Path,
    run_id: str,
    gemini_bin: str = "gemini",
    gemini_model: str | None = None,
    gemini_extensions: list[str] | None = None,
    approval_mode: str = "yolo",
    debug_artifacts: bool = False,
    gemini_timeout_sec: int = 60,
) -> dict:
    config = render_support.load_run_config(run_root)
    status_path = run_root / "output" / "verify.status.json"
    output_file = Path(config["output_file"])
    status = {
        "schema_version": contracts.SCHEMA_VERSION,
        "stage": "verify_agent",
        "lesson_id": None,
        "status": "running",
        "run_id": run_id,
        "started_at": contracts.utc_now(),
        "finished_at": None,
        "input_refs": [str(output_file)],
        "output_refs": [
            str(status_path),
            str(run_root / "output" / "verify_rule_review.json"),
            str(run_root / "output" / "verify_review.json"),
        ],
        "fallback_used": False,
        "warnings": [],
        "errors": [],
        "agent_spec_path": str(agent_runtime.agent_doc_path("verify_agent")),
        "model": gemini_model or gemini_bin,
    }
    contracts.write_json(status_path, status)
    textbook.verify_output(config)
    verify_rule_review = build_verify_rule_review(output_file)
    contracts.write_json(run_root / "output" / "verify_rule_review.json", verify_rule_review)

    try:
        run_manifest = render_support.read_json(run_root / "run_manifest.json")
        prompt = build_verify_ai_review_prompt(
            output_file=output_file,
            verify_rule_review=verify_rule_review,
            run_manifest=run_manifest,
        )
        (run_root / "output" / "verify_review.prompt.md").write_text(prompt, encoding="utf-8")
        ai_review, _ = gemini_pipeline.invoke_gemini_json(
            prompt=prompt,
            artifact_dir=run_root / "output",
            stem="verify_review",
            gemini_bin=gemini_bin,
            gemini_model=gemini_model,
            gemini_extensions=gemini_extensions or ["stitch-skills"],
            approval_mode=approval_mode,
            debug_artifacts=debug_artifacts,
            timeout_sec=gemini_timeout_sec,
        )
        validate_review_result(ai_review)
        ai_review.setdefault("schema_version", contracts.SCHEMA_VERSION)
        ai_review["stage"] = "review_verify_agent"
        contracts.write_json(run_root / "output" / "verify_review.json", ai_review)
    except Exception as exc:
        status["warnings"].append(f"verify_review fallback used: {exc}")
        fallback_review = build_verify_ai_review_fallback(verify_rule_review, exc)
        contracts.write_json(run_root / "output" / "verify_review.json", fallback_review)

    status["status"] = "succeeded"
    status["finished_at"] = contracts.utc_now()
    contracts.write_json(status_path, status)
    return {
        "output_file": output_file,
        "warning_count": len(status["warnings"]),
    }
