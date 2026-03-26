import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import pipeline_contracts as contracts  # noqa: E402
import render_pipeline_support as render_support  # noqa: E402


def execute_manifest_review(*, run_root: Path) -> dict:
    manifest = render_support.read_json(run_root / "render" / "render_manifest.json")
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

    review = {
        "schema_version": contracts.SCHEMA_VERSION,
        "stage": "review_manifest_agent",
        "lesson_id": None,
        "status": status,
        "decision": decision,
        "findings": findings,
        "blocking_issues": blocking_issues,
        "warnings": warnings,
    }
    review_path = run_root / "render" / "manifest_review.json"
    contracts.write_json(review_path, review)
    return {
        "review_path": review_path,
        "warning_count": len(warnings),
    }
