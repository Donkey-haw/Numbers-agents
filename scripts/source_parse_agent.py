import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import generate_numbers_lesson as textbook  # noqa: E402
import pipeline_contracts as contracts  # noqa: E402
import run_gemini_cli_pipeline as gemini_pipeline  # noqa: E402


def serialize_jsonable(value):
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {key: serialize_jsonable(item) for key, item in value.items() if not key.startswith("_")}
    if isinstance(value, list):
        return [serialize_jsonable(item) for item in value]
    return value


def find_source_range(section: dict, resource_id: str, role: str) -> dict | None:
    for item in section.get("source_ranges", []):
        if item.get("resource_id") == resource_id and item.get("role") == role:
            return item
    return None


def build_config_quality_review(config: dict) -> dict:
    findings = []
    warnings = []
    blocking_issues = []

    sections = config.get("sections", [])
    if not sections:
        blocking_issues.append("sections is empty")

    for section in sections:
        lesson_id = section["sheet_name"]
        if not section.get("sources"):
            blocking_issues.append(f"{lesson_id}: sources is empty")
            continue

        textbook_sources = [source for source in section["sources"] if source.get("role", "textbook") == "textbook"]
        if not textbook_sources:
            blocking_issues.append(f"{lesson_id}: no textbook source defined")

        for source in section.get("sources", []):
            inference = source.get("_inference", {})
            start_match_count = int(inference.get("start_match_count", 0) or 0)
            if start_match_count > 1:
                warnings.append(
                    f"{lesson_id}: source '{source['resource_id']}' title_query matched {start_match_count} pages"
                )
                findings.append(
                    {
                        "severity": "warning",
                        "message": f"{lesson_id}의 시작 쿼리가 여러 페이지에 매칭됩니다.",
                        "evidence_refs": [source.get("title_query") or section.get("title_query") or section["title"]],
                    }
                )

        if "source_ranges" not in section or not section["source_ranges"]:
            blocking_issues.append(f"{lesson_id}: source_ranges is empty after inference")

    decision = "pass"
    status = "succeeded"
    if blocking_issues:
        decision = "blocked"
        status = "blocked"
    elif warnings:
        decision = "pass_with_warning"
        status = "succeeded_with_warning"

    return {
        "schema_version": contracts.SCHEMA_VERSION,
        "stage": "review_source_config",
        "lesson_id": None,
        "status": status,
        "decision": decision,
        "findings": findings,
        "blocking_issues": blocking_issues,
        "warnings": warnings,
    }


def build_boundary_review(config: dict) -> dict:
    findings = []
    warnings = []
    blocking_issues = []
    entries = []

    for section in config.get("sections", []):
        lesson_id = section["sheet_name"]
        for source in section.get("sources", []):
            inference = source.get("_inference", {})
            entry = {
                "lesson_id": lesson_id,
                "resource_id": source["resource_id"],
                "role": source.get("role", "textbook"),
                "title_query": source.get("title_query") or section.get("title_query") or section["title"],
                "start_page": inference.get("start_page"),
                "end_page": inference.get("end_page"),
                "start_match_pages": inference.get("start_match_pages", []),
                "start_match_count": inference.get("start_match_count", 0),
                "end_strategy": inference.get("end_strategy"),
                "end_reference_query": inference.get("end_reference_query"),
                "intro_boundary_page": inference.get("intro_boundary_page"),
                "status": inference.get("status", "unknown"),
            }
            entries.append(entry)

            if entry["status"] == "not_found":
                blocking_issues.append(
                    f"{lesson_id}: source '{entry['resource_id']}' query '{entry['title_query']}' was not found"
                )
            elif entry["status"] == "optional_not_found":
                warnings.append(
                    f"{lesson_id}: optional source '{entry['resource_id']}' query '{entry['title_query']}' was not found"
                )
            elif int(entry["start_match_count"] or 0) > 1:
                warnings.append(
                    f"{lesson_id}: boundary start for '{entry['resource_id']}' is ambiguous ({entry['start_match_count']} matches)"
                )
            if entry["end_strategy"] == "topic_intro_signal":
                findings.append(
                    {
                        "severity": "info",
                        "message": f"{lesson_id}는 다음 주제 도입 신호를 감지해 더 이른 경계로 절단했습니다.",
                        "evidence_refs": [str(entry["intro_boundary_page"])],
                    }
                )

    decision = "pass"
    status = "succeeded"
    if blocking_issues:
        decision = "blocked"
        status = "blocked"
    elif warnings:
        decision = "pass_with_warning"
        status = "succeeded_with_warning"

    return {
        "schema_version": contracts.SCHEMA_VERSION,
        "stage": "review_source_boundary",
        "lesson_id": None,
        "status": status,
        "decision": decision,
        "findings": findings,
        "blocking_issues": blocking_issues,
        "warnings": warnings,
        "entries": entries,
    }


def build_supplement_review(config: dict) -> dict:
    findings = []
    warnings = []
    blocking_issues = []
    entries = []

    resources_by_id = config.get("resources_by_id", {})
    supplement_resources = {
        resource_id
        for resource_id, resource in resources_by_id.items()
        if resource.get("kind") in {"supplement", "reference"}
    }

    for section in config.get("sections", []):
        lesson_id = section["sheet_name"]
        for source in section.get("sources", []):
            resource_id = source["resource_id"]
            role = source.get("role", "textbook")
            if role not in {"supplement", "reference"} and resource_id not in supplement_resources:
                continue
            inference = source.get("_inference", {})
            matched_range = find_source_range(section, resource_id, role)
            status_value = "matched" if matched_range else inference.get("status", "not_found")
            entry = {
                "lesson_id": lesson_id,
                "resource_id": resource_id,
                "role": role,
                "title_query": source.get("title_query") or section.get("title_query") or section["title"],
                "status": status_value,
                "optional": bool(source.get("optional")),
                "pdf_pages": matched_range.get("pdf_pages", []) if matched_range else [],
            }
            entries.append(entry)

            if status_value != "matched":
                message = f"{lesson_id}: supplement '{resource_id}' was not matched"
                if entry["optional"]:
                    warnings.append(message)
                else:
                    blocking_issues.append(message)

    if supplement_resources and not any(entry["status"] == "matched" for entry in entries):
        warnings.append("No supplement resource was matched in this run")
        findings.append(
            {
                "severity": "warning",
                "message": "보조자료 리소스가 설정되어 있지만 실제 매칭된 차시가 없습니다.",
                "evidence_refs": sorted(supplement_resources),
            }
        )

    decision = "pass"
    status = "succeeded"
    if blocking_issues:
        decision = "blocked"
        status = "blocked"
    elif warnings:
        decision = "pass_with_warning"
        status = "succeeded_with_warning"

    return {
        "schema_version": contracts.SCHEMA_VERSION,
        "stage": "review_source_supplement",
        "lesson_id": None,
        "status": status,
        "decision": decision,
        "findings": findings,
        "blocking_issues": blocking_issues,
        "warnings": warnings,
        "entries": entries,
    }


def execute_source_parse(
    *,
    config_path: Path,
    run_root: Path,
    run_id: str,
    chart_path: Path | None = None,
) -> dict:
    source_dir = run_root / "source"
    status_path = source_dir / "source_parse.status.json"
    started_at = contracts.utc_now()
    status = {
        "schema_version": contracts.SCHEMA_VERSION,
        "stage": "source_parse_agent",
        "lesson_id": None,
        "status": "running",
        "run_id": run_id,
        "started_at": started_at,
        "finished_at": None,
        "input_refs": [str(config_path.resolve())],
        "output_refs": [
            str(source_dir / "schedule_draft.json"),
            str(source_dir / "textbook_context.json"),
            str(source_dir / "runtime_config.json"),
            str(source_dir / "config_quality_review.json"),
            str(source_dir / "boundary_review.json"),
            str(source_dir / "supplement_review.json"),
        ],
        "fallback_used": False,
        "warnings": [],
        "errors": [],
    }
    if chart_path:
        status["input_refs"].append(str(chart_path.resolve()))
    contracts.write_json(status_path, status)

    try:
        config = textbook.load_config(config_path)
        textbook.infer_section_pages(config)

        schedule_draft = gemini_pipeline.build_schedule_draft(config, chart_path)
        contracts.write_json(source_dir / "schedule_draft.json", schedule_draft)

        gemini_pipeline.build_textbook_context(config, source_dir)

        runtime_config = serialize_jsonable(config)
        runtime_config.pop("resources_by_id", None)
        contracts.write_json(source_dir / "runtime_config.json", runtime_config)

        config_quality_review = build_config_quality_review(config)
        boundary_review = build_boundary_review(config)
        supplement_review = build_supplement_review(config)
        contracts.write_json(source_dir / "config_quality_review.json", config_quality_review)
        contracts.write_json(source_dir / "boundary_review.json", boundary_review)
        contracts.write_json(source_dir / "supplement_review.json", supplement_review)

        review_warnings = (
            len(config_quality_review["warnings"])
            + len(boundary_review["warnings"])
            + len(supplement_review["warnings"])
        )
        review_blocking = (
            len(config_quality_review["blocking_issues"])
            + len(boundary_review["blocking_issues"])
            + len(supplement_review["blocking_issues"])
        )
        status["warnings"].extend(config_quality_review["warnings"])
        status["warnings"].extend(boundary_review["warnings"])
        status["warnings"].extend(supplement_review["warnings"])
        if review_blocking:
            status["status"] = "blocked"
            status["errors"].extend(config_quality_review["blocking_issues"])
            status["errors"].extend(boundary_review["blocking_issues"])
            status["errors"].extend(supplement_review["blocking_issues"])
        elif review_warnings:
            status["status"] = "succeeded_with_warning"
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
        "config_quality_review_path": source_dir / "config_quality_review.json",
        "boundary_review_path": source_dir / "boundary_review.json",
        "supplement_review_path": source_dir / "supplement_review.json",
        "status_path": status_path,
        "warning_count": len(status["warnings"]),
        "blocked_count": len(status["errors"]),
    }
