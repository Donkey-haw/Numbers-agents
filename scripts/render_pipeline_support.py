import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import generate_numbers_lesson as textbook  # noqa: E402


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_run_config(run_root: Path) -> dict:
    run_root = run_root.resolve()
    manifest = read_json(run_root / "run_manifest.json")
    config = textbook.load_config(Path(manifest["config_path"]))
    runtime_config = read_json(run_root / "source" / "runtime_config.json")
    config["sections"] = runtime_config["sections"]
    config["output_file"] = (run_root / "output" / Path(config["output_file"]).name).resolve()
    config["pages_dir"] = (run_root / "render" / "pages").resolve()
    config["cards_dir"] = (run_root / "render" / "cards").resolve()
    config["html_dir"] = (run_root / "render" / "html").resolve()
    return config


def serialize_jsonable(value):
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {key: serialize_jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [serialize_jsonable(item) for item in value]
    return value


def list_activity_plan_paths(run_root: Path) -> list[Path]:
    return sorted((run_root / "sections").glob("*/activity_plan.json"))
