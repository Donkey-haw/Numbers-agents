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
        "stage": "html_card_agent",
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


def execute_html_rendering(*, run_root: Path, run_id: str) -> dict:
    config = render_support.load_run_config(run_root)
    textbook.ensure_dirs(config)
    textbook.infer_section_pages(config)

    started_at = contracts.utc_now()
    status_path = run_root / "render" / "html_card.status.json"
    rendered_runtime_config_path = run_root / "render" / "runtime_config.json"
    html_manifest_path = run_root / "render" / "html_manifest.json"

    plan_paths = render_support.list_activity_plan_paths(run_root)
    status = build_status(
        run_id=run_id,
        started_at=started_at,
        input_refs=[str(path) for path in plan_paths] + [str(run_root / "source" / "runtime_config.json")],
        output_refs=[str(rendered_runtime_config_path), str(html_manifest_path)],
    )
    contracts.write_json(status_path, status)

    textbook_page_assets = textbook.extract_pages(config)
    textbook_html_paths = textbook.generated_html_paths(config)
    for section in config["sections"]:
        for source_card in textbook.section_source_cards(section, config):
            html_path = config["html_dir"] / f"{source_card['card_stem']}.html"
            html_path.write_text(textbook.render_html(source_card, config), encoding="utf-8")

    plans = [(path, numbers_with_activities.load_activity_plan(path)) for path in plan_paths]
    activity_html_pairs = numbers_with_activities.render_activity_html_files(plans, config, {"approved", "draft"})

    html_manifest = {
        "schema_version": contracts.SCHEMA_VERSION,
        "run_id": run_id,
        "generated_at": contracts.utc_now(),
        "textbook_page_assets": [str(path) for path in textbook_page_assets],
        "textbook_html_paths": [str(path) for path in textbook_html_paths],
        "activity_html_paths": [str(html_path) for _, html_path, _ in activity_html_pairs],
        "activity_plan_paths": [str(path) for path in plan_paths],
    }
    contracts.write_json(rendered_runtime_config_path, render_support.serialize_jsonable(config))
    contracts.write_json(html_manifest_path, html_manifest)

    status["status"] = "succeeded"
    status["finished_at"] = contracts.utc_now()
    contracts.write_json(status_path, status)
    return {
        "runtime_config_path": rendered_runtime_config_path,
        "html_manifest_path": html_manifest_path,
        "warning_count": 0,
    }
