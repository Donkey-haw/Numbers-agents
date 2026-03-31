import asyncio
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import generate_numbers_lesson as textbook  # noqa: E402
import generate_numbers_with_activities as numbers_with_activities  # noqa: E402
import pipeline_contracts as contracts  # noqa: E402
import render_pipeline_support as render_support  # noqa: E402


def build_status(run_id: str, started_at: str, input_refs: list[str], output_refs: list[str]) -> dict:
    return {
        "schema_version": contracts.SCHEMA_VERSION,
        "stage": "capture_agent",
        "lesson_id": None,
        "status": "running",
        "run_id": run_id,
        "started_at": started_at,
        "finished_at": None,
        "input_refs": input_refs,
        "output_refs": output_refs,
        "fallback_used": False,
        "warnings": [],
        "errors": [],
    }


def execute_capture(*, run_root: Path, run_id: str) -> dict:
    config = render_support.load_run_config(run_root)
    started_at = contracts.utc_now()
    html_manifest_path = run_root / "render" / "html_manifest.json"
    render_manifest_path = run_root / "render" / "render_manifest.json"
    status_path = run_root / "render" / "capture.status.json"
    plan_paths = render_support.list_activity_plan_paths(run_root)

    status = build_status(
        run_id=run_id,
        started_at=started_at,
        input_refs=[str(html_manifest_path)] + [str(path) for path in plan_paths],
        output_refs=[str(render_manifest_path)],
    )
    contracts.write_json(status_path, status)
    try:
        textbook_card_assets = asyncio.run(textbook.capture_cards(config))
        plans = [(path, numbers_with_activities.load_activity_plan(path)) for path in plan_paths]
        activity_html_pairs = numbers_with_activities.render_activity_html_files(plans, config, {"approved", "draft"})
        activity_assets = asyncio.run(numbers_with_activities.capture_html_files(activity_html_pairs, config))
        manifest = numbers_with_activities.build_manifest(config, textbook_card_assets, activity_assets)
        render_manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        status["status"] = "succeeded"
        status["finished_at"] = contracts.utc_now()
        contracts.write_json(status_path, status)
        return {
            "render_manifest_path": render_manifest_path,
            "asset_count": len(manifest["assets"]),
            "warning_count": 0,
        }
    except Exception as exc:
        status["status"] = "failed"
        status["finished_at"] = contracts.utc_now()
        status["errors"] = [str(exc)]
        contracts.write_json(status_path, status)
        raise
