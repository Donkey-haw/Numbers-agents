import argparse
import json
import re
from pathlib import Path

import fitz


HEADER_LINES = {"대단원", "주제", "주요 학습 활동", "차시", "준비물", "6학년 1학기 사회 진도표"}
TOPIC_MARKERS = set("①②③④⑤⑥⑦⑧⑨")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", required=True, help="Progress chart PDF path")
    parser.add_argument("--output", required=True, help="Output JSON path")
    return parser.parse_args()


def normalize_line(text: str) -> str:
    text = text.replace("〜", "~").replace("∼", "~").replace("～", "~")
    text = re.sub(r"\s+", " ", text.strip())
    return text


def clean_title(parts: list[str]) -> str:
    text = " ".join(part for part in parts if part)
    text = normalize_line(text)
    text = re.sub(r"([가-힣])\s+([이가은는을를와과의도만로란])\s+", r"\1\2 ", text)
    text = re.sub(r"\s+([,./])", r"\1", text)
    return text.strip()


def is_schedule_line(line: str) -> bool:
    return bool(re.fullmatch(r"\d+(?:~\d+)?", line))


def is_unit_header_line(line: str) -> bool:
    return bool(re.fullmatch(r"\d+\.", line))


def consume_schedule(lines: list[str], index: int) -> tuple[str | None, int]:
    if index >= len(lines):
        return None, index
    line = lines[index]
    if is_schedule_line(line):
        if re.fullmatch(r"\d+~\d", line) and index + 1 < len(lines) and re.fullmatch(r"\d", lines[index + 1]):
            return f"{line}{lines[index + 1]}", index + 2
        return line, index + 1
    return None, index


def is_section_header_start(lines: list[str], index: int) -> bool:
    if index >= len(lines):
        return False
    line = lines[index]
    if is_unit_header_line(line):
        return True
    if line in TOPIC_MARKERS:
        return True
    if re.fullmatch(r"\d+단원", line):
        return index + 1 < len(lines) and lines[index + 1] in {"도입", "정리"}
    return False


def extract_lines(pdf_path: Path) -> list[str]:
    doc = fitz.open(pdf_path)
    lines: list[str] = []
    for page in doc:
        for raw in page.get_text("text").splitlines():
            line = normalize_line(raw)
            if not line or line in HEADER_LINES:
                continue
            lines.append(line)
    return lines


def parse_progress_chart(lines: list[str]) -> dict:
    units = []
    current_unit = None
    current_section = None
    index = 0

    while index < len(lines):
        line = lines[index]

        if is_unit_header_line(line):
            unit_number = int(line[:-1])
            index += 1
            title_parts = []
            while index < len(lines) and not re.fullmatch(r"\d+단원", lines[index]):
                title_parts.append(lines[index])
                index += 1
            current_unit = {
                "unit_number": unit_number,
                "unit_title": clean_title(title_parts),
                "sections": [],
            }
            units.append(current_unit)
            continue

        if re.fullmatch(r"\d+단원", line):
            if current_unit is None:
                index += 1
                continue
            section_kind = "도입" if index + 1 < len(lines) and lines[index + 1] == "도입" else "정리"
            section = {
                "section_type": "unit_intro" if section_kind == "도입" else "unit_summary",
                "section_label": f"{line} {section_kind}",
                "section_title": f"{line} {section_kind}",
                "lessons": [],
            }
            current_unit["sections"].append(section)
            current_section = section
            index += 2
            continue

        if line in TOPIC_MARKERS:
            if current_unit is None:
                index += 1
                continue
            marker = line
            index += 1
            title_parts = []
            while index < len(lines) and not lines[index].startswith("•"):
                title_parts.append(lines[index])
                index += 1
            section = {
                "section_type": "topic",
                "section_label": marker,
                "section_title": clean_title(title_parts),
                "lessons": [],
            }
            current_unit["sections"].append(section)
            current_section = section
            continue

        if line.startswith("•") and current_section is not None:
            activity_lines = []
            while index < len(lines):
                current_line = lines[index]
                if current_line.startswith("•"):
                    activity_lines.append(current_line.lstrip("• ").strip())
                    index += 1
                    continue
                if (
                    activity_lines
                    and not is_schedule_line(current_line)
                    and not is_section_header_start(lines, index)
                ):
                    activity_lines[-1] = normalize_line(f"{activity_lines[-1]} {current_line}")
                    index += 1
                    continue
                break

            schedule, index = consume_schedule(lines, index)
            if schedule is None:
                continue

            material_lines = []
            while index < len(lines) and not lines[index].startswith("•") and not is_section_header_start(lines, index):
                material_lines.append(lines[index])
                index += 1

            current_section["lessons"].append(
                {
                    "sheet_name": f"{schedule.replace('~', '-')}차시",
                    "chart_range": schedule,
                    "activity_summary": activity_lines,
                    "materials": clean_title(material_lines),
                }
            )
            continue

        index += 1

    return {
        "schema_version": "1.0.0",
        "source_type": "progress_chart_pdf",
        "units": units,
    }


def main() -> int:
    args = parse_args()
    pdf_path = Path(args.pdf).resolve()
    output_path = Path(args.output).resolve()
    lines = extract_lines(pdf_path)
    payload = parse_progress_chart(lines)
    payload["source_pdf"] = str(pdf_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
