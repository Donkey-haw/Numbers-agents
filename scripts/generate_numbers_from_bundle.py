import argparse
import tempfile
from pathlib import Path

import build_runtime_config as runtime_config_builder
import generate_numbers_lesson as textbook


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", required=True, help="Path to unit_bundle JSON")
    parser.add_argument("--project-root", required=True, help="Project root path")
    parser.add_argument("--template-path", required=True, help="Numbers template path")
    parser.add_argument("--output-file", required=True, help="Output .numbers path")
    parser.add_argument("--footer", required=True, help="Footer text for generated cards")
    parser.add_argument("--config-output", help="Optional path to persist the generated runtime config")
    parser.add_argument("--review-output", help="Optional path to persist supplement review report JSON")
    parser.add_argument("--review-overrides", help="Optional JSON file that approves supplement candidate pages")
    parser.add_argument(
        "--include-needs-review-supplements",
        action="store_true",
        help="Keep supplement sources even when match_status is needs_review",
    )
    parser.add_argument(
        "--include-unmatched-supplements",
        action="store_true",
        help="Keep supplement sources even when match_status is not_found",
    )
    parser.add_argument("--keep-assets", action="store_true", help="Keep generated html/png assets")
    parser.add_argument("--skip-numbers", action="store_true", help="Skip Numbers insertion for debugging")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    bundle = runtime_config_builder.read_json(Path(args.bundle))
    review_overrides = (
        runtime_config_builder.load_review_overrides(Path(args.review_overrides))
        if args.review_overrides
        else {}
    )
    config, review_report = runtime_config_builder.build_runtime_config(
        bundle=bundle,
        project_root=args.project_root,
        template_path=args.template_path,
        output_file=args.output_file,
        footer=args.footer,
        review_overrides=review_overrides,
        include_needs_review_supplements=args.include_needs_review_supplements,
        include_unmatched_supplements=args.include_unmatched_supplements,
    )

    if args.config_output:
        config_path = Path(args.config_output).resolve()
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(runtime_config_builder.json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    else:
        tmp = tempfile.NamedTemporaryFile("w", suffix=".generated.json", delete=False, encoding="utf-8")
        try:
            tmp.write(runtime_config_builder.json.dumps(config, ensure_ascii=False, indent=2) + "\n")
            tmp.close()
            config_path = Path(tmp.name)
        except Exception:
            tmp.close()
            Path(tmp.name).unlink(missing_ok=True)
            raise

    if args.review_output:
        review_path = Path(args.review_output).resolve()
        review_path.parent.mkdir(parents=True, exist_ok=True)
        review_path.write_text(runtime_config_builder.json.dumps(review_report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    try:
        cli_args = argparse.Namespace(
            config=str(config_path),
            keep_assets=args.keep_assets,
            skip_numbers=args.skip_numbers,
        )
        textbook.main(cli_args)
    finally:
        if not args.config_output:
            config_path.unlink(missing_ok=True)

    print(config_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
