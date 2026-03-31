import argparse
import json
import re
import unicodedata
from pathlib import Path

from parse_progress_chart_pdf import parse_progress_chart, extract_lines


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CHART_PDF = PROJECT_ROOT / "textbook/사회/6학년 1학기 사회 진도표.pdf"
DEFAULT_CHART_JSON = PROJECT_ROOT / "configs/charts/social_6_1_progress_chart.json"
DEFAULT_CONFIG_DIR = PROJECT_ROOT / "configs/units/social"
TEXTBOOK_PDF = "textbook/사회/[사회]6_1_교과서.pdf"
TEMPLATE_PATH = "빈 넘버스 파일.numbers"
ACCENTS = [
    ["#6366f1", "#818cf8"],
    ["#4f46e5", "#7c3aed"],
    ["#0f766e", "#14b8a6"],
    ["#1d4ed8", "#3b82f6"],
    ["#d97706", "#f59e0b"],
    ["#9333ea", "#c084fc"],
]

BRACKET_TAG_RE = re.compile(r"^\[[^\]]+\]\s*")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--chart-pdf", default=str(DEFAULT_CHART_PDF))
    parser.add_argument("--chart-json", default=str(DEFAULT_CHART_JSON))
    parser.add_argument("--config-dir", default=str(DEFAULT_CONFIG_DIR))
    return parser.parse_args()


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFC", value).strip().lower()
    normalized = re.sub(r"[^0-9A-Za-z가-힣]+", "_", normalized)
    normalized = re.sub(r"_+", "_", normalized).strip("_")
    return normalized or "config"


def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFC", value)
    value = re.sub(r"\s+", " ", value.strip())
    replacements = {
        "생활 에": "생활에",
        "살 펴보기": "살펴보기",
        "까 닭": "까닭",
        "융 합": "융합",
        "살펴보 ": "살펴보기",
    }
    for before, after in replacements.items():
        value = value.replace(before, after)
    return value.strip(" /")


def split_activity_parts(activity: str) -> list[str]:
    activity = normalize_text(activity)
    if activity.startswith("[단원 도입]") or activity.startswith("[주제 도입]") or activity.startswith("[단원 마무리]") or activity.startswith("[주제 마무리]"):
        return []
    parts = [normalize_text(part) for part in activity.split("/") if normalize_text(part)]
    cleaned = []
    for part in parts:
        cleaned_part = normalize_text(BRACKET_TAG_RE.sub("", part))
        if not cleaned_part:
            continue
        cleaned.append(cleaned_part)
    return cleaned


def primary_activity(lesson: dict) -> str:
    for activity in lesson.get("activity_summary", []):
        parts = split_activity_parts(activity)
        if parts:
            return parts[0]
    for activity in lesson.get("activity_summary", []):
        activity = normalize_text(activity)
        if activity.startswith("[단원 도입]") or activity.startswith("[주제 도입]") or activity.startswith("[단원 마무리]") or activity.startswith("[주제 마무리]"):
            continue
        stripped = normalize_text(BRACKET_TAG_RE.sub("", activity))
        if stripped:
            return stripped
    return normalize_text(lesson.get("sheet_name", "차시"))


def next_boundary_query(sections: list[dict], current_index: int) -> str | None:
    for section in sections[current_index + 1 :]:
        lessons = section.get("lessons", [])
        if not lessons:
            continue
        return primary_activity(lessons[0])
    return None


def build_topic_config(unit: dict, topic: dict, topic_index: int, all_sections: list[dict]) -> tuple[str, dict]:
    topic_slug = slugify(topic["section_title"])
    unit_number = unit["unit_number"]
    config_name = f"social_6_1_unit{unit_number}_{topic_slug}"
    sections = []
    for lesson_index, lesson in enumerate(topic.get("lessons", [])):
        sheet_name = normalize_text(lesson["sheet_name"])
        title = primary_activity(lesson)
        sections.append(
            {
                "sheet_name": sheet_name,
                "card_file": slugify(f"{config_name}_{sheet_name}"),
                "title": title,
                "title_query": title,
                "badge": sheet_name,
                "accent": ACCENTS[lesson_index % len(ACCENTS)],
            }
        )

    config = {
        "project_root": str(PROJECT_ROOT),
        "pdf_path": TEXTBOOK_PDF,
        "template_path": TEMPLATE_PATH,
        "output_file": f"output/{config_name}.numbers",
        "footer": f"사회 6-1 · {unit_number}단원 · {normalize_text(topic['section_title'])}",
        "source_chart": "configs/charts/social_6_1_progress_chart.json",
        "sections": sections,
    }
    end_query = next_boundary_query(all_sections, topic_index)
    if end_query:
        config["end_before_query"] = end_query
    return config_name, config


def main() -> int:
    args = parse_args()
    chart_pdf = Path(args.chart_pdf).resolve()
    chart_json = Path(args.chart_json).resolve()
    config_dir = Path(args.config_dir).resolve()

    chart_payload = parse_progress_chart(extract_lines(chart_pdf))
    chart_payload["source_pdf"] = str(chart_pdf)
    chart_json.parent.mkdir(parents=True, exist_ok=True)
    chart_json.write_text(json.dumps(chart_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    config_dir.mkdir(parents=True, exist_ok=True)
    generated = []
    for unit in chart_payload.get("units", []):
        sections = unit.get("sections", [])
        for index, section in enumerate(sections):
            if section.get("section_type") != "topic":
                continue
            config_name, config = build_topic_config(unit, section, index, sections)
            config_path = config_dir / f"{config_name}.json"
            config_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            generated.append(str(config_path))

    print(json.dumps({"chart_json": str(chart_json), "generated_configs": generated}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
