import json
from datetime import datetime, timezone
from pathlib import Path


SCHEMA_VERSION = "1.0.0"
WORKFLOW_MODES = {"stable", "freeform_experimental", "recovery"}
STAGE_STATUS_VALUES = {
    "pending",
    "running",
    "succeeded",
    "succeeded_with_warning",
    "failed",
    "blocked",
}
REVIEW_DECISION_VALUES = {"pass", "pass_with_warning", "needs_revision", "blocked"}
RUN_FINAL_STATUS_VALUES = {"pending", "running", "success", "partial-with-warning", "textbook-only", "failed"}
DEFAULT_STAGE_ORDER = [
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


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_timestamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def sanitize_name(value: str) -> str:
    return "".join(char if char.isalnum() or char in "-_." else "_" for char in value)


def section_artifact_stem(section: dict) -> str:
    base = section.get("card_file") or section.get("sheet_name") or "section"
    title = section.get("title") or section.get("sheet_name") or "untitled"
    return sanitize_name(f"{base}__{title}")


def build_run_id(config_stem: str) -> str:
    return f"{sanitize_name(config_stem)}-{run_timestamp()}"


def build_run_root(project_root: Path, run_id: str) -> Path:
    root = project_root / "artifacts" / "runs" / run_id
    root.mkdir(parents=True, exist_ok=True)
    for name in ("source", "sections", "render", "output", "events"):
        (root / name).mkdir(parents=True, exist_ok=True)
    return root


def write_json(path: Path, payload: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def make_status_summary(
    stage: str,
    status: str = "pending",
    fallback_used: bool = False,
    warning_count: int = 0,
    error_count: int = 0,
    details: dict | None = None,
) -> dict:
    if status not in STAGE_STATUS_VALUES:
        raise ValueError(f"Invalid stage status: {status}")
    return {
        "stage": stage,
        "status": status,
        "fallback_used": fallback_used,
        "warning_count": warning_count,
        "error_count": error_count,
        "details": details or {},
    }


def build_run_manifest(
    *,
    run_id: str,
    workflow_mode: str,
    config_path: Path,
    stage_order: list[str] | None = None,
    selected_unit: str | None = None,
    selected_lessons: list[str] | None = None,
) -> dict:
    if workflow_mode not in WORKFLOW_MODES:
        raise ValueError(f"Invalid workflow mode: {workflow_mode}")
    ordered = stage_order or list(DEFAULT_STAGE_ORDER)
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "workflow_mode": workflow_mode,
        "config_path": str(config_path.resolve()),
        "selected_unit": selected_unit,
        "selected_lessons": selected_lessons or [],
        "stage_order": ordered,
        "started_at": utc_now(),
        "finished_at": None,
        "final_status": "pending",
        "final_output_file": None,
        "status_summary": [make_status_summary(stage) for stage in ordered],
    }
