import subprocess
import sys
from pathlib import Path


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]
    config_path = project_root / "configs" / "unit2.json"
    cmd = [
        sys.executable,
        str(project_root / "scripts" / "generate_numbers_lesson.py"),
        "--config",
        str(config_path),
        "--skip-numbers",
        "--keep-assets",
    ]
    print("Deprecated: use scripts/generate_numbers_lesson.py --config configs/unit2.json --skip-numbers --keep-assets")
    return subprocess.run(cmd).returncode


if __name__ == "__main__":
    raise SystemExit(main())
