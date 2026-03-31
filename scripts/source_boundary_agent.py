import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import agent_runtime  # noqa: E402
import generate_numbers_lesson as textbook  # noqa: E402
import pipeline_contracts as contracts  # noqa: E402
import run_gemini_cli_pipeline as gemini_pipeline  # noqa: E402


def serialize_jsonable(value):
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {key: serialize_jsonable(item) for key, item in value.items()}
    if isinstance(value, list):
        return [serialize_jsonable(item) for item in value]
    return value


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def lesson_sheet_name_map(source_dir: Path) -> dict[str, str]:
    lesson_queries = read_json(source_dir / "lesson_queries.json")
    return {lesson["lesson_id"]: lesson["sheet_name"] for lesson in lesson_queries.get("lessons", [])}


def build_boundary_payload(*, config: dict, source_dir: Path) -> dict:
    lesson_to_sheet = lesson_sheet_name_map(source_dir)
    raw_decisions = read_json(source_dir / "boundary_decisions.json")
    decision_map = {item["lesson_id"]: item for item in raw_decisions.get("boundaries", [])}
    payload_items = []

    for index, section in enumerate(config.get("sections", []), start=1):
        lesson_id = f"lesson-{index:03d}"
        decision = decision_map.get(lesson_id)
        sheet_name = lesson_to_sheet.get(lesson_id, section["sheet_name"])
        for source in section.get("sources", []):
            role = source.get("role", "textbook")
            if role == "textbook" and decision:
                decision_status = decision.get("status", "not_found")
                status = "matched" if decision_status in {"matched", "low_confidence"} else "not_found"
                payload_items.append(
                    {
                        "section_index": index - 1,
                        "sheet_name": sheet_name,
                        "resource_id": source["resource_id"],
                        "role": role,
                        "status": status,
                        "start_page": decision.get("start_page"),
                        "end_page": decision.get("end_page"),
                        "reason": decision.get("reason", ""),
                        "confidence": decision.get("confidence"),
                        "evidence_pages": decision.get("evidence_pages", []),
                    }
                )
            else:
                payload_items.append(
                    {
                        "section_index": index - 1,
                        "sheet_name": sheet_name,
                        "resource_id": source["resource_id"],
                        "role": role,
                        "status": "optional_not_found" if source.get("optional") else "not_found",
                        "start_page": None,
                        "end_page": None,
                        "reason": "No boundary decision was available for this source",
                        "confidence": 0.0,
                        "evidence_pages": [],
                    }
                )

    return {
        "schema_version": contracts.SCHEMA_VERSION,
        "boundaries": payload_items,
    }


def apply_boundary_payload(config: dict, payload: dict) -> tuple[int, int]:
    boundary_map = {
        (item["section_index"], item["resource_id"], item["role"]): item
        for item in payload["boundaries"]
    }
    warning_count = 0
    blocked_count = 0

    for section_index, section in enumerate(config["sections"]):
        source_ranges = []
        textbook_pages = None
        for source in section.get("sources", []):
            role = source.get("role", "textbook")
            item = boundary_map.get((section_index, source["resource_id"], role))
            if item is None:
                blocked_count += 1
                continue

            status = item["status"]
            source["_inference"] = {
                "status": status,
                "start_page": item["start_page"],
                "end_page": item["end_page"],
                "start_query": source.get("title_query") or section.get("title_query") or section["title"],
                "start_match_pages": item.get("evidence_pages", [])[:10],
                "start_match_count": len(item.get("evidence_pages", [])),
                "end_strategy": "boundary_decision_agent" if status == "matched" else None,
                "end_reference_query": source.get("end_before_query"),
                "intro_boundary_page": None,
                "reason": item.get("reason", ""),
                "confidence": item.get("confidence"),
            }

            if status == "matched":
                start_page = int(item["start_page"])
                end_page = int(item["end_page"])
                if end_page < start_page:
                    blocked_count += 1
                    continue
                pages = list(range(start_page, end_page + 1))
                source["pdf_pages"] = pages
                source_ranges.append(
                    {
                        "resource_id": source["resource_id"],
                        "role": role,
                        "pdf_pages": pages,
                    }
                )
                if role == "textbook" and textbook_pages is None:
                    textbook_pages = pages
            elif status == "optional_not_found" and source.get("optional"):
                warning_count += 1
            else:
                blocked_count += 1

        section["source_ranges"] = source_ranges
        if textbook_pages:
            section["pdf_pages"] = textbook_pages

    return warning_count, blocked_count


def execute_source_boundary(
    *,
    config_path: Path,
    run_root: Path,
    run_id: str,
    chart_path: Path | None = None,
    gemini_bin: str = "gemini",
    gemini_model: str | None = None,
    gemini_extensions: list[str] | None = None,
    approval_mode: str = "yolo",
    debug_artifacts: bool = False,
    gemini_timeout_sec: int = 120,
) -> dict:
    del gemini_bin, gemini_model, gemini_extensions, approval_mode, debug_artifacts, gemini_timeout_sec

    source_dir = run_root / "source"
    status_path = source_dir / "source_boundary.status.json"
    started_at = contracts.utc_now()
    status = {
        "schema_version": contracts.SCHEMA_VERSION,
        "stage": "source_boundary_agent",
        "lesson_id": None,
        "status": "running",
        "run_id": run_id,
        "started_at": started_at,
        "finished_at": None,
        "input_refs": [
            str(config_path.resolve()),
            str((source_dir / "lesson_queries.json").resolve()),
            str((source_dir / "page_candidates.json").resolve()),
            str((source_dir / "boundary_decisions.json").resolve()),
            str((source_dir / "boundary_validation.json").resolve()),
        ],
        "output_refs": [
            str(source_dir / "source_boundary.ai.json"),
            str(source_dir / "schedule_draft.json"),
            str(source_dir / "textbook_context.json"),
            str(source_dir / "runtime_config.json"),
        ],
        "fallback_used": False,
        "warnings": [],
        "errors": [],
        "agent_spec_path": str(agent_runtime.agent_doc_path("source_boundary_agent")),
        "runtime_driven": True,
    }
    if chart_path:
        status["input_refs"].append(str(chart_path.resolve()))
    contracts.write_json(status_path, status)

    try:
        config = textbook.load_config(config_path)
        validation = read_json(source_dir / "boundary_validation.json")
        boundary_payload = build_boundary_payload(config=config, source_dir=source_dir)
        contracts.write_json(source_dir / "source_boundary.ai.json", boundary_payload)
        warning_count, blocked_count = apply_boundary_payload(config, boundary_payload)

        schedule_draft = gemini_pipeline.build_schedule_draft(config, chart_path)
        contracts.write_json(source_dir / "schedule_draft.json", schedule_draft)
        gemini_pipeline.build_textbook_context(config, source_dir)

        runtime_config = serialize_jsonable(config)
        runtime_config.pop("resources_by_id", None)
        contracts.write_json(source_dir / "runtime_config.json", runtime_config)

        status["warnings"].extend(validation.get("warnings", []))
        if blocked_count or validation.get("blocking_issues"):
            status["status"] = "blocked"
            status["errors"].extend(validation.get("blocking_issues", []))
            if blocked_count and not validation.get("blocking_issues"):
                status["errors"].append("source boundary normalization returned unmatched required sources")
        elif warning_count or status["warnings"]:
            status["status"] = "succeeded_with_warning"
            if warning_count:
                status["warnings"].append(f"{warning_count} optional sources were not matched")
        else:
            status["status"] = "succeeded"
    except Exception as exc:
        status["status"] = "failed"
        status["errors"].append(str(exc))
        status["finished_at"] = contracts.utc_now()
        contracts.write_json(status_path, status)
        raise

    status["finished_at"] = contracts.utc_now()
    contracts.write_json(status_path, status)
    return {
        "schedule_draft_path": source_dir / "schedule_draft.json",
        "textbook_context_path": source_dir / "textbook_context.json",
        "runtime_config_path": source_dir / "runtime_config.json",
        "status_path": status_path,
        "warning_count": len(status["warnings"]),
        "blocked_count": len(status["errors"]),
    }
