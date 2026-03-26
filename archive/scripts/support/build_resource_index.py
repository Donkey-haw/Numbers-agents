import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import fitz


TITLE_LINE_MAX_LENGTH = 60
TITLE_MIN_LENGTH = 4
TITLE_STOPWORDS = {
    "스스로 해 보기",
    "함께 해 보기",
    "단원 마무리",
    "주제 마무리",
    "이 주제를 배우면",
    "한 문장 정리",
}
TOC_KEYWORDS = ("차례", "이 책의차례", "이책의차례", "목차", "세계 전도")
INDEX_KEYWORDS = ("찾아보기", "일반도")
APPENDIX_KEYWORDS = ("자료 출처", "인용 자료 출처", "백지도 보기", "부록")
ACTIVITY_KEYWORDS = ("학년 활동", "만들기", "게임을 하면서", "친구와 함께", "기념우표")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", required=True, help="Path to the PDF resource to index")
    parser.add_argument("--resource-id", required=True, help="Stable id for this resource")
    parser.add_argument("--label", required=True, help="Human-readable label for this resource")
    parser.add_argument(
        "--kind",
        default="textbook",
        choices=["textbook", "supplement", "reference", "worksheet", "courseware"],
        help="Resource kind",
    )
    parser.add_argument("--subject", help="Optional subject name")
    parser.add_argument("--output", required=True, help="Path to the generated resource_index JSON")
    return parser.parse_args()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_text(text: str) -> str:
    return re.sub(r"[^0-9A-Za-z가-힣]", "", text)


def clean_line(line: str) -> str:
    return re.sub(r"\s+", " ", line).strip()


def extract_title_candidates(text: str) -> list[str]:
    seen: list[str] = []
    for raw_line in text.splitlines():
        line = clean_line(raw_line)
        if not line:
            continue
        if len(line) < TITLE_MIN_LENGTH or len(line) > TITLE_LINE_MAX_LENGTH:
            continue
        if sum(char.isdigit() for char in line) > max(2, len(line) // 3):
            continue
        if not re.search(r"[가-힣A-Za-z]", line):
            continue
        if line in TITLE_STOPWORDS:
            continue
        if line not in seen:
            seen.append(line)
    return seen[:12]


def classify_page_type(page_num: int, raw_text: str, title_candidates: list[str]) -> str:
    normalized_text = normalize_text(raw_text)
    joined_titles = " ".join(title_candidates)
    candidate_text = f"{raw_text}\n{joined_titles}"

    if page_num <= 5:
        return "front_matter"
    if any(keyword in candidate_text for keyword in INDEX_KEYWORDS):
        return "index"
    if any(keyword in candidate_text for keyword in APPENDIX_KEYWORDS):
        return "appendix"
    if any(keyword in candidate_text for keyword in TOC_KEYWORDS):
        return "table_of_contents"
    if len(re.findall(r"\d+\s*~\s*\d+", raw_text)) >= 2:
        return "table_of_contents"
    if any(keyword in candidate_text for keyword in ACTIVITY_KEYWORDS):
        return "activity"
    if normalized_text:
        return "content"
    return "unknown"


def build_image_cache_key(pdf_path: Path, page_num: int) -> str:
    digest = hashlib.sha1(f"{pdf_path.resolve()}::{page_num}::3x".encode("utf-8")).hexdigest()
    return digest[:16]


def build_resource_index(
    pdf_path: Path,
    resource_id: str,
    label: str,
    kind: str,
    output_path: Path,
    subject: str | None = None,
) -> dict:
    doc = fitz.open(pdf_path)
    try:
        pages = []
        for page_num in range(1, doc.page_count + 1):
            raw_text = doc[page_num - 1].get_text("text")
            title_candidates = extract_title_candidates(raw_text)
            pages.append(
                {
                    "page_num": page_num,
                    "raw_text": raw_text,
                    "normalized_text": normalize_text(raw_text),
                    "title_candidates": title_candidates,
                    "page_type": classify_page_type(page_num, raw_text, title_candidates),
                    "image_cache_key": build_image_cache_key(pdf_path, page_num),
                }
            )
    finally:
        doc.close()

    payload = {
        "schema_version": "1.0.0",
        "generated_at": utc_now(),
        "resource_id": resource_id,
        "label": label,
        "kind": kind,
        "pdf_path": str(pdf_path.resolve()),
        "page_count": len(pages),
        "pages": pages,
    }
    if subject:
        payload["subject"] = subject

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    args = parse_args()
    pdf_path = Path(args.pdf).resolve()
    output_path = Path(args.output).resolve()
    payload = build_resource_index(
        pdf_path=pdf_path,
        resource_id=args.resource_id,
        label=args.label,
        kind=args.kind,
        output_path=output_path,
        subject=args.subject,
    )
    print(output_path)
    print(f"pages={payload['page_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
