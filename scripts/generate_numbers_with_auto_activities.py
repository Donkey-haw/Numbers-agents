import argparse
import json
import shutil
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
import run_gemini_cli_pipeline as gemini_pipeline  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to textbook config JSON")
    parser.add_argument("--analysis-dir", help="Directory to persist lesson_analysis JSON files")
    parser.add_argument("--plan-dir", help="Directory to persist activity_plan JSON files")
    parser.add_argument("--manifest-output", help="Optional render manifest output path")
    parser.add_argument("--keep-assets", action="store_true", help="Keep generated html/png assets")
    parser.add_argument("--local-only", action="store_true", help="Use local heuristic generators instead of Gemini CLI")
    parser.add_argument("--gemini-bin", default="gemini", help="Gemini CLI binary path")
    parser.add_argument("--gemini-model", help="Gemini model name")
    parser.add_argument(
        "--gemini-extensions",
        nargs="*",
        default=["stitch-skills"],
        help="Gemini extensions to enable for headless runs",
    )
    parser.add_argument("--gemini-timeout-sec", type=int, default=90, help="Timeout for each Gemini CLI call")
    parser.add_argument("--max-workers", type=int, default=2, help="Max concurrent lesson workers for Gemini stages")
    parser.add_argument("--debug-artifacts", action="store_true", help="Keep Gemini prompt/raw/wrapper debug artifacts")
    parser.add_argument("--output-root", help="Artifact root directory for Gemini pipeline")
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


def gemini_available(binary: str) -> bool:
    return shutil.which(binary) is not None


def copy_gemini_outputs(artifact_root: Path, analysis_dir: Path | None, plan_dir: Path | None) -> None:
    if analysis_dir:
        analysis_dir.mkdir(parents=True, exist_ok=True)
    if plan_dir:
        plan_dir.mkdir(parents=True, exist_ok=True)

    for lesson_dir in sorted((artifact_root / "sections").glob("*")):
        if not lesson_dir.is_dir():
            continue
        if analysis_dir:
            source = lesson_dir / "lesson_analysis.json"
            if source.exists():
                shutil.copy2(source, analysis_dir / source.name)
        if plan_dir:
            source = lesson_dir / "activity_plan.json"
            if source.exists():
                shutil.copy2(source, plan_dir / source.name)


def run_gemini_generation(args: argparse.Namespace, config_path: Path) -> int:
    gemini_args = argparse.Namespace(
        config=str(config_path),
        pdf=None,
        chart=None,
        gemini_bin=args.gemini_bin,
        gemini_model=args.gemini_model,
        gemini_extensions=args.gemini_extensions,
        gemini_timeout_sec=args.gemini_timeout_sec,
        output_root=args.output_root,
        approval_mode="yolo",
        max_workers=args.max_workers,
        keep_artifacts=args.keep_assets,
        debug_artifacts=args.debug_artifacts,
        dry_run=False,
        include_status=args.include_status,
        textbook_only_fallback=False,
    )
    exit_code = gemini_pipeline.main_with_args(gemini_args)
    artifact_root = Path(gemini_args.output_root) if gemini_args.output_root else gemini_pipeline.LAST_ARTIFACT_ROOT
    if artifact_root is not None:
        copy_gemini_outputs(
            artifact_root,
            Path(args.analysis_dir) if args.analysis_dir else None,
            Path(args.plan_dir) if args.plan_dir else None,
        )
    return exit_code


def main() -> int:
    args = parse_args()
    config_path = Path(args.config)

    if not args.local_only and gemini_available(args.gemini_bin):
        return run_gemini_generation(args, config_path)

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
