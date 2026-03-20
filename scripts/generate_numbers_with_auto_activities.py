import argparse
import json
import sys
import tempfile
from pathlib import Path

import fitz


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import generate_activity_plan as activity_plan_builder  # noqa: E402
import generate_lesson_analysis as lesson_analysis_builder  # noqa: E402
import generate_numbers_lesson as textbook  # noqa: E402
import generate_numbers_with_activities as activity_pipeline  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to textbook config JSON")
    parser.add_argument("--analysis-dir", help="Directory to persist lesson_analysis JSON files")
    parser.add_argument("--plan-dir", help="Directory to persist activity_plan JSON files")
    parser.add_argument("--manifest-output", help="Optional render manifest output path")
    parser.add_argument("--keep-assets", action="store_true", help="Keep generated html/png assets")
    parser.add_argument(
        "--include-status",
        nargs="*",
        default=["draft", "reviewed", "approved"],
        help="review_status values to render from generated activity plans",
    )
    return parser.parse_args()


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_generated_content(config_path: Path, analysis_dir: Path, plan_dir: Path) -> list[Path]:
    config = textbook.load_config(config_path)
    textbook.infer_section_pages(config)

    activity_plan_paths: list[Path] = []
    doc = fitz.open(config["pdf_path"])
    try:
        for section in config["sections"]:
            analysis = lesson_analysis_builder.build_analysis(doc, section)
            analysis_path = analysis_dir / f"{section['card_file']}.lesson_analysis.json"
            write_json(analysis_path, analysis)

            plan = activity_plan_builder.build_activity_plan(analysis)
            plan_path = plan_dir / f"{section['card_file']}.activity_plan.json"
            write_json(plan_path, plan)
            activity_plan_paths.append(plan_path)
    finally:
        doc.close()

    return activity_plan_paths


def main() -> int:
    args = parse_args()
    config_path = Path(args.config)

    with tempfile.TemporaryDirectory(prefix="numbersauto_analysis_") as analysis_tmp, tempfile.TemporaryDirectory(
        prefix="numbersauto_plans_"
    ) as plan_tmp:
        analysis_dir = Path(args.analysis_dir) if args.analysis_dir else Path(analysis_tmp)
        plan_dir = Path(args.plan_dir) if args.plan_dir else Path(plan_tmp)
        activity_plan_paths = build_generated_content(config_path, analysis_dir, plan_dir)

        pipeline_args = argparse.Namespace(
            config=str(config_path),
            activity_plan=[str(path) for path in activity_plan_paths],
            manifest_output=args.manifest_output,
            keep_assets=args.keep_assets,
            include_status=args.include_status,
        )
        activity_pipeline.main(pipeline_args)

        if args.analysis_dir:
            print(analysis_dir)
        if args.plan_dir:
            print(plan_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
