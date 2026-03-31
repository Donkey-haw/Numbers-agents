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


def execute_html_rendering_for_lesson(*, run_root: Path, run_id: str, section_key: str) -> dict:
    """Render HTML cards for a single lesson (used by lesson-level DAG scheduler)."""
    import json as _json

    config = render_support.load_run_config(run_root)
    textbook.ensure_dirs(config)
    textbook.infer_section_pages(config)

    # Find the target section
    target_section = None
    for section in config["sections"]:
        if contracts.section_artifact_stem(section) == section_key:
            target_section = section
            break

    if target_section is None:
        raise ValueError(f"Section not found for key: {section_key}")

    started_at = contracts.utc_now()
    lesson_dir = run_root / "sections" / section_key
    status_path = lesson_dir / "html_card.status.json"
    html_manifest_path = lesson_dir / "html_manifest.json"

    status = build_status(
        run_id=run_id,
        started_at=started_at,
        input_refs=[str(lesson_dir / "activity_plan.json")],
        output_refs=[str(html_manifest_path)],
    )
    status["lesson_id"] = target_section.get("sheet_name")
    contracts.write_json(status_path, status)

    warning_count = 0

    # Extract textbook pages for this section only
    try:
        textbook_page_assets = textbook.extract_pages_for_section(config, target_section)
    except AttributeError:
        # Fallback: extract all pages if per-section method not available
        textbook_page_assets = textbook.extract_pages(config)

    # Render textbook source cards for this section
    textbook_html_paths = []
    for source_card in textbook.section_source_cards(target_section, config):
        html_path = config["html_dir"] / f"{source_card['card_stem']}.html"
        html_path.write_text(textbook.render_html(source_card, config), encoding="utf-8")
        textbook_html_paths.append(html_path)

    # Render activity HTML for this section
    plan_path = lesson_dir / "activity_plan.json"
    activity_html_pairs = []
    if plan_path.exists():
        plan = numbers_with_activities.load_activity_plan(plan_path)
        activity_html_pairs = numbers_with_activities.render_activity_html_files(
            [(plan_path, plan)], config, {"approved", "draft"}
        )

    html_manifest = {
        "schema_version": contracts.SCHEMA_VERSION,
        "run_id": run_id,
        "section_key": section_key,
        "generated_at": contracts.utc_now(),
        "textbook_page_assets": [str(p) for p in textbook_page_assets] if isinstance(textbook_page_assets, list) else [],
        "textbook_html_paths": [str(p) for p in textbook_html_paths],
        "activity_html_paths": [str(hp) for _, hp, _ in activity_html_pairs],
        "activity_plan_paths": [str(plan_path)] if plan_path.exists() else [],
    }
    contracts.write_json(html_manifest_path, html_manifest)

    status["status"] = "succeeded"
    status["finished_at"] = contracts.utc_now()
    contracts.write_json(status_path, status)

    return {
        "html_manifest_path": html_manifest_path,
        "section_key": section_key,
        "lesson_id": target_section.get("sheet_name"),
        "warning_count": warning_count,
    }

