import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import agent_runtime  # noqa: E402
import pipeline_contracts as contracts  # noqa: E402
import render_pipeline_support as render_support  # noqa: E402
import run_gemini_cli_pipeline as gemini_pipeline  # noqa: E402


def build_rule_review(manifest: dict) -> dict:
    findings = []
    blocking_issues = []
    warnings = []

    assets_by_sheet = {}
    for asset in manifest.get("assets", []):
        assets_by_sheet.setdefault(asset["sheet_name"], []).append(asset)

    for sheet_name, assets in assets_by_sheet.items():
        ordered = sorted(assets, key=lambda item: item["insert_order"])
        if not ordered:
            blocking_issues.append(f"{sheet_name}: no assets")
            continue
        if ordered[0]["asset_type"] != "textbook_card":
            warnings.append(f"{sheet_name}: first asset is not textbook_card")
            findings.append(
                {
                    "severity": "warning",
                    "message": "교과서 카드가 첫 번째 위치에 있지 않습니다.",
                    "evidence_refs": [sheet_name],
                }
            )
        flow = [item.get("lesson_flow_stage") for item in ordered if item["asset_type"] == "activity_sheet"]
        if flow and flow != sorted(flow, key=lambda name: {"before": 0, "during": 1, "after": 2}.get(name, 99)):
            warnings.append(f"{sheet_name}: activity flow order is not before/during/after")

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
        "stage": "review_manifest_rule_agent",
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


def build_manifest_ai_review_prompt(manifest: dict, rule_review: dict) -> str:
    compact_manifest = {
        "asset_count": len(manifest.get("assets", [])),
        "sheet_names": sorted({asset.get("sheet_name") for asset in manifest.get("assets", [])}),
        "assets": [
            {
                "sheet_name": asset.get("sheet_name"),
                "asset_type": asset.get("asset_type"),
                "insert_order": asset.get("insert_order"),
                "lesson_flow_stage": asset.get("lesson_flow_stage"),
                "x": asset.get("x"),
                "y": asset.get("y"),
                "width": asset.get("width"),
                "height": asset.get("height"),
            }
            for asset in manifest.get("assets", [])[:120]
        ],
    }
    task_prompt = (
        "너의 역할은 render manifest를 사후 검토하는 review-only agent다.\n"
        "manifest를 수정하거나 재배치안을 직접 실행하지 마라.\n"
        "아래 자료를 보고 review_result JSON 하나만 반환하라.\n"
        "마크다운, 설명문, 코드블록 없이 JSON object 하나만 반환하라.\n"
        "최상단 문자와 마지막 문자는 반드시 중괄호여야 한다.\n"
        "stage는 review_manifest_agent로 써라.\n"
        "decision은 pass, pass_with_warning, needs_revision, blocked 중 하나여야 한다.\n"
        "status는 succeeded, succeeded_with_warning, blocked 중 하나여야 한다.\n"
        "findings의 각 항목은 severity, message, evidence_refs만 가져야 한다.\n"
        "NumbersDesign.md 관점에서 객체 순서와 흐름이 자연스러운지 검토하라.\n\n"
        "Rule review:\n"
        + gemini_pipeline.json.dumps(rule_review, ensure_ascii=False, indent=2)
        + "\n\nRender manifest summary:\n"
        + gemini_pipeline.json.dumps(compact_manifest, ensure_ascii=False, indent=2)
        + "\n\nSchema:\n"
        + gemini_pipeline.read_text(PROJECT_ROOT / "schemas" / "review_result.schema.json")
    )
    return agent_runtime.build_agent_prompt(agent_name="review_manifest_agent", task_prompt=task_prompt)


def build_manifest_ai_review_fallback(rule_review: dict, exc: Exception) -> dict:
    review = {
        "schema_version": contracts.SCHEMA_VERSION,
        "stage": "review_manifest_agent",
        "lesson_id": None,
        "status": rule_review["status"],
        "decision": rule_review["decision"],
        "findings": list(rule_review.get("findings", [])),
        "blocking_issues": list(rule_review.get("blocking_issues", [])),
        "warnings": list(rule_review.get("warnings", [])),
    }
    review["findings"].insert(
        0,
        {
            "severity": "info",
            "message": f"AI manifest review fallback used: {exc}",
            "evidence_refs": [],
        },
    )
    return review


def execute_manifest_review(
    *,
    run_root: Path,
    gemini_bin: str = "gemini",
    gemini_model: str | None = None,
    gemini_extensions: list[str] | None = None,
    approval_mode: str = "yolo",
    debug_artifacts: bool = False,
    gemini_timeout_sec: int = 60,
) -> dict:
    manifest = render_support.read_json(run_root / "render" / "render_manifest.json")
    rule_review = build_rule_review(manifest)
    rule_review_path = run_root / "render" / "manifest_rule_review.json"
    contracts.write_json(rule_review_path, rule_review)

    review_path = run_root / "render" / "manifest_review.json"
    try:
        prompt = build_manifest_ai_review_prompt(manifest, rule_review)
        (run_root / "render" / "manifest_review.prompt.md").write_text(prompt, encoding="utf-8")
        ai_review, _ = gemini_pipeline.invoke_gemini_json(
            prompt=prompt,
            artifact_dir=run_root / "render",
            stem="manifest_review",
            gemini_bin=gemini_bin,
            gemini_model=gemini_model,
            gemini_extensions=gemini_extensions or ["stitch-skills"],
            approval_mode=approval_mode,
            debug_artifacts=debug_artifacts,
            timeout_sec=gemini_timeout_sec,
        )
        validate_review_result(ai_review)
        ai_review.setdefault("schema_version", contracts.SCHEMA_VERSION)
        ai_review["stage"] = "review_manifest_agent"
        review = ai_review
    except Exception as exc:
        review = build_manifest_ai_review_fallback(rule_review, exc)

    review_path = run_root / "render" / "manifest_review.json"
    contracts.write_json(review_path, review)
    return {
        "review_path": review_path,
        "warning_count": len(review.get("warnings", [])),
    }
