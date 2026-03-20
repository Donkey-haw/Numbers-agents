import argparse
import json
import re
import subprocess
from pathlib import Path


ACCENTS = [
    ["#6366f1", "#818cf8"],
    ["#4f46e5", "#7c3aed"],
    ["#0f766e", "#14b8a6"],
    ["#1d4ed8", "#3b82f6"],
    ["#d97706", "#f59e0b"],
    ["#9333ea", "#c084fc"],
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True, help="Progress chart image path")
    parser.add_argument("--project-root", default=".", help="Project root path")
    parser.add_argument("--pdf-path", required=True, help="Relative PDF path from project root")
    parser.add_argument("--template-path", default="빈 넘버스 파일.numbers", help="Relative Numbers template path")
    parser.add_argument("--output-file", required=True, help="Relative output .numbers path")
    parser.add_argument("--config-output", required=True, help="Where to write config json")
    parser.add_argument("--footer", required=True, help="Footer text for cards")
    parser.add_argument("--textbook-page-offset", type=int, default=2, help="PDF page minus printed textbook page")
    parser.add_argument("--end-before-query", help="Textbook heading that marks the end of the last lesson")
    parser.add_argument("--unit-end-page", type=int, help="Fallback PDF page number for the last lesson end")
    parser.add_argument("--print-ocr", action="store_true", help="Print OCR lines before parsing")
    parser.add_argument("--start-after", help="Only parse lines after this heading text appears")
    parser.add_argument("--stop-before", help="Stop parsing when this heading text appears")
    return parser.parse_args()


def run_ocr(script_path: Path, image_path: Path) -> list[dict]:
    result = subprocess.run(
        ["swift", str(script_path), str(image_path)],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def normalize_text(text: str) -> str:
    text = text.replace("〜", "~")
    text = text.replace("∼", "~")
    text = text.replace("～", "~")
    text = re.sub(r"\s+", " ", text.strip())
    return text


def filter_lines(ocr_lines: list[dict], start_after: str | None, stop_before: str | None) -> list[dict]:
    started = start_after is None
    filtered = []
    for line in ocr_lines:
        text = normalize_text(line["text"])
        if not started:
            if start_after in text:
                started = True
            continue
        if stop_before and stop_before in text:
            break
        filtered.append({**line, "text": text})
    return filtered


def parse_sections(ocr_lines: list[dict]) -> list[dict]:
    sections = []
    seen = set()
    for line in ocr_lines:
        text = line["text"]
        if "차시" not in text:
            continue
        match = re.search(
            r"\[?\s*(\d+(?:[~-]\d+)?)차시\]?\s*(.+?)(?:\s*\(사회\s*\d+(?:~\d+)?쪽\))?$",
            text,
        )
        if not match:
            match = re.search(
                r"(\d+(?:[~-]\d+)?)차시\s*(.+?)(?:\s*사회\s*\d+(?:~\d+)?쪽)?$",
                text,
            )
        if not match:
            continue

        sheet_range = match.group(1).replace("~", "-")
        sheet_name = f"{sheet_range}차시"
        title = re.sub(r"\s*\(사회\s*\d+(?:~\d+)?쪽\)\s*$", "", match.group(2)).strip(" /_")
        key = (sheet_name, title)
        if key in seen:
            continue
        seen.add(key)

        card_file = re.sub(r"[^0-9A-Za-z가-힣_-]+", "_", f"draft_{sheet_name}")
        accent = ACCENTS[len(sections) % len(ACCENTS)]
        sections.append(
            {
                "sheet_name": sheet_name,
                "card_file": card_file,
                "title": title,
                "badge": sheet_name,
                "accent": accent,
            }
        )
    return sections


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    image_path = (project_root / args.image).resolve() if not Path(args.image).is_absolute() else Path(args.image)
    swift_script = project_root / "scripts" / "ocr_progress_chart.swift"
    ocr_lines = run_ocr(swift_script, image_path)

    filtered_lines = filter_lines(ocr_lines, args.start_after, args.stop_before)

    if args.print_ocr:
        for line in filtered_lines:
            print(line["text"])

    sections = parse_sections(filtered_lines)
    if not sections:
        raise SystemExit("No sections parsed from OCR output")

    config = {
        "project_root": str(project_root),
        "pdf_path": args.pdf_path,
        "template_path": args.template_path,
        "output_file": args.output_file,
        "footer": args.footer,
        "textbook_page_offset": args.textbook_page_offset,
        "sections": sections,
        "_note": "OCR draft. Review titles and end boundary before generation. Printed chart page ranges are intentionally ignored.",
    }
    if args.end_before_query:
        config["end_before_query"] = args.end_before_query
    if args.unit_end_page:
        config["unit_end_page"] = args.unit_end_page
    output_path = (project_root / args.config_output).resolve() if not Path(args.config_output).is_absolute() else Path(args.config_output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
