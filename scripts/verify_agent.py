import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import generate_numbers_lesson as textbook  # noqa: E402
import pipeline_contracts as contracts  # noqa: E402
import render_pipeline_support as render_support  # noqa: E402


def execute_verify(*, run_root: Path, run_id: str) -> dict:
    config = render_support.load_run_config(run_root)
    status_path = run_root / "output" / "verify.status.json"
    status = {
        "schema_version": contracts.SCHEMA_VERSION,
        "stage": "verify_agent",
        "lesson_id": None,
        "status": "running",
        "run_id": run_id,
        "started_at": contracts.utc_now(),
        "finished_at": None,
        "input_refs": [str(config["output_file"])],
        "output_refs": [str(status_path)],
        "fallback_used": False,
        "warnings": [],
        "errors": [],
    }
    contracts.write_json(status_path, status)
    textbook.verify_output(config)
    status["status"] = "succeeded"
    status["finished_at"] = contracts.utc_now()
    contracts.write_json(status_path, status)
    return {
        "output_file": config["output_file"],
        "warning_count": 0,
    }
