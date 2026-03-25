import argparse
import json
import re
from pathlib import Path


ACCENT_SEQUENCE = [
    ["#6366f1", "#818cf8"],
    ["#4f46e5", "#7c3aed"],
    ["#0f766e", "#14b8a6"],
    ["#1d4ed8", "#3b82f6"],
    ["#d97706", "#f59e0b"],
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle", required=True, help="Path to unit_bundle JSON")
    parser.add_argument("--project-root", required=True, help="Project root path")
    parser.add_argument("--template-path", required=True, help="Numbers template path relative to project root")
    parser.add_argument("--output-file", required=True, help="Output Numbers path relative to project root")
    parser.add_argument("--footer", required=True, help="Footer text for rendered cards")
    parser.add_argument("--output", required=True, help="Output config JSON path")
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
    parser.add_argument("--review-overrides", help="Optional JSON file that approves supplement candidate pages")
    parser.add_argument("--review-output", help="Optional path to write supplement review report JSON")
    return parser.parse_args()


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sanitize_name(value: str) -> str:
    return re.sub(r"[^0-9A-Za-z가-힣]+", "_", value).strip("_")


def make_override_key(sheet_name: str, resource_id: str) -> str:
    return f"{sheet_name}::{resource_id}"


def load_review_overrides(path: Path | None) -> dict[str, dict]:
    if path is None:
        return {}
    payload = read_json(path)
    return {
        make_override_key(item["sheet_name"], item["resource_id"]): item
        for item in payload.get("overrides", [])
    }


def apply_review_override(section: dict, source: dict, overrides: dict[str, dict]) -> dict:
    override = overrides.get(make_override_key(section["sheet_name"], source["resource_id"]))
    if not override:
        return source
    merged = dict(source)
    if "title_query" in override:
        merged["title_query"] = override["title_query"]
    if "pdf_pages" in override:
        merged["pdf_pages"] = override["pdf_pages"]
        merged["candidate_pages"] = override["pdf_pages"]
    if "match_status" in override:
        merged["match_status"] = override["match_status"]
    else:
        merged["match_status"] = "matched"
    notes = merged.get("notes", "")
    suffix = "Approved via review override."
    merged["notes"] = f"{notes} {suffix}".strip()
    return merged


def should_include_source(
    source: dict,
    include_needs_review_supplements: bool,
    include_unmatched_supplements: bool,
) -> bool:
    if source.get("role") != "supplement":
        return True
    if include_unmatched_supplements:
        return True
    status = source.get("match_status")
    if status in (None, "matched"):
        return True
    if status == "needs_review":
        return include_needs_review_supplements
    return False


def build_runtime_config(
    bundle: dict,
    project_root: str,
    template_path: str,
    output_file: str,
    footer: str,
    review_overrides: dict[str, dict] | None = None,
    include_needs_review_supplements: bool = False,
    include_unmatched_supplements: bool = False,
) -> tuple[dict, dict]:
    review_overrides = review_overrides or {}
    review_items = []
    sections = []
    for index, section in enumerate(bundle["sections"]):
        included_sources = []
        for source in section["sources"]:
            resolved_source = apply_review_override(section, source, review_overrides)
            if should_include_source(
                resolved_source,
                include_needs_review_supplements=include_needs_review_supplements,
                include_unmatched_supplements=include_unmatched_supplements,
            ):
                included_sources.append(resolved_source)
            else:
                review_items.append(
                    {
                        "sheet_name": section["sheet_name"],
                        "lesson_title": section["lesson_title"],
                        "resource_id": resolved_source["resource_id"],
                        "role": resolved_source["role"],
                        "match_status": resolved_source.get("match_status", "not_found"),
                        "title_query": resolved_source.get("title_query"),
                        "candidate_pages": resolved_source.get("candidate_pages", []),
                        "notes": resolved_source.get("notes", ""),
                    }
                )

        if not included_sources:
            raise RuntimeError(f"No runnable sources remain for sheet '{section['sheet_name']}'")
        primary_source = next((source for source in included_sources if source["role"] == "textbook"), included_sources[0])
        sections.append(
            {
                "sheet_name": section["sheet_name"],
                "card_file": f"{sanitize_name(bundle['unit_id'])}_{sanitize_name(section['sheet_name'])}",
                "title": section["lesson_title"],
                "badge": section["sheet_name"],
                "accent": ACCENT_SEQUENCE[index % len(ACCENT_SEQUENCE)],
                "sources": included_sources,
                "title_query": primary_source.get("title_query", section["lesson_title"]),
            }
        )

    included_resource_ids = {source["resource_id"] for section in sections for source in section["sources"]}
    config = {
        "project_root": project_root,
        "template_path": template_path,
        "output_file": output_file,
        "footer": footer,
        "resources": [resource for resource in bundle["resources"] if resource["resource_id"] in included_resource_ids],
        "sections": sections,
    }
    review_report = {
        "schema_version": "1.0.0",
        "bundle_id": bundle["unit_id"],
        "excluded_sources": review_items,
        "override_template": [
            {
                "sheet_name": item["sheet_name"],
                "resource_id": item["resource_id"],
                "title_query": item["title_query"],
                "pdf_pages": item["candidate_pages"],
                "match_status": "matched",
            }
            for item in review_items
            if item["candidate_pages"]
        ],
    }
    return config, review_report


def main() -> int:
    args = parse_args()
    bundle = read_json(Path(args.bundle))
    review_overrides = load_review_overrides(Path(args.review_overrides)) if args.review_overrides else {}
    config, review_report = build_runtime_config(
        bundle=bundle,
        project_root=args.project_root,
        template_path=args.template_path,
        output_file=args.output_file,
        footer=args.footer,
        review_overrides=review_overrides,
        include_needs_review_supplements=args.include_needs_review_supplements,
        include_unmatched_supplements=args.include_unmatched_supplements,
    )
    output_path = Path(args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if args.review_output:
        review_output = Path(args.review_output).resolve()
        review_output.parent.mkdir(parents=True, exist_ok=True)
        review_output.write_text(json.dumps(review_report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(output_path)
    print(f"sections={len(config['sections'])}")
    print(f"excluded_sources={len(review_report['excluded_sources'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
