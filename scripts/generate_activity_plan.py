import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lesson-analysis", required=True, help="Path to lesson_analysis json")
    parser.add_argument("--output", required=True, help="Output activity_plan json path")
    return parser.parse_args()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


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
    misconception = analysis["misconceptions"][0] if analysis["misconceptions"] else f"{analysis['lesson_title']}를 단순한 사실 암기로 이해한다."
    return {
        "activity_id": f"{analysis['lesson_id']}-learning-note",
        "lesson_id": analysis["lesson_id"],
        "activity_type": "learning_note",
        "level": "on-level",
        "learning_goal": analysis["learning_goals"][0],
        "prompt_text": f"수업에서 들은 설명을 바탕으로 {analysis['lesson_title']}를 자신의 말로 정리하고, 헷갈리기 쉬운 생각을 바로잡아 봅시다.",
        "layout_template": "learning_note",
        "source_refs": analysis["source_page_refs"],
        "teacher_notes": f"교과서 문장 복사가 아니라 자신의 말 정리인지, 그리고 '{misconception}'을 스스로 수정하는 흔적이 있는지 확인한다.",
        "student_writing_zones": [
            {"zone_id": "summary", "label": "수업시간에 들은 내용 정리", "input_area_type": "lined", "min_height": 620},
            {"zone_id": "question", "label": "헷갈렸던 생각 바로잡기 / 질문", "input_area_type": "free-writing", "min_height": 220}
        ],
        "estimated_minutes": 12,
        "review_status": "draft"
    }


def build_stw(analysis: dict) -> dict:
    first_chunk_pages = analysis["content_chunks"][0]["source_pages"]
    concept = analysis["key_concepts"][0] if analysis["key_concepts"] else analysis["lesson_title"]
    return {
        "activity_id": f"{analysis['lesson_id']}-see-think-wonder",
        "lesson_id": analysis["lesson_id"],
        "activity_type": "see_think_wonder",
        "level": "core",
        "learning_goal": f"{analysis['lesson_title']}를 생활 속 사례와 연결해 해석하고 새로운 질문을 만들 수 있다.",
        "prompt_text": f"교과서 설명을 그대로 옮기지 말고, {concept}이 실제 생활이나 사회 문제에서 어떻게 나타나는지 떠올리며 관찰, 해석, 질문을 넓혀 봅시다.",
        "layout_template": "see_think_wonder",
        "source_refs": first_chunk_pages,
        "teacher_notes": "교과서 속 장면 묘사에 머물지 않고 실제 사례 상상, 해석, 추가 질문으로 확장되는지 확인한다.",
        "student_writing_zones": [
            {"zone_id": "see", "label": "생활 속에서 비슷한 장면 / 사례 찾기", "input_area_type": "free-writing", "min_height": 380},
            {"zone_id": "think", "label": "왜 그렇게 보이는지 해석하기", "input_area_type": "free-writing", "min_height": 380},
            {"zone_id": "wonder", "label": "더 알아보고 싶은 점 / 따져볼 점", "input_area_type": "free-writing", "min_height": 380}
        ],
        "estimated_minutes": 10,
        "review_status": "draft"
    }


def build_worksheet(analysis: dict) -> dict:
    concepts = analysis["key_concepts"][:2]
    while len(concepts) < 2:
        concepts.append(f"핵심 개념 {len(concepts) + 1}")
    essential_question = analysis.get("essential_question") or f"{analysis['lesson_title']}를 다른 상황에 적용해 본다."
    return {
        "activity_id": f"{analysis['lesson_id']}-worksheet",
        "lesson_id": analysis["lesson_id"],
        "activity_type": "worksheet",
        "level": "extension",
        "learning_goal": f"{analysis['lesson_title']}의 핵심 개념을 새로운 사례에 적용하고 근거를 들어 판단할 수 있다.",
        "prompt_text": f"새로운 사례를 떠올리거나 제시된 상황을 보고, {analysis['lesson_title']}의 관점에서 더 바람직한 선택을 근거와 함께 판단해 봅시다.",
        "layout_template": "worksheet",
        "source_refs": analysis["source_page_refs"],
        "teacher_notes": f"'{essential_question}'에 답하듯 사고를 확장하는지, 그리고 {', '.join(analysis['key_concepts'][:3])} 중 적어도 두 개 이상을 근거와 연결하는지 본다.",
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
