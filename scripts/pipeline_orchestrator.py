import argparse
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import activity_plan_agent  # noqa: E402
import capture_agent  # noqa: E402
import generate_numbers_lesson as textbook  # noqa: E402
import html_card_agent  # noqa: E402
import lesson_analysis_agent  # noqa: E402
import numbers_compose_agent  # noqa: E402
import pipeline_contracts as contracts  # noqa: E402
import review_manifest_agent  # noqa: E402
import source_parse_agent  # noqa: E402
import verify_agent  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to textbook config JSON")
    parser.add_argument(
        "--workflow-mode",
        default="stable",
        choices=sorted(contracts.WORKFLOW_MODES),
        help="Agent workflow mode",
    )
    parser.add_argument("--run-root", help="Optional explicit run root directory")
    parser.add_argument("--gemini-bin", default="gemini", help="Gemini CLI binary path")
    parser.add_argument("--gemini-model", help="Gemini model name")
    parser.add_argument("--gemini-extensions", nargs="*", default=["stitch-skills"], help="Gemini extensions")
    parser.add_argument("--approval-mode", default="yolo", help="Gemini approval mode")
    parser.add_argument("--debug-artifacts", action="store_true", help="Keep Gemini prompt/raw artifacts")
    parser.add_argument("--gemini-timeout-sec", type=int, default=60, help="Timeout for each Gemini CLI call")
    parser.add_argument("--max-workers", type=int, default=2, help="Max parallel Gemini lesson/activity workers")
    parser.add_argument(
        "--stop-after",
        choices=contracts.DEFAULT_STAGE_ORDER,
        help="Stop after completing the specified stage",
    )
    parser.add_argument("--dry-run", action="store_true", help="Create run root and run_manifest only")
    return parser.parse_args()


def detect_selected_unit(config: dict) -> str | None:
    output_file = config.get("output_file")
    if output_file:
        return Path(output_file).stem
    return None


def detect_selected_lessons(config: dict) -> list[str]:
    sections = config.get("sections", [])
    return [section.get("sheet_name", section.get("title", "")) for section in sections]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def update_run_manifest_for_stage(run_root: Path, stage: str, status: str, fallback_used: bool = False, warning_count: int = 0, error_count: int = 0) -> None:
    manifest_path = run_root / "run_manifest.json"
    manifest = load_json(manifest_path)
    for item in manifest["status_summary"]:
        if item["stage"] == stage:
            item["status"] = status
            item["fallback_used"] = fallback_used
            item["warning_count"] = warning_count
            item["error_count"] = error_count
            break
    contracts.write_json(manifest_path, manifest)


def finalize_run_manifest(run_root: Path, final_status: str, final_output_file: str | None = None) -> None:
    manifest_path = run_root / "run_manifest.json"
    manifest = load_json(manifest_path)
    manifest["finished_at"] = contracts.utc_now()
    manifest["final_status"] = final_status
    manifest["final_output_file"] = final_output_file
    contracts.write_json(manifest_path, manifest)


def main() -> int:
    args = parse_args()
    config_path = Path(args.config).resolve()
    config = textbook.load_config(config_path)

    if args.run_root:
        run_root = Path(args.run_root).resolve()
        run_root.mkdir(parents=True, exist_ok=True)
        for name in ("source", "sections", "render", "output"):
            (run_root / name).mkdir(parents=True, exist_ok=True)
        run_id = run_root.name
    else:
        run_id = contracts.build_run_id(config_path.stem)
        run_root = contracts.build_run_root(PROJECT_ROOT, run_id)

    manifest = contracts.build_run_manifest(
        run_id=run_id,
        workflow_mode=args.workflow_mode,
        config_path=config_path,
        selected_unit=detect_selected_unit(config),
        selected_lessons=detect_selected_lessons(config),
    )
    contracts.write_json(run_root / "run_manifest.json", manifest)

    source_status = {
        "schema_version": contracts.SCHEMA_VERSION,
        "stage": "source_parse_agent",
        "lesson_id": None,
        "status": "pending",
        "run_id": run_id,
        "started_at": manifest["started_at"],
        "finished_at": None,
        "input_refs": [str(config_path)],
        "output_refs": [
            str(run_root / "source" / "schedule_draft.json"),
            str(run_root / "source" / "textbook_context.json"),
            str(run_root / "source" / "runtime_config.json"),
            str(run_root / "source" / "config_quality_review.json"),
            str(run_root / "source" / "boundary_review.json"),
            str(run_root / "source" / "supplement_review.json"),
        ],
        "fallback_used": False,
        "warnings": [],
        "errors": [],
    }
    contracts.write_json(run_root / "source" / "source_parse.status.json", source_status)

    print(run_root)
    if args.dry_run:
        return 0
    try:
        update_run_manifest_for_stage(run_root, "source_parse_agent", "running")
        source_result = source_parse_agent.execute_source_parse(
            config_path=config_path,
            run_root=run_root,
            run_id=run_id,
            chart_path=None,
        )
        source_stage_status = "succeeded"
        if source_result["blocked_count"]:
            source_stage_status = "blocked"
        elif source_result["warning_count"]:
            source_stage_status = "succeeded_with_warning"
        update_run_manifest_for_stage(
            run_root,
            "source_parse_agent",
            source_stage_status,
            warning_count=source_result["warning_count"],
            error_count=source_result["blocked_count"],
        )
        if source_result["blocked_count"]:
            finalize_run_manifest(run_root, "failed")
            return 1
        if args.stop_after == "source_parse_agent":
            finalize_run_manifest(run_root, "success")
            return 0
    except Exception:
        update_run_manifest_for_stage(run_root, "source_parse_agent", "failed", error_count=1)
        finalize_run_manifest(run_root, "failed")
        raise
    try:
        update_run_manifest_for_stage(run_root, "lesson_analysis_agent", "running")
        lesson_result = lesson_analysis_agent.execute_lesson_analysis(
            run_root=run_root,
            run_id=run_id,
            gemini_bin=args.gemini_bin,
            gemini_model=args.gemini_model,
            gemini_extensions=args.gemini_extensions,
            approval_mode=args.approval_mode,
            debug_artifacts=args.debug_artifacts,
            gemini_timeout_sec=args.gemini_timeout_sec,
            max_workers=args.max_workers,
        )
        lesson_stage_status = "succeeded"
        if lesson_result["fallback_count"]:
            lesson_stage_status = "failed_fallback_used"
        elif lesson_result["warning_count"]:
            lesson_stage_status = "succeeded_with_warning"
        update_run_manifest_for_stage(
            run_root,
            "lesson_analysis_agent",
            lesson_stage_status,
            fallback_used=lesson_result["fallback_count"] > 0,
            warning_count=lesson_result["warning_count"],
            error_count=lesson_result["fallback_count"],
        )
        review_status = "succeeded" if lesson_result["warning_count"] == 0 else "succeeded_with_warning"
        update_run_manifest_for_stage(
            run_root,
            "review_lesson_agent",
            review_status,
            warning_count=lesson_result["warning_count"],
        )
        if args.stop_after == "lesson_analysis_agent" or args.stop_after == "review_lesson_agent":
            finalize_run_manifest(run_root, "success")
            return 0
    except Exception:
        update_run_manifest_for_stage(run_root, "lesson_analysis_agent", "failed", error_count=1)
        finalize_run_manifest(run_root, "failed")
        raise
    try:
        update_run_manifest_for_stage(run_root, "activity_plan_agent", "running")
        activity_result = activity_plan_agent.execute_activity_planning(
            run_root=run_root,
            run_id=run_id,
            gemini_bin=args.gemini_bin,
            gemini_model=args.gemini_model,
            gemini_extensions=args.gemini_extensions,
            approval_mode=args.approval_mode,
            debug_artifacts=args.debug_artifacts,
            gemini_timeout_sec=args.gemini_timeout_sec,
            max_workers=args.max_workers,
        )
        activity_stage_status = "succeeded"
        if activity_result["fallback_count"]:
            activity_stage_status = "failed_fallback_used"
        elif activity_result["warning_count"]:
            activity_stage_status = "succeeded_with_warning"
        update_run_manifest_for_stage(
            run_root,
            "activity_plan_agent",
            activity_stage_status,
            fallback_used=activity_result["fallback_count"] > 0,
            warning_count=activity_result["warning_count"],
            error_count=activity_result["fallback_count"],
        )
        review_status = "succeeded" if activity_result["warning_count"] == 0 else "succeeded_with_warning"
        update_run_manifest_for_stage(
            run_root,
            "review_activity_agent",
            review_status,
            warning_count=activity_result["warning_count"],
        )
        if args.stop_after == "activity_plan_agent" or args.stop_after == "review_activity_agent":
            finalize_run_manifest(run_root, "success")
            return 0
    except Exception:
        update_run_manifest_for_stage(run_root, "activity_plan_agent", "failed", error_count=1)
        finalize_run_manifest(run_root, "failed")
        raise
    try:
        update_run_manifest_for_stage(run_root, "html_card_agent", "running")
        html_result = html_card_agent.execute_html_rendering(
            run_root=run_root,
            run_id=run_id,
        )
        html_status = "succeeded" if html_result["warning_count"] == 0 else "succeeded_with_warning"
        update_run_manifest_for_stage(
            run_root,
            "html_card_agent",
            html_status,
            warning_count=html_result["warning_count"],
        )
        if args.stop_after == "html_card_agent":
            finalize_run_manifest(run_root, "success")
            return 0
    except Exception:
        update_run_manifest_for_stage(run_root, "html_card_agent", "failed", error_count=1)
        finalize_run_manifest(run_root, "failed")
        raise
    try:
        update_run_manifest_for_stage(run_root, "capture_agent", "running")
        capture_result = capture_agent.execute_capture(
            run_root=run_root,
            run_id=run_id,
        )
        capture_status = "succeeded" if capture_result["warning_count"] == 0 else "succeeded_with_warning"
        update_run_manifest_for_stage(
            run_root,
            "capture_agent",
            capture_status,
            warning_count=capture_result["warning_count"],
        )
        if args.stop_after == "capture_agent":
            finalize_run_manifest(run_root, "success")
            return 0
    except Exception:
        update_run_manifest_for_stage(run_root, "capture_agent", "failed", error_count=1)
        finalize_run_manifest(run_root, "failed")
        raise
    try:
        update_run_manifest_for_stage(run_root, "numbers_compose_agent", "running")
        compose_result = numbers_compose_agent.execute_numbers_compose(
            run_root=run_root,
            run_id=run_id,
        )
        compose_status = "succeeded" if compose_result["warning_count"] == 0 else "succeeded_with_warning"
        update_run_manifest_for_stage(
            run_root,
            "numbers_compose_agent",
            compose_status,
            warning_count=compose_result["warning_count"],
        )
        if args.stop_after == "numbers_compose_agent":
            finalize_run_manifest(run_root, "success", str(compose_result["output_file"]))
            return 0
    except Exception:
        update_run_manifest_for_stage(run_root, "numbers_compose_agent", "failed", error_count=1)
        finalize_run_manifest(run_root, "failed")
        raise
    try:
        review_result = review_manifest_agent.execute_manifest_review(run_root=run_root)
        review_status = "succeeded" if review_result["warning_count"] == 0 else "succeeded_with_warning"
        update_run_manifest_for_stage(
            run_root,
            "review_manifest_agent",
            review_status,
            warning_count=review_result["warning_count"],
        )
        if args.stop_after == "review_manifest_agent":
            finalize_run_manifest(run_root, "success", str(compose_result["output_file"]))
            return 0
    except Exception:
        update_run_manifest_for_stage(run_root, "review_manifest_agent", "failed", error_count=1)
        finalize_run_manifest(run_root, "failed")
        raise
    try:
        verify_result = verify_agent.execute_verify(
            run_root=run_root,
            run_id=run_id,
        )
        update_run_manifest_for_stage(run_root, "verify_agent", "succeeded")
        finalize_run_manifest(run_root, "success", str(verify_result["output_file"]))
        return 0
    except Exception:
        update_run_manifest_for_stage(run_root, "verify_agent", "failed", error_count=1)
        finalize_run_manifest(run_root, "failed")
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
