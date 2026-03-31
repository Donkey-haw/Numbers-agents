import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lesson-analysis", required=True, help="Path to lesson_analysis json")
    parser.add_argument("--output", required=True, help="Output activity_plan json path")
    return parser.parse_args()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip()


QUESTION_TOKENS = {
    "무엇",
    "무엇일까요",
    "왜",
    "어떻게",
    "어떤",
    "일어났을까요",
    "이루었을까요",
    "달라졌을까요",
    "살펴볼까요",
}


def lesson_topic(analysis: dict) -> str:
    title = normalize_spaces(analysis.get("lesson_title") or analysis["lesson_id"])
    title = re.sub(r"[?？]+$", "", title).strip()
    return title or analysis["lesson_id"]


def first_learning_goal(analysis: dict) -> str:
    goals = analysis.get("learning_goals") or []
    if goals:
        return goals[0]
    return f"{lesson_topic(analysis)}의 핵심 내용을 설명할 수 있다."


def primary_concepts(analysis: dict, limit: int = 3) -> list[str]:
    concepts = []
    for item in analysis.get("key_concepts", []):
        cleaned = normalize_spaces(item)
        if not cleaned or cleaned in QUESTION_TOKENS:
            continue
        concepts.append(cleaned)
    return concepts[:limit]


def focus_phrase(analysis: dict) -> str:
    concepts = primary_concepts(analysis, limit=2)
    if len(concepts) >= 2:
        return f"{concepts[0]} {concepts[1]}"
    if concepts:
        return concepts[0]
    return lesson_topic(analysis)


def misconception_text(analysis: dict) -> str:
    misconceptions = [normalize_spaces(item) for item in analysis.get("misconceptions", []) if normalize_spaces(item)]
    if misconceptions:
        return misconceptions[0]
    return f"{focus_phrase(analysis)}를 단순한 사실 암기로만 이해할 수 있다."


def chunk_summaries(analysis: dict) -> list[str]:
    chunks = []
    for chunk in analysis.get("content_chunks", []):
        summary = normalize_spaces(chunk.get("summary", ""))
        if summary:
            chunks.append(summary)
    return chunks


def main_chunk_pages(analysis: dict) -> list[int]:
    chunks = analysis.get("content_chunks", [])
    if chunks and chunks[0].get("source_pages"):
        return chunks[0]["source_pages"]
    return analysis.get("source_page_refs", [])


def teacher_note_keywords(analysis: dict, limit: int = 3) -> str:
    concepts = primary_concepts(analysis, limit=limit)
    if not concepts:
        return lesson_topic(analysis)
    if len(concepts) == 1:
        return concepts[0]
    return ", ".join(concepts)


def build_activity_plan(analysis: dict) -> dict:
    return {
        "schema_version": "1.0.0",
        "generated_at": utc_now(),
        "lesson_id": analysis["lesson_id"],
        "activities": [
            build_learning_note(analysis),
            build_stw(analysis),
            build_worksheet(analysis)
        ]
    }


def build_learning_note(analysis: dict) -> dict:
    topic = lesson_topic(analysis)
    misconception = misconception_text(analysis)
    learning_goal = first_learning_goal(analysis)
    key_phrase = focus_phrase(analysis)
    return {
        "activity_id": f"{analysis['lesson_id']}-learning-note",
        "lesson_id": analysis["lesson_id"],
        "object_role": "learning_note",
        "lesson_flow_stage": "during",
        "activity_type": "learning_note",
        "level": "on-level",
        "learning_goal": learning_goal,
        "prompt_text": f"오늘 배운 {topic}의 핵심 내용을 자신의 말로 정리하고, 헷갈리기 쉬운 생각을 바로잡아 봅시다.",
        "layout_template": "learning_note",
        "source_refs": analysis.get("source_page_refs", []),
        "teacher_notes": f"교과서 문장을 그대로 옮기지 않고 '{key_phrase}'이라는 내용을 자신의 말로 설명하는지, 그리고 '{misconception}' 같은 오해를 스스로 수정하는지 확인한다.",
        "student_writing_zones": [
            {"zone_id": "summary", "label": "수업시간에 들은 내용 정리", "input_area_type": "lined", "min_height": 620},
            {"zone_id": "question", "label": "헷갈렸던 생각 바로잡기 / 질문", "input_area_type": "free-writing", "min_height": 220}
        ],
        "estimated_minutes": 12,
        "review_status": "draft"
    }


def build_stw(analysis: dict) -> dict:
    topic = lesson_topic(analysis)
    first_chunk_pages = main_chunk_pages(analysis)
    concept = focus_phrase(analysis)
    summaries = chunk_summaries(analysis)
    anchor_summary = summaries[0] if summaries else f"{topic}와 관련된 사례를 떠올려 봅시다."
    return {
        "activity_id": f"{analysis['lesson_id']}-see-think-wonder",
        "lesson_id": analysis["lesson_id"],
        "object_role": "activity_area",
        "lesson_flow_stage": "during",
        "activity_type": "see_think_wonder",
        "level": "core",
        "learning_goal": f"{topic}를 실제 사례와 연결해 해석하고 새로운 질문을 만들 수 있다.",
        "prompt_text": f"'{anchor_summary}'를 떠올리며, '{concept}'라는 주제가 실제 생활이나 사회에서 어떻게 드러나는지 관찰하고 해석한 뒤 더 알아보고 싶은 질문을 만들어 봅시다.",
        "layout_template": "see_think_wonder",
        "source_refs": first_chunk_pages,
        "teacher_notes": f"교과서 문장 재진술에 머물지 않고, '{concept}'를 실제 사례와 연결해 해석하고 질문을 확장하는지 확인한다.",
        "student_writing_zones": [
            {"zone_id": "see", "label": "생활 속에서 비슷한 장면 / 사례 찾기", "input_area_type": "free-writing", "min_height": 380},
            {"zone_id": "think", "label": "왜 그렇게 보이는지 해석하기", "input_area_type": "free-writing", "min_height": 380},
            {"zone_id": "wonder", "label": "더 알아보고 싶은 점 / 따져볼 점", "input_area_type": "free-writing", "min_height": 380}
        ],
        "estimated_minutes": 10,
        "review_status": "draft"
    }


def build_worksheet(analysis: dict) -> dict:
    topic = lesson_topic(analysis)
    concepts = primary_concepts(analysis, limit=2)
    while len(concepts) < 2:
        concepts.append(f"핵심 개념 {len(concepts) + 1}")
    essential_question = normalize_spaces(analysis.get("essential_question") or f"{topic}를 다른 상황에 적용해 본다.")
    summaries = chunk_summaries(analysis)
    anchor_summary = summaries[-1] if summaries else f"{topic}를 새로운 사례에 적용해 봅시다."
    teacher_keywords = teacher_note_keywords(analysis)
    return {
        "activity_id": f"{analysis['lesson_id']}-worksheet",
        "lesson_id": analysis["lesson_id"],
        "object_role": "worksheet",
        "lesson_flow_stage": "after",
        "activity_type": "worksheet",
        "level": "extension",
        "learning_goal": f"{topic}의 핵심 개념을 새로운 사례에 적용하고 근거를 들어 판단할 수 있다.",
        "prompt_text": f"'{anchor_summary}'를 바탕으로 새로운 사례를 떠올리거나 제시된 상황을 보고, {topic}의 관점에서 더 바람직한 선택을 근거와 함께 판단해 봅시다.",
        "layout_template": "worksheet",
        "source_refs": analysis.get("source_page_refs", []),
        "teacher_notes": f"'{essential_question}'에 답하듯 사고를 확장하는지, 그리고 {teacher_keywords}를 근거와 연결해 판단하는지 확인한다.",
        "student_writing_zones": [
            {"zone_id": "short-a", "label": f"새 사례에서 보이는 {concepts[0]}", "input_area_type": "inline-answer", "min_height": 90},
            {"zone_id": "short-b", "label": f"판단에 필요한 {concepts[1]} 근거", "input_area_type": "inline-answer", "min_height": 90},
            {"zone_id": "extended", "label": "더 바람직한 선택과 이유 쓰기", "input_area_type": "free-writing", "min_height": 240}
        ],
        "estimated_minutes": 15,
        "review_status": "draft"
    }


def main() -> int:
    args = parse_args()
    analysis = json.loads(Path(args.lesson_analysis).read_text(encoding="utf-8"))
    plan = build_activity_plan(analysis)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
