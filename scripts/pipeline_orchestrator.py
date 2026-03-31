import argparse
import json
import shutil
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import activity_plan_agent  # noqa: E402
import activity_review_agent  # noqa: E402
import capture_agent  # noqa: E402
import generate_numbers_lesson as textbook  # noqa: E402
import html_card_agent  # noqa: E402
import lesson_analysis_agent  # noqa: E402
import lesson_review_agent  # noqa: E402
import numbers_compose_agent  # noqa: E402
import orchestrator_events  # noqa: E402
import pipeline_contracts as contracts  # noqa: E402
import review_manifest_agent  # noqa: E402
import runtime_driven_agents  # noqa: E402
import run_gemini_cli_pipeline as gemini_pipeline  # noqa: E402
import source_boundary_agent  # noqa: E402
import source_validation_agent  # noqa: E402
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
    parser.add_argument("--gemini-timeout-sec", type=int, default=0, help="Timeout for each Gemini CLI call. Use 0 to disable.")
    parser.add_argument("--gemini-idle-timeout-sec", type=int, default=180, help="Idle timeout for each Gemini CLI call. Use 0 to disable.")
    parser.add_argument("--lesson-gemini-timeout-sec", type=int, help="Override Gemini timeout for lesson_analysis_agent. Use 0 to disable.")
    parser.add_argument("--activity-gemini-timeout-sec", type=int, help="Override Gemini timeout for activity_plan_agent. Use 0 to disable.")
    parser.add_argument("--lesson-gemini-idle-timeout-sec", type=int, help="Override Gemini idle timeout for lesson_analysis_agent. Use 0 to disable.")
    parser.add_argument("--activity-gemini-idle-timeout-sec", type=int, help="Override Gemini idle timeout for activity_plan_agent. Use 0 to disable.")
    parser.add_argument(
        "--max-workers",
        type=int,
        help="Override parallel lesson/activity workers. Default is the number of config sections.",
    )
    parser.add_argument("--lesson-max-workers", type=int, help="Override parallel workers for lesson_analysis_agent")
    parser.add_argument("--activity-max-workers", type=int, help="Override parallel workers for activity_plan/review agents")
    parser.add_argument(
        "--keep-run-artifacts",
        action="store_true",
        help="Preserve artifacts/runs/<run_id> even after a successful full run",
    )
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


def is_manual_page_map_config(config: dict) -> bool:
    sections = config.get("sections", [])
    if not sections:
        return False
    return all(section.get("pdf_pages") for section in sections)


def manual_stage_order() -> list[str]:
    return [
        "lesson_analysis_agent",
        "lesson_review_agent",
        "activity_plan_agent",
        "activity_review_agent",
        "html_card_agent",
        "capture_agent",
        "numbers_compose_agent",
        "review_manifest_agent",
        "verify_agent",
    ]


def serialize_jsonable(value):
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {key: serialize_jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [serialize_jsonable(item) for item in value]
    return value


def prepare_manual_source_artifacts(*, config: dict, run_root: Path) -> None:
    source_dir = run_root / "source"
    runtime_config = json.loads(json.dumps(serialize_jsonable(config), ensure_ascii=False))
    for section in runtime_config.get("sections", []):
        section.setdefault("lesson_id", contracts.section_artifact_stem(section))
    textbook.infer_section_pages(runtime_config)
    runtime_config.pop("resources_by_id", None)
    contracts.write_json(source_dir / "runtime_config.json", runtime_config)
    runtime_config_for_context = textbook.load_config(run_root / "source" / "runtime_config.json")
    schedule_draft = gemini_pipeline.build_schedule_draft(runtime_config_for_context, chart_path=None)
    contracts.write_json(source_dir / "schedule_draft.json", schedule_draft)
    gemini_pipeline.build_textbook_context(runtime_config_for_context, source_dir)


def build_document_inventory_inputs(config: dict, config_path: Path) -> list[dict]:
    documents = [
        {
            "document_id": "config",
            "path": str(config_path),
            "kind": "reference",
            "label": config_path.stem,
        }
    ]

    seen_paths = {str(config_path.resolve())}

    for resource in config.get("resources", []):
        resource_path = Path(resource["pdf_path"]).resolve()
        resource_path_str = str(resource_path)
        if resource_path_str in seen_paths:
            continue
        seen_paths.add(resource_path_str)
        documents.append(
            {
                "document_id": resource.get("resource_id"),
                "path": resource_path_str,
                "kind": resource.get("kind", "textbook"),
                "label": resource.get("label", resource.get("resource_id", resource_path.stem)),
            }
        )

    chart_path = config.get("chart_path")
    if chart_path:
        resolved_chart_path = Path(chart_path).resolve()
        resolved_chart_path_str = str(resolved_chart_path)
        if resolved_chart_path_str not in seen_paths:
            documents.append(
                {
                    "document_id": "schedule_chart",
                    "path": resolved_chart_path_str,
                    "kind": "schedule_chart",
                    "label": resolved_chart_path.stem,
                }
            )

    return documents


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def section_count(config: dict) -> int:
    return max(1, len(config.get("sections", [])))


def lesson_worker_count(args: argparse.Namespace, config: dict) -> int:
    if args.lesson_max_workers is not None:
        return max(1, args.lesson_max_workers)
    if args.max_workers is not None:
        return max(1, args.max_workers)
    return section_count(config)


def activity_worker_count(args: argparse.Namespace, config: dict) -> int:
    if args.activity_max_workers is not None:
        return max(1, args.activity_max_workers)
    if args.max_workers is not None:
        return max(1, args.max_workers)
    return section_count(config)


def gemini_timeout_sec(args: argparse.Namespace) -> int | None:
    return normalize_timeout_arg(args.gemini_timeout_sec)


def gemini_idle_timeout_sec(args: argparse.Namespace) -> int | None:
    return normalize_timeout_arg(args.gemini_idle_timeout_sec)


def normalize_timeout_arg(value: int | None, fallback: int | None = None) -> int | None:
    selected = value if value is not None else fallback
    if selected is None or selected == 0:
        return None
    return max(1, selected)


def lesson_gemini_timeout_sec(args: argparse.Namespace) -> int | None:
    return normalize_timeout_arg(args.lesson_gemini_timeout_sec, args.gemini_timeout_sec)


def activity_gemini_timeout_sec(args: argparse.Namespace) -> int | None:
    return normalize_timeout_arg(args.activity_gemini_timeout_sec, args.gemini_timeout_sec)


def lesson_gemini_idle_timeout_sec(args: argparse.Namespace) -> int | None:
    return normalize_timeout_arg(args.lesson_gemini_idle_timeout_sec, args.gemini_idle_timeout_sec)


def activity_gemini_idle_timeout_sec(args: argparse.Namespace) -> int | None:
    return normalize_timeout_arg(args.activity_gemini_idle_timeout_sec, args.gemini_idle_timeout_sec)


def stage_status_from_counts(*, warning_count: int = 0, blocked_count: int = 0) -> str:
    if blocked_count:
        return "blocked"
    if warning_count:
        return "succeeded_with_warning"
    return "succeeded"


def update_run_manifest_for_stage(
    run_root: Path,
    stage: str,
    status: str,
    fallback_used: bool = False,
    warning_count: int = 0,
    error_count: int = 0,
    details: dict | None = None,
) -> None:
    manifest_path = run_root / "run_manifest.json"
    manifest = load_json(manifest_path)
    previous_status = None
    for item in manifest["status_summary"]:
        if item["stage"] == stage:
            previous_status = item["status"]
            item["status"] = status
            item["fallback_used"] = fallback_used
            item["warning_count"] = warning_count
            item["error_count"] = error_count
            item["details"] = details or {}
            break
    contracts.write_json(manifest_path, manifest)
    if previous_status != status:
        event_type = "stage_started" if status == "running" else "stage_finished"
        orchestrator_events.append_event(
            run_root=run_root,
            run_id=manifest["run_id"],
            event_type=event_type,
            stage=stage,
            status=status,
            payload={
                "previous_status": previous_status,
                "fallback_used": fallback_used,
                "warning_count": warning_count,
                "error_count": error_count,
                "details": details or {},
            },
        )


def finalize_run_manifest(run_root: Path, final_status: str, final_output_file: str | None = None) -> None:
    manifest_path = run_root / "run_manifest.json"
    manifest = load_json(manifest_path)
    manifest["finished_at"] = contracts.utc_now()
    manifest["final_status"] = final_status
    manifest["final_output_file"] = final_output_file
    contracts.write_json(manifest_path, manifest)
    orchestrator_events.append_event(
        run_root=run_root,
        run_id=manifest["run_id"],
        event_type="run_finished",
        status=final_status,
        payload={
            "final_output_file": final_output_file,
        },
    )


def write_generation_diagnostics(run_root: Path) -> None:
    manifest = load_json(run_root / "run_manifest.json")
    summary = {item["stage"]: item for item in manifest.get("status_summary", [])}
    payload = {
        "schema_version": contracts.SCHEMA_VERSION,
        "run_id": manifest["run_id"],
        "updated_at": contracts.utc_now(),
        "stages": {
            stage: {
                "status": summary.get(stage, {}).get("status"),
                "fallback_used": summary.get(stage, {}).get("fallback_used", False),
                "warning_count": summary.get(stage, {}).get("warning_count", 0),
                "error_count": summary.get(stage, {}).get("error_count", 0),
                "details": summary.get(stage, {}).get("details", {}),
            }
            for stage in ("lesson_analysis_agent", "activity_plan_agent")
        },
    }
    contracts.write_json(run_root / "output" / "generation_diagnostics.json", payload)


def write_job_manifest(run_root: Path) -> None:
    sections_root = run_root / "sections"
    jobs = []
    if sections_root.exists():
        for status_path in sorted(sections_root.glob("*/*.worker.status.json")):
            jobs.append(load_json(status_path))

    manifest = {
        "schema_version": contracts.SCHEMA_VERSION,
        "run_id": run_root.name,
        "updated_at": contracts.utc_now(),
        "jobs": jobs,
    }
    contracts.write_json(run_root / "job_manifest.json", manifest)


def should_keep_run_artifacts(args: argparse.Namespace, final_status: str) -> bool:
    if final_status != "success":
        return True
    if args.keep_run_artifacts:
        return True
    if args.debug_artifacts:
        return True
    if args.stop_after:
        return True
    if args.run_root:
        return True
    return False


def promote_final_output_and_cleanup(*, run_root: Path, produced_output: Path, configured_output: Path) -> None:
    configured_output.parent.mkdir(parents=True, exist_ok=True)
    if configured_output.exists():
        configured_output.unlink()
    shutil.copy2(produced_output, configured_output)
    shutil.rmtree(run_root)


def promote_final_output_only(*, produced_output: Path, configured_output: Path) -> None:
    configured_output.parent.mkdir(parents=True, exist_ok=True)
    if configured_output.exists():
        configured_output.unlink()
    shutil.copy2(produced_output, configured_output)


def main() -> int:
    args = parse_args()
    config_path = Path(args.config).resolve()
    config = textbook.load_config(config_path)
    manual_page_map = is_manual_page_map_config(config)
    configured_output_file = Path(config["output_file"]).resolve()

    if args.run_root:
        run_root = Path(args.run_root).resolve()
        run_root.mkdir(parents=True, exist_ok=True)
        for name in ("source", "sections", "render", "output", "events"):
            (run_root / name).mkdir(parents=True, exist_ok=True)
        run_id = run_root.name
    else:
        run_id = contracts.build_run_id(config_path.stem)
        run_root = contracts.build_run_root(PROJECT_ROOT, run_id)

    manifest = contracts.build_run_manifest(
        run_id=run_id,
        workflow_mode=args.workflow_mode,
        config_path=config_path,
        stage_order=manual_stage_order() if manual_page_map else None,
        selected_unit=detect_selected_unit(config),
        selected_lessons=detect_selected_lessons(config),
    )
    contracts.write_json(run_root / "run_manifest.json", manifest)
    write_job_manifest(run_root)
    orchestrator_events.append_event(
        run_root=run_root,
        run_id=run_id,
        event_type="run_created",
        status="pending",
        payload={
            "config_path": str(config_path),
            "workflow_mode": args.workflow_mode,
            "selected_unit": manifest["selected_unit"],
            "selected_lessons": manifest["selected_lessons"],
        },
    )
    orchestrator_events.append_event(
        run_root=run_root,
        run_id=run_id,
        event_type="run_started",
        status="running",
        payload={
            "stage_order": manifest["stage_order"],
        },
    )

    print(run_root, flush=True)
    if args.dry_run:
        return 0
    if manual_page_map:
        prepare_manual_source_artifacts(config=config, run_root=run_root)
        if args.stop_after in {
            "document_inventory_agent",
            "pdf_extract_agent",
            "page_index_agent",
            "schedule_parse_agent",
            "lesson_query_agent",
            "page_candidate_agent",
            "boundary_decision_agent",
            "boundary_validation_agent",
            "source_boundary_agent",
            "source_validation_agent",
        }:
            finalize_run_manifest(run_root, "success")
            return 0
    if not manual_page_map:
        try:
            update_run_manifest_for_stage(run_root, "document_inventory_agent", "running")
            document_inventory_result = runtime_driven_agents.execute_document_inventory(
                documents=build_document_inventory_inputs(config, config_path),
                run_root=run_root,
                run_id=run_id,
                project_root=PROJECT_ROOT,
            )
            update_run_manifest_for_stage(
                run_root,
                "document_inventory_agent",
                stage_status_from_counts(
                    warning_count=document_inventory_result["warning_count"],
                    blocked_count=document_inventory_result["blocked_count"],
                ),
                warning_count=document_inventory_result["warning_count"],
                error_count=document_inventory_result["blocked_count"],
            )
            if document_inventory_result["blocked_count"]:
                finalize_run_manifest(run_root, "failed")
                return 1
            if args.stop_after == "document_inventory_agent":
                finalize_run_manifest(run_root, "success")
                return 0
        except Exception:
            update_run_manifest_for_stage(run_root, "document_inventory_agent", "failed", error_count=1)
            finalize_run_manifest(run_root, "failed")
            raise
        try:
            update_run_manifest_for_stage(run_root, "pdf_extract_agent", "running")
            pdf_extract_result = runtime_driven_agents.execute_pdf_extract(
                run_root=run_root,
                run_id=run_id,
            )
            update_run_manifest_for_stage(
                run_root,
                "pdf_extract_agent",
                stage_status_from_counts(
                    warning_count=pdf_extract_result["warning_count"],
                    blocked_count=pdf_extract_result["blocked_count"],
                ),
                warning_count=pdf_extract_result["warning_count"],
                error_count=pdf_extract_result["blocked_count"],
            )
            if pdf_extract_result["blocked_count"]:
                finalize_run_manifest(run_root, "failed")
                return 1
            if args.stop_after == "pdf_extract_agent":
                finalize_run_manifest(run_root, "success")
                return 0
        except Exception:
            update_run_manifest_for_stage(run_root, "pdf_extract_agent", "failed", error_count=1)
            finalize_run_manifest(run_root, "failed")
            raise
        try:
            update_run_manifest_for_stage(run_root, "page_index_agent", "running")
            page_index_result = runtime_driven_agents.execute_page_index(
                run_root=run_root,
                run_id=run_id,
            )
            update_run_manifest_for_stage(
                run_root,
                "page_index_agent",
                stage_status_from_counts(
                    warning_count=page_index_result["warning_count"],
                    blocked_count=page_index_result["blocked_count"],
                ),
                warning_count=page_index_result["warning_count"],
                error_count=page_index_result["blocked_count"],
            )
            if page_index_result["blocked_count"]:
                finalize_run_manifest(run_root, "failed")
                return 1
            if args.stop_after == "page_index_agent":
                finalize_run_manifest(run_root, "success")
                return 0
        except Exception:
            update_run_manifest_for_stage(run_root, "page_index_agent", "failed", error_count=1)
            finalize_run_manifest(run_root, "failed")
            raise
        try:
            update_run_manifest_for_stage(run_root, "schedule_parse_agent", "running")
            schedule_parse_result = runtime_driven_agents.execute_schedule_parse(
                config_path=config_path,
                run_root=run_root,
                run_id=run_id,
            )
            update_run_manifest_for_stage(
                run_root,
                "schedule_parse_agent",
                stage_status_from_counts(
                    warning_count=schedule_parse_result["warning_count"],
                    blocked_count=schedule_parse_result["blocked_count"],
                ),
                warning_count=schedule_parse_result["warning_count"],
                error_count=schedule_parse_result["blocked_count"],
            )
            if schedule_parse_result["blocked_count"]:
                finalize_run_manifest(run_root, "failed")
                return 1
            if args.stop_after == "schedule_parse_agent":
                finalize_run_manifest(run_root, "success")
                return 0
        except Exception:
            update_run_manifest_for_stage(run_root, "schedule_parse_agent", "failed", error_count=1)
            finalize_run_manifest(run_root, "failed")
            raise
        try:
            update_run_manifest_for_stage(run_root, "lesson_query_agent", "running")
            lesson_query_result = runtime_driven_agents.execute_lesson_query(
                run_root=run_root,
                run_id=run_id,
            )
            update_run_manifest_for_stage(
                run_root,
                "lesson_query_agent",
                stage_status_from_counts(
                    warning_count=lesson_query_result["warning_count"],
                    blocked_count=lesson_query_result["blocked_count"],
                ),
                warning_count=lesson_query_result["warning_count"],
                error_count=lesson_query_result["blocked_count"],
            )
            if lesson_query_result["blocked_count"]:
                finalize_run_manifest(run_root, "failed")
                return 1
            if args.stop_after == "lesson_query_agent":
                finalize_run_manifest(run_root, "success")
                return 0
        except Exception:
            update_run_manifest_for_stage(run_root, "lesson_query_agent", "failed", error_count=1)
            finalize_run_manifest(run_root, "failed")
            raise
        try:
            update_run_manifest_for_stage(run_root, "page_candidate_agent", "running")
            page_candidate_result = runtime_driven_agents.execute_page_candidate(
                run_root=run_root,
                run_id=run_id,
                gemini_bin=args.gemini_bin,
                gemini_model=args.gemini_model,
                gemini_extensions=args.gemini_extensions,
                approval_mode=args.approval_mode,
                debug_artifacts=args.debug_artifacts,
                gemini_timeout_sec=gemini_timeout_sec(args),
                gemini_idle_timeout_sec=gemini_idle_timeout_sec(args),
            )
            update_run_manifest_for_stage(
                run_root,
                "page_candidate_agent",
                stage_status_from_counts(
                    warning_count=page_candidate_result["warning_count"],
                    blocked_count=page_candidate_result["blocked_count"],
                ),
                warning_count=page_candidate_result["warning_count"],
                error_count=page_candidate_result["blocked_count"],
            )
            if page_candidate_result["blocked_count"]:
                finalize_run_manifest(run_root, "failed")
                return 1
            if args.stop_after == "page_candidate_agent":
                finalize_run_manifest(run_root, "success")
                return 0
        except Exception:
            update_run_manifest_for_stage(run_root, "page_candidate_agent", "failed", error_count=1)
            finalize_run_manifest(run_root, "failed")
            raise
        try:
            update_run_manifest_for_stage(run_root, "boundary_decision_agent", "running")
            boundary_decision_result = runtime_driven_agents.execute_boundary_decision(
                run_root=run_root,
                run_id=run_id,
                gemini_bin=args.gemini_bin,
                gemini_model=args.gemini_model,
                gemini_extensions=args.gemini_extensions,
                approval_mode=args.approval_mode,
                debug_artifacts=args.debug_artifacts,
                gemini_timeout_sec=gemini_timeout_sec(args),
                gemini_idle_timeout_sec=gemini_idle_timeout_sec(args),
            )
            update_run_manifest_for_stage(
                run_root,
                "boundary_decision_agent",
                stage_status_from_counts(
                    warning_count=boundary_decision_result["warning_count"],
                    blocked_count=boundary_decision_result["blocked_count"],
                ),
                warning_count=boundary_decision_result["warning_count"],
                error_count=boundary_decision_result["blocked_count"],
            )
            if boundary_decision_result["blocked_count"]:
                finalize_run_manifest(run_root, "failed")
                return 1
            if args.stop_after == "boundary_decision_agent":
                finalize_run_manifest(run_root, "success")
                return 0
        except Exception:
            update_run_manifest_for_stage(run_root, "boundary_decision_agent", "failed", error_count=1)
            finalize_run_manifest(run_root, "failed")
            raise
        try:
            update_run_manifest_for_stage(run_root, "boundary_validation_agent", "running")
            boundary_validation_result = runtime_driven_agents.execute_boundary_validation(
                run_root=run_root,
                run_id=run_id,
            )
            update_run_manifest_for_stage(
                run_root,
                "boundary_validation_agent",
                stage_status_from_counts(
                    warning_count=boundary_validation_result["warning_count"],
                    blocked_count=boundary_validation_result["blocked_count"],
                ),
                warning_count=boundary_validation_result["warning_count"],
                error_count=boundary_validation_result["blocked_count"],
            )
            if boundary_validation_result["blocked_count"]:
                finalize_run_manifest(run_root, "failed")
                return 1
            if args.stop_after == "boundary_validation_agent":
                finalize_run_manifest(run_root, "success")
                return 0
        except Exception:
            update_run_manifest_for_stage(run_root, "boundary_validation_agent", "failed", error_count=1)
            finalize_run_manifest(run_root, "failed")
            raise
        try:
            update_run_manifest_for_stage(run_root, "source_boundary_agent", "running")
            source_boundary_result = source_boundary_agent.execute_source_boundary(
                config_path=config_path,
                run_root=run_root,
                run_id=run_id,
                chart_path=None,
                gemini_bin=args.gemini_bin,
                gemini_model=args.gemini_model,
                gemini_extensions=args.gemini_extensions,
                approval_mode=args.approval_mode,
                debug_artifacts=args.debug_artifacts,
                gemini_timeout_sec=gemini_timeout_sec(args),
            )
            update_run_manifest_for_stage(
                run_root,
                "source_boundary_agent",
                stage_status_from_counts(
                    warning_count=source_boundary_result["warning_count"],
                    blocked_count=source_boundary_result["blocked_count"],
                ),
                warning_count=source_boundary_result["warning_count"],
                error_count=source_boundary_result["blocked_count"],
            )
            if source_boundary_result["blocked_count"]:
                finalize_run_manifest(run_root, "failed")
                return 1
            if args.stop_after == "source_boundary_agent":
                finalize_run_manifest(run_root, "success")
                return 0
        except Exception:
            update_run_manifest_for_stage(run_root, "source_boundary_agent", "failed", error_count=1)
            finalize_run_manifest(run_root, "failed")
            raise
        try:
            update_run_manifest_for_stage(run_root, "source_validation_agent", "running")
            source_validation_result = source_validation_agent.execute_source_validation(
                config_path=config_path,
                run_root=run_root,
                run_id=run_id,
                gemini_bin=args.gemini_bin,
                gemini_model=args.gemini_model,
                gemini_extensions=args.gemini_extensions,
                approval_mode=args.approval_mode,
                debug_artifacts=args.debug_artifacts,
                gemini_timeout_sec=gemini_timeout_sec(args),
            )
            source_validation_status = "succeeded"
            if source_validation_result["blocked_count"]:
                source_validation_status = "blocked"
            elif source_validation_result["warning_count"]:
                source_validation_status = "succeeded_with_warning"
            update_run_manifest_for_stage(
                run_root,
                "source_validation_agent",
                source_validation_status,
                warning_count=source_validation_result["warning_count"],
                error_count=source_validation_result["blocked_count"],
            )
            if source_validation_result["blocked_count"]:
                finalize_run_manifest(run_root, "failed")
                return 1
            if args.stop_after == "source_validation_agent":
                finalize_run_manifest(run_root, "success")
                return 0
        except Exception:
            update_run_manifest_for_stage(run_root, "source_validation_agent", "failed", error_count=1)
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
            gemini_timeout_sec=lesson_gemini_timeout_sec(args),
            gemini_idle_timeout_sec=lesson_gemini_idle_timeout_sec(args),
            max_workers=lesson_worker_count(args, config),
        )
        lesson_stage_status = "succeeded"
        if lesson_result["warning_count"] or lesson_result["fallback_count"]:
            lesson_stage_status = "succeeded_with_warning"
        update_run_manifest_for_stage(
            run_root,
            "lesson_analysis_agent",
            lesson_stage_status,
            fallback_used=lesson_result["fallback_count"] > 0,
            warning_count=lesson_result["warning_count"],
            error_count=0,
            details={"fallback_category_counts": lesson_result.get("fallback_category_counts", {})},
        )
        write_job_manifest(run_root)
        write_generation_diagnostics(run_root)
        if args.stop_after == "lesson_analysis_agent":
            finalize_run_manifest(run_root, "success")
            return 0
    except Exception:
        update_run_manifest_for_stage(run_root, "lesson_analysis_agent", "failed", error_count=1)
        write_job_manifest(run_root)
        finalize_run_manifest(run_root, "failed")
        raise
    try:
        update_run_manifest_for_stage(run_root, "lesson_review_agent", "running")
        lesson_review_result = lesson_review_agent.execute_lesson_review(
            run_root=run_root,
            run_id=run_id,
            max_workers=lesson_worker_count(args, config),
        )
        lesson_review_status = "succeeded"
        if lesson_review_result["blocked_count"]:
            lesson_review_status = "blocked"
        elif lesson_review_result["warning_count"]:
            lesson_review_status = "succeeded_with_warning"
        update_run_manifest_for_stage(
            run_root,
            "lesson_review_agent",
            lesson_review_status,
            warning_count=lesson_review_result["warning_count"],
            error_count=lesson_review_result["blocked_count"],
        )
        if lesson_review_result["blocked_count"]:
            finalize_run_manifest(run_root, "failed")
            return 1
        if args.stop_after == "lesson_review_agent":
            finalize_run_manifest(run_root, "success")
            return 0
    except Exception:
        update_run_manifest_for_stage(run_root, "lesson_review_agent", "failed", error_count=1)
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
            gemini_timeout_sec=activity_gemini_timeout_sec(args),
            gemini_idle_timeout_sec=activity_gemini_idle_timeout_sec(args),
            max_workers=activity_worker_count(args, config),
        )
        activity_stage_status = "succeeded"
        if activity_result["warning_count"] or activity_result["fallback_count"]:
            activity_stage_status = "succeeded_with_warning"
        update_run_manifest_for_stage(
            run_root,
            "activity_plan_agent",
            activity_stage_status,
            fallback_used=activity_result["fallback_count"] > 0,
            warning_count=activity_result["warning_count"],
            error_count=0,
            details={"fallback_category_counts": activity_result.get("fallback_category_counts", {})},
        )
        write_job_manifest(run_root)
        write_generation_diagnostics(run_root)
        if args.stop_after == "activity_plan_agent":
            finalize_run_manifest(run_root, "success")
            return 0
    except Exception:
        update_run_manifest_for_stage(run_root, "activity_plan_agent", "failed", error_count=1)
        write_job_manifest(run_root)
        finalize_run_manifest(run_root, "failed")
        raise
    try:
        update_run_manifest_for_stage(run_root, "activity_review_agent", "running")
        activity_review_result = activity_review_agent.execute_activity_review(
            run_root=run_root,
            run_id=run_id,
            max_workers=activity_worker_count(args, config),
        )
        activity_review_status = "succeeded"
        if activity_review_result["blocked_count"]:
            activity_review_status = "blocked"
        elif activity_review_result["warning_count"]:
            activity_review_status = "succeeded_with_warning"
        update_run_manifest_for_stage(
            run_root,
            "activity_review_agent",
            activity_review_status,
            warning_count=activity_review_result["warning_count"],
            error_count=activity_review_result["blocked_count"],
        )
        write_job_manifest(run_root)
        if activity_review_result["blocked_count"]:
            finalize_run_manifest(run_root, "failed")
            return 1
        if args.stop_after == "activity_review_agent":
            finalize_run_manifest(run_root, "success")
            return 0
    except Exception:
        update_run_manifest_for_stage(run_root, "activity_review_agent", "failed", error_count=1)
        write_job_manifest(run_root)
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
        update_run_manifest_for_stage(run_root, "review_manifest_agent", "running")
        review_result = review_manifest_agent.execute_manifest_review(
            run_root=run_root,
            gemini_bin=args.gemini_bin,
            gemini_model=args.gemini_model,
            gemini_extensions=args.gemini_extensions,
            approval_mode=args.approval_mode,
            debug_artifacts=args.debug_artifacts,
            gemini_timeout_sec=gemini_timeout_sec(args),
        )
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
        update_run_manifest_for_stage(run_root, "verify_agent", "running")
        verify_result = verify_agent.execute_verify(
            run_root=run_root,
            run_id=run_id,
            gemini_bin=args.gemini_bin,
            gemini_model=args.gemini_model,
            gemini_extensions=args.gemini_extensions,
            approval_mode=args.approval_mode,
            debug_artifacts=args.debug_artifacts,
            gemini_timeout_sec=gemini_timeout_sec(args),
        )
        verify_status = "succeeded" if verify_result["warning_count"] == 0 else "succeeded_with_warning"
        update_run_manifest_for_stage(run_root, "verify_agent", verify_status, warning_count=verify_result["warning_count"])
        final_output_path = Path(verify_result["output_file"]).resolve()
        finalize_run_manifest(run_root, "success", str(final_output_path))
        if should_keep_run_artifacts(args, "success"):
            promote_final_output_only(
                produced_output=final_output_path,
                configured_output=configured_output_file,
            )
        else:
            promote_final_output_and_cleanup(
                run_root=run_root,
                produced_output=final_output_path,
                configured_output=configured_output_file,
            )
        return 0
    except Exception:
        update_run_manifest_for_stage(run_root, "verify_agent", "failed", error_count=1)
        finalize_run_manifest(run_root, "failed")
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
