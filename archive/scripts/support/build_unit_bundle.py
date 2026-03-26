import argparse
import difflib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import generate_numbers_lesson as textbook  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--chart", required=True, help="Path to progress_chart_map JSON")
    parser.add_argument("--unit-number", required=True, type=int, help="Target unit number")
    parser.add_argument("--topic-title", required=True, help="Target topic section_title")
    parser.add_argument("--resource-index", action="append", required=True, help="Path to resource_index JSON")
    parser.add_argument("--primary-resource-id", required=True, help="resource_id of the main textbook")
    parser.add_argument(
        "--supplement-resource-id",
        action="append",
        default=[],
        help="resource_id to include as optional supplement sources",
    )
    parser.add_argument("--existing-config", help="Optional existing config JSON to enrich bundle sources")
    parser.add_argument("--output", required=True, help="Output unit_bundle JSON path")
    parser.add_argument("--include-unit-summary", action="store_true", help="Include unit summary after the topic")
    parser.add_argument("--exclude-unit-intro", action="store_true", help="Skip the unit intro lesson")
    return parser.parse_args()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_text(text: str) -> str:
    return re.sub(r"[^0-9A-Za-z가-힣]", "", text)


def strip_bracket_prefix(text: str) -> str:
    return re.sub(r"^\[[^\]]+\]\s*", "", text).strip()


def derive_lesson_title(section: dict, lesson: dict) -> str:
    if section["section_type"] == "unit_intro":
        return "단원·주제 도입"
    if section["section_type"] == "unit_summary":
        return "단원 정리"
    summaries = [strip_bracket_prefix(item) for item in lesson.get("activity_summary", []) if strip_bracket_prefix(item)]
    if summaries:
        return summaries[0]
    return section["section_title"]


def parse_virtual_units(chart: dict) -> list[dict]:
    sections = chart["units"][0]["sections"]
    virtual_units: list[dict] = []
    current_unit: dict | None = None

    for section in sections:
        label = section.get("section_label", "")
        intro_match = re.match(r"(\d+)단원 도입", label)
        if intro_match:
            if current_unit is not None:
                virtual_units.append(current_unit)
            current_unit = {
                "unit_number": int(intro_match.group(1)),
                "sections": [section],
            }
            continue
        if current_unit is None:
            continue
        current_unit["sections"].append(section)

    if current_unit is not None:
        virtual_units.append(current_unit)

    for unit in virtual_units:
        topic_titles = [section["section_title"] for section in unit["sections"] if section["section_type"] == "topic"]
        unit["unit_title"] = ", ".join(topic_titles) if topic_titles else f"{unit['unit_number']}단원"

    return virtual_units


def load_resource_indexes(paths: list[Path]) -> dict[str, dict]:
    indexes = {}
    for path in paths:
        payload = read_json(path)
        indexes[payload["resource_id"]] = payload
    return indexes


def load_existing_config(path: Path | None) -> dict[str, dict]:
    if path is None:
        return {}
    config = textbook.load_config(path)
    textbook.infer_section_pages(config)
    return {section["sheet_name"]: section for section in config["sections"]}


def similarity(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, a, b).ratio()


def best_title_candidate_match(page: dict, normalized_query: str) -> float:
    best = 0.0
    for candidate in page.get("title_candidates", []):
        normalized_candidate = normalize_text(candidate)
        if not normalized_candidate:
            continue
        if normalized_query in normalized_candidate or normalized_candidate in normalized_query:
            return 1.0
        best = max(best, similarity(normalized_query, normalized_candidate))
    return best


def page_type_rank(page_type: str) -> int:
    ranks = {
        "content": 0,
        "activity": 1,
        "unknown": 2,
        "front_matter": 3,
        "table_of_contents": 4,
        "appendix": 5,
        "index": 6,
    }
    return ranks.get(page_type, 99)


def find_resource_matches(
    resource_index: dict,
    queries: list[str],
    max_pages: int = 2,
) -> tuple[str | None, list[int], str]:
    pages = resource_index["pages"]
    for query in queries:
        normalized_query = normalize_text(query)
        if not normalized_query:
            continue
        exact_pages = [page for page in pages if best_title_candidate_match(page, normalized_query) >= 1.0]
        if exact_pages:
            exact_pages.sort(key=lambda page: (page_type_rank(page.get("page_type", "unknown")), page["page_num"]))
            best_type = exact_pages[0].get("page_type", "unknown")
            selected = [page["page_num"] for page in exact_pages[:max_pages]]
            if best_type == "content":
                return query, selected, "matched"
            if best_type == "activity":
                return query, selected, "needs_review"
            return query, selected, "needs_review"

        text_pages = [page for page in pages if normalized_query in page.get("normalized_text", "")]
        if text_pages:
            text_pages.sort(key=lambda page: (page_type_rank(page.get("page_type", "unknown")), page["page_num"]))
            best_type = text_pages[0].get("page_type", "unknown")
            selected = [page["page_num"] for page in text_pages[:max_pages]]
            if best_type in {"content", "activity"}:
                return query, selected, "needs_review"

    fuzzy_candidates: list[tuple[float, int, str]] = []
    for query in queries:
        normalized_query = normalize_text(query)
        if not normalized_query:
            continue
        for page in pages:
            score = best_title_candidate_match(page, normalized_query)
            if score >= 0.58:
                fuzzy_candidates.append((score, page_type_rank(page.get("page_type", "unknown")), page["page_num"], query))

    if fuzzy_candidates:
        fuzzy_candidates.sort(key=lambda item: (-item[0], item[1], item[2]))
        selected_pages: list[int] = []
        selected_query = fuzzy_candidates[0][3]
        for _, _, page_num, _ in fuzzy_candidates:
            if page_num not in selected_pages:
                selected_pages.append(page_num)
            if len(selected_pages) >= max_pages:
                break
        return selected_query, selected_pages, "needs_review"

    return None, [], "not_found"


def build_bundle(args: argparse.Namespace) -> dict:
    chart = read_json(Path(args.chart))
    virtual_units = parse_virtual_units(chart)
    target_unit = next((unit for unit in virtual_units if unit["unit_number"] == args.unit_number), None)
    if target_unit is None:
        raise RuntimeError(f"Could not find unit_number={args.unit_number} in chart")

    topic_section = next(
        (
            section
            for section in target_unit["sections"]
            if section["section_type"] == "topic" and section["section_title"] == args.topic_title
        ),
        None,
    )
    if topic_section is None:
        raise RuntimeError(f"Could not find topic '{args.topic_title}' in unit {args.unit_number}")

    resource_indexes = load_resource_indexes([Path(path) for path in args.resource_index])
    if args.primary_resource_id not in resource_indexes:
        raise RuntimeError(f"Primary resource_id '{args.primary_resource_id}' not found in resource indexes")
    for resource_id in args.supplement_resource_id:
        if resource_id not in resource_indexes:
            raise RuntimeError(f"Supplement resource_id '{resource_id}' not found in resource indexes")

    existing_sections = load_existing_config(Path(args.existing_config)) if args.existing_config else {}

    selected_sections = []
    if not args.exclude_unit_intro:
        intro_section = next((section for section in target_unit["sections"] if section["section_type"] == "unit_intro"), None)
        if intro_section is not None:
            selected_sections.append(intro_section)
    selected_sections.append(topic_section)
    if args.include_unit_summary:
        summary_section = next((section for section in target_unit["sections"] if section["section_type"] == "unit_summary"), None)
        if summary_section is not None:
            selected_sections.append(summary_section)

    bundle_sections = []
    for section in selected_sections:
        topic_title = section["section_title"] if section["section_type"] == "topic" else args.topic_title
        for lesson in section["lessons"]:
            existing = existing_sections.get(lesson["sheet_name"])
            lesson_title = existing["title"] if existing else derive_lesson_title(section, lesson)

            primary_source = {
                "resource_id": args.primary_resource_id,
                "role": "textbook",
            }
            if existing:
                primary_source["title_query"] = existing.get("title_query", existing["title"])
                primary_source["pdf_pages"] = existing["pdf_pages"]

            sources = [primary_source]
            for resource_id in args.supplement_resource_id:
                resource_index = resource_indexes[resource_id]
                supplement_queries = []
                for candidate in (
                    lesson_title,
                    primary_source.get("title_query"),
                    topic_title,
                ):
                    if candidate and candidate not in supplement_queries:
                        supplement_queries.append(candidate)
                matched_query, candidate_pages, match_status = find_resource_matches(resource_index, supplement_queries)
                supplement_source = {
                    "resource_id": resource_id,
                    "role": "supplement",
                    "optional": True,
                }
                if matched_query and candidate_pages and match_status == "matched":
                    supplement_source["title_query"] = matched_query
                    supplement_source["pdf_pages"] = candidate_pages
                    supplement_source["candidate_pages"] = candidate_pages
                    supplement_source["match_status"] = match_status
                    supplement_source["notes"] = "Matched provisionally from resource_index. Review before final use."
                elif matched_query and candidate_pages and match_status == "needs_review":
                    supplement_source["title_query"] = matched_query
                    supplement_source["candidate_pages"] = candidate_pages
                    supplement_source["match_status"] = match_status
                    supplement_source["notes"] = "Potential supplement match found from title_candidates. Manual review required."
                else:
                    supplement_source["title_query"] = topic_title
                    supplement_source["match_status"] = "not_found"
                    supplement_source["notes"] = "No clear supplement match found in resource_index. Safe to skip."
                sources.append(supplement_source)

            bundle_sections.append(
                {
                    "sheet_name": lesson["sheet_name"],
                    "section_type": section["section_type"],
                    "lesson_title": lesson_title,
                    "topic_title": topic_title,
                    "sources": sources,
                }
            )

    bundle_resources = []
    included_resource_ids = {source["resource_id"] for section in bundle_sections for source in section["sources"]}
    for resource_id in included_resource_ids:
        resource_index = resource_indexes[resource_id]
        bundle_resources.append(
            {
                "resource_id": resource_index["resource_id"],
                "label": resource_index["label"],
                "kind": resource_index["kind"],
                "pdf_path": resource_index["pdf_path"],
            }
        )

    return {
        "schema_version": "1.0.0",
        "generated_at": utc_now(),
        "unit_id": f"unit{args.unit_number}_{re.sub(r'[^0-9A-Za-z가-힣]+', '_', args.topic_title).strip('_')}",
        "unit_title": target_unit["unit_title"],
        "subject": resource_indexes[args.primary_resource_id].get("subject", ""),
        "source_chart": str(Path(args.chart).resolve()),
        "resources": sorted(bundle_resources, key=lambda item: item["resource_id"]),
        "sections": bundle_sections,
    }


def main() -> int:
    args = parse_args()
    bundle = build_bundle(args)
    output_path = Path(args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(bundle, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(output_path)
    print(f"sections={len(bundle['sections'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
