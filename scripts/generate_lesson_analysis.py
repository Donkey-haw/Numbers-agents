import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import fitz


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import generate_numbers_lesson as textbook  # noqa: E402


STOPWORDS = {
    "그리고", "그러나", "하지만", "입니다", "있습니다", "합니다", "있어요", "수있다", "무엇", "무엇일까요",
    "어떤", "통해", "대한", "이해", "설명", "찾아", "보기", "학습", "단원", "주제", "차시", "사회",
    "우리", "나라", "민주주의", "학생", "내용", "활동", "그림", "자료", "질문", "생각", "정리"
}
PARTICLE_SUFFIXES = (
    "으로", "에서", "에게", "까지", "부터", "처럼", "보다", "라도",
    "은", "는", "이", "가", "을", "를", "와", "과", "의", "도", "만", "로", "란", "들",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to textbook config")
    parser.add_argument("--output-dir", required=True, help="Directory for lesson_analysis json files")
    return parser.parse_args()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def canonicalize_token(token: str) -> str:
    for suffix in PARTICLE_SUFFIXES:
        if token.endswith(suffix) and len(token) - len(suffix) >= 2:
            return token[: -len(suffix)]
    return token


def tokenize_korean(text: str) -> list[str]:
    tokens = re.findall(r"[가-힣]{2,}", text)
    cleaned = [canonicalize_token(token) for token in tokens]
    return [token for token in cleaned if token not in STOPWORDS]


def build_learning_goal(title: str) -> str:
    cleaned = title
    cleaned = cleaned.split("/")[0].strip()
    cleaned = re.sub(r"\s*\([^)]*\)", "", cleaned).strip()
    cleaned = re.sub(r"[?？]+$", "", cleaned).strip()
    cleaned = re.sub(r"(무엇일까요|어떻게 이루어질까요|어떤 역할을 할까요)$", "", cleaned).strip()
    cleaned = canonicalize_token(cleaned)
    if not cleaned:
        cleaned = title.strip(" ?？")
    return f"{cleaned}의 핵심 내용을 설명할 수 있다."


def pick_key_terms(text: str, title: str, limit: int = 5) -> list[str]:
    title_terms = tokenize_korean(title)
    freq = Counter(tokenize_korean(text))
    ordered = []
    for term in title_terms:
        if term not in ordered:
            ordered.append(term)
    for term, _ in freq.most_common():
        if term not in ordered:
            ordered.append(term)
        if len(ordered) >= limit:
            break
    return ordered[:limit]


def split_chunks(pages: list[int]) -> list[list[int]]:
    if len(pages) <= 2:
        return [pages]
    midpoint = max(1, len(pages) // 2)
    first = pages[:midpoint]
    second = pages[midpoint:]
    return [first, second] if second else [first]


def summarize_chunk(text: str, fallback: str) -> str:
    cleaned = normalize_spaces(text)
    if not cleaned:
        return fallback
    sentences = re.split(r"(?<=[.!?])\s+|(?<=다)\s+", cleaned)
    return sentences[0][:140]


def build_analysis(doc: fitz.Document, section: dict) -> dict:
    pages = section["pdf_pages"]
    page_texts = {page: normalize_spaces(doc[page - 1].get_text("text")) for page in pages}
    full_text = " ".join(page_texts.values())
    lesson_title = section["title"]
    key_concepts = pick_key_terms(full_text, lesson_title)
    vocabulary = key_concepts[:3]
    learning_goal = build_learning_goal(lesson_title)

    chunks = []
    for index, chunk_pages in enumerate(split_chunks(pages), start=1):
        chunk_text = " ".join(page_texts[page] for page in chunk_pages)
        knowledge_type = "concept"
        lowered = chunk_text
        if "과정" in lowered or "단계" in lowered:
            knowledge_type = "procedure"
        elif "역할" in lowered or "의미" in lowered:
            knowledge_type = "concept"
        elif "비교" in lowered or "차이" in lowered:
            knowledge_type = "comparison"
        elif "이유" in lowered or "원인" in lowered:
            knowledge_type = "cause-effect"

        suggested = ["learning_note", "worksheet"]
        if index == 1:
            suggested.insert(0, "see_think_wonder")

        chunks.append(
            {
                "chunk_id": f"{section['sheet_name']}-chunk-{index}",
                "label": f"학습 덩어리 {index}",
                "content_type": "mixed",
                "knowledge_type": knowledge_type,
                "summary": summarize_chunk(chunk_text, lesson_title),
                "source_pages": chunk_pages,
                "suggested_activity_types": suggested[:3],
            }
        )

    misconceptions = []
    if "선거" in full_text:
        misconceptions.append("선거를 단순히 사람을 뽑는 행사로만 이해할 수 있다.")
    if "민주주의" in full_text:
        misconceptions.append("민주주의의 핵심이 참여보다 결과에만 있다고 오해할 수 있다.")

    essential_question = lesson_title
    if not essential_question.endswith("?"):
        essential_question = f"{lesson_title.rstrip('다.')}"

    return {
        "schema_version": "1.0.0",
        "generated_at": utc_now(),
        "lesson_id": section.get("lesson_id", section["sheet_name"]),
        "sheet_name": section["sheet_name"],
        "lesson_title": lesson_title,
        "lesson_type": "core",
        "pdf_pages": pages,
        "essential_question": essential_question,
        "learning_goals": [learning_goal],
        "key_concepts": key_concepts,
        "vocabulary": vocabulary,
        "misconceptions": misconceptions,
        "difficulty_band": "on-level",
        "content_chunks": chunks,
        "source_page_refs": pages,
        "analysis_confidence": 0.75,
        "review_status": "draft",
        "notes": "자동 생성 초안. lesson title, key concepts, chunks를 검토 후 승인 필요."
    }


def main() -> int:
    args = parse_args()
    config = textbook.load_config(Path(args.config))
    textbook.infer_section_pages(config)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(config["pdf_path"])
    for section in config["sections"]:
        analysis = build_analysis(doc, section)
        out_path = output_dir / f"{section['card_file']}.lesson_analysis.json"
        out_path.write_text(json.dumps(analysis, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(out_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
