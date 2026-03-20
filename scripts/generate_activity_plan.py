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
    return {
        "activity_id": f"{analysis['lesson_id']}-learning-note",
        "lesson_id": analysis["lesson_id"],
        "activity_type": "learning_note",
        "level": "on-level",
        "learning_goal": analysis["learning_goals"][0],
        "prompt_text": f"교과서를 읽고 {analysis['lesson_title']}의 핵심 내용을 배움 노트에 정리해 봅시다.",
        "layout_template": "learning_note",
        "source_refs": analysis["source_page_refs"],
        "teacher_notes": f"핵심 개념 {', '.join(analysis['key_concepts'][:3])}이 학생 정리에 포함되는지 확인한다.",
        "student_writing_zones": [
            {"zone_id": "summary", "label": "오늘 내용 요약", "input_area_type": "lined", "min_height": 520},
            {"zone_id": "question", "label": "질문 / 메모", "input_area_type": "free-writing", "min_height": 110}
        ],
        "estimated_minutes": 12,
        "review_status": "draft"
    }


def build_stw(analysis: dict) -> dict:
    first_chunk_pages = analysis["content_chunks"][0]["source_pages"]
    return {
        "activity_id": f"{analysis['lesson_id']}-see-think-wonder",
        "lesson_id": analysis["lesson_id"],
        "activity_type": "see_think_wonder",
        "level": "core",
        "learning_goal": f"{analysis['lesson_title']}와 관련된 장면을 관찰하고 질문을 만들 수 있다.",
        "prompt_text": f"{analysis['lesson_title']}와 관련된 교과서 장면이나 자료를 보고 보이는 것, 생각나는 것, 궁금한 것을 정리해 봅시다.",
        "layout_template": "see_think_wonder",
        "source_refs": first_chunk_pages,
        "teacher_notes": "관찰과 해석을 구분해 쓰는지 확인한다.",
        "student_writing_zones": [
            {"zone_id": "see", "label": "무엇이 보이나요?", "input_area_type": "free-writing", "min_height": 340},
            {"zone_id": "think", "label": "어떤 생각이 드나요?", "input_area_type": "free-writing", "min_height": 340},
            {"zone_id": "wonder", "label": "무엇이 궁금한가요?", "input_area_type": "free-writing", "min_height": 340}
        ],
        "estimated_minutes": 10,
        "review_status": "draft"
    }


def build_worksheet(analysis: dict) -> dict:
    concepts = analysis["key_concepts"][:2]
    while len(concepts) < 2:
        concepts.append(f"핵심 개념 {len(concepts) + 1}")
    return {
        "activity_id": f"{analysis['lesson_id']}-worksheet",
        "lesson_id": analysis["lesson_id"],
        "activity_type": "worksheet",
        "level": "extension",
        "learning_goal": f"{analysis['lesson_title']}의 핵심 개념을 근거와 함께 설명할 수 있다.",
        "prompt_text": f"{analysis['lesson_title']}와 관련된 핵심 개념을 정리하고, 자신의 생각을 근거와 함께 써 봅시다.",
        "layout_template": "worksheet",
        "source_refs": analysis["source_page_refs"],
        "teacher_notes": f"{', '.join(analysis['key_concepts'][:3])} 중 적어도 두 개 이상을 근거와 연결하는지 본다.",
        "student_writing_zones": [
            {"zone_id": "short-a", "label": f"{concepts[0]} 정리", "input_area_type": "inline-answer", "min_height": 72},
            {"zone_id": "short-b", "label": f"{concepts[1]} 연결", "input_area_type": "inline-answer", "min_height": 72},
            {"zone_id": "extended", "label": "근거를 들어 자신의 생각 쓰기", "input_area_type": "free-writing", "min_height": 120}
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
