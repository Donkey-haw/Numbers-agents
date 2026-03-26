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
        "stage": "numbers_compose_agent",
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


def execute_numbers_compose(*, run_root: Path, run_id: str) -> dict:
    config = render_support.load_run_config(run_root)
    textbook.ensure_dirs(config)
    textbook.copy_template(config)

    manifest_path = run_root / "render" / "render_manifest.json"
    status_path = run_root / "output" / "numbers_compose.status.json"
    status = build_status(
        run_id=run_id,
        started_at=contracts.utc_now(),
        input_refs=[str(manifest_path)],
        output_refs=[str(config["output_file"])],
    )
    contracts.write_json(status_path, status)

    manifest = render_support.read_json(manifest_path)
    inserted_sheets = numbers_with_activities.insert_manifest_into_numbers(config, manifest)
    numbers_with_activities.verify_manifest_output(config, inserted_sheets)

    status["status"] = "succeeded"
    status["finished_at"] = contracts.utc_now()
    contracts.write_json(status_path, status)
    return {
        "output_file": config["output_file"],
        "sheet_names": inserted_sheets,
        "warning_count": 0,
    }
