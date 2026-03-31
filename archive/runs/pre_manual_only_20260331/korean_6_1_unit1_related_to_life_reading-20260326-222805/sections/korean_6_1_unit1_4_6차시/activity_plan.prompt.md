# Runtime Agent Spec: activity_plan_agent

아래 AGENT.md는 이 단계의 역할과 경계를 정의한다.
문서에 적힌 역할만 수행하고, 하지 말아야 할 일은 넘지 마라.
출력 형식 요구가 있으면 반드시 지켜라.

# activity_plan_agent

## 역할
- lesson analysis를 바탕으로 차시별 activity plan을 생성한다.
- 같은 단계 안에서 `review_activity_agent` 산출물을 함께 만든다.
- Gemini 결과가 실패하면 local activity builder로 fallback한다.

구현:
- `scripts/activity_plan_agent.py`

## 입력
- `sections/<lesson>/lesson_analysis.json`

## 출력
- `sections/<lesson>/activity_plan.prompt.md`
- `sections/<lesson>/activity_plan_ai.json`
- `sections/<lesson>/activity_plan.repair.prompt.md`
- `sections/<lesson>/activity_plan_ai_repair.json`
- `sections/<lesson>/activity_plan.json`
- `sections/<lesson>/activity_review.json`
- `sections/<lesson>/activity_plan.status.json`

## 내부 책임
- Gemini prompt를 구성한다.
- 1차 응답이 문제 있으면 repair prompt를 한 번 더 시도한다.
- 실패 시 `generate_activity_plan.py`의 로컬 builder로 fallback한다.
- activity 수준 구조 검토 결과를 review JSON으로 남긴다.
- lesson 단위 병렬 실행을 지원한다.

## 성공 조건
- 각 lesson에 `activity_plan.json`이 생성된다.
- 각 lesson에 `activity_review.json`이 생성된다.
- status 파일에서 attempt, repair, fallback 여부가 확인된다.

## fallback
- Gemini timeout
- Gemini JSON 생성 실패
- repair 이후에도 plan 정규화 실패

## review_activity_agent 내장 규칙
- `activities` 비어 있으면 blocked
- 각 activity의 `source_refs` 필수
- 각 activity의 `student_writing_zones` 필수
- `lesson_flow_stage`는 `before/during/after`
- `object_role`은 허용 enum 안에 있어야 함

## 하지 말아야 할 일
- source 경계나 lesson analysis를 수정하지 않는다.
- HTML 렌더와 캡처를 수행하지 않는다.
- Numbers 배치를 직접 제어하지 않는다.

## 테스트 방법
```bash
python3 scripts/pipeline_orchestrator.py \
  --config configs/<config>.json \
  --stop-after review_activity_agent \
  --keep-run-artifacts
```

## 확인 포인트
- `activity_plan.status.json`의 `repair_attempted`
- `activity_plan.status.json`의 `fallback_used`
- `activity_review.json`의 `decision`



# Execution Task

You are helping a local textbook-to-Numbers pipeline generate student activity cards.

Your job is not to copy an existing template.
Your job is to design activities that fit the lesson and the Numbers canvas.

Rules:
- Return JSON only.
- Do not include markdown fences.
- Do not use tools or external files. Answer from the prompt content only.
- Keep `review_status` as `draft`.
- Ground every activity in the provided lesson analysis only.
- Do not invent source pages outside `source_page_refs`.
- Build each activity as a full standalone HTML card inside `html_content`.
- Follow `NumbersDesign.md` as a constraint document, not as a fixed template catalog.
- Include `object_role` and `lesson_flow_stage` on every activity.
- Use the textbook as a launch point, not as a script to restate.
- Every activity must serve at least one of these functions:
  - supplement what the textbook does not make students do yet
  - deepen understanding through comparison, reasoning, justification, or structured explanation
  - extend learning into a new case, medium, decision, or expression
- Do not merely rephrase a textbook paragraph, textbook question, or textbook activity.
- Prioritize student writing, drawing, organizing, comparing, and expressing over decorative layout.
- The outer page background must remain transparent or white so it matches the default Numbers sheet background.
- Do not place a gray canvas or gray body background behind the card.

When planning a card, think in this order:
1. What object is this card serving?
   - learning note
   - activity area
   - reference material
   - worksheet
   - AI-linked follow-up
2. Where does it belong in the lesson flow?
   - before class activity
   - during class activity
   - after class / wrap-up activity
3. What learning function does it serve?
   - creative expression
   - reasoning / explanation
   - practice / reinforcement
   - summary / reflection
   - resource use
4. What should students physically do with Apple Pencil on this card?
5. How is this card different from simply following the textbook page?

Design expectations:
- Prefer roomy cards with large, usable writing areas.
- Use strong visual hierarchy, but do not overfit to one repeated layout.
- You may create new layouts when the lesson demands it.
- The card should make the intended student action obvious at a glance.
- If the card is note-oriented, it should help students organize what they heard during class.
- If the card is creative, include guidance or examples without crowding out writing space.
- If the card is reasoning-focused, make the thinking process recordable.
- If the card is practice-focused, provide enough repetition space.
- Favor prompts that ask students to compare, judge, redesign, connect to life, explain with evidence, or apply ideas to a new case.
- When you use textbook content, transform it into a new task structure rather than echoing the printed prompt.

Required visual constraints:
- student writing areas must use white backgrounds
- writing areas must have bold dark borders comparable to `2px solid #333`
- major writing areas should usually be `420px+` tall when the task expects paragraph-level handwriting
- do not compress the full card into a shallow banner-like layout
- cards should be tall enough for handwriting
- avoid dense multi-column layouts unless the lesson truly needs them
- do not make every card look like the same badge-header-template clone


Generate one `activity_plan` JSON object from the lesson analysis below.

Lesson analysis:
{
  "lesson_id": "4-6차시",
  "sheet_name": "4-6차시",
  "lesson_title": "작품을 읽고 시대적 상황과 인물이 추구하는 가치에 대하여 질문하기",
  "lesson_type": "core",
  "pdf_pages": [
    15,
    16,
    17,
    18,
    19,
    20,
    21,
    22,
    23,
    24,
    25,
    26
  ],
  "essential_question": "작품 속 인물의 말과 행동을 통해 그들이 중요하게 여기는 가치와 시대적 배경을 어떻게 찾아낼 수 있을까?",
  "learning_goals": [
    "「책 깎는 소년」을 읽고 조선 시대의 출판 문화와 시대적 상황을 파악할 수 있다.",
    "장호와 봉운의 말과 행동을 비교하여 각 인물이 추구하는 가치를 설명할 수 있다.",
    "인물이 추구하는 가치와 시대적 상황에 대하여 질문을 만들고 답할 수 있다."
  ],
  "key_concepts": [
    "시대적 상황",
    "인물이 추구하는 가치",
    "조선 시대 출판 문화",
    "가치 비교",
    "질문 만들기"
  ],
  "vocabulary": [
    "필사",
    "목판 인쇄술",
    "각수",
    "서포",
    "대패질",
    "판각",
    "수모",
    "책판"
  ],
  "misconceptions": [
    "가치를 단순히 돈이나 명예 같은 눈에 보이는 결과물로만 한정하여 생각할 수 있다.",
    "시대적 배경을 단순히 옛날 이야기로만 치부하고 인물의 고민과 연결 짓지 못할 수 있다."
  ],
  "content_chunks": [
    {
      "chunk_id": "4-6차시-chunk-1",
      "label": "시대적 배경 탐구",
      "knowledge_type": "concept",
      "summary": "조선 시대의 출판 문화(필사, 목판 인쇄술)와 관련 직업(각수), 장소(서포)를 통해 이야기의 배경이 되는 시대적 상황을 이해한다.",
      "source_pages": [
        15
      ]
    },
    {
      "chunk_id": "4-6차시-chunk-2",
      "label": "이야기 읽기 및 갈등 파악",
      "knowledge_type": "cause-effect",
      "summary": "「책 깎는 소년」을 읽으며 부자가 되고 싶은 장호와 진심으로 책을 만들고 싶어 하는 봉운의 태도 차이를 파악한다.",
      "source_pages": [
        16,
        17,
        18,
        19,
        20,
        21,
        22
      ]
    },
    {
      "chunk_id": "4-6차시-chunk-3",
      "label": "가치 비교 및 분석",
      "knowledge_type": "comparison",
      "summary": "장호(경제적 가치/성공)와 봉운(장인 정신/보람)이 추구하는 가치를 구체적인 근거를 들어 비교하고 분석한다.",
      "source_pages": [
        23,
        24,
        25
      ]
    },
    {
      "chunk_id": "4-6차시-chunk-4",
      "label": "질문하기 및 면담 활동",
      "knowledge_type": "application",
      "summary": "인물이 추구하는 가치를 깊이 있게 이해하기 위해 질문을 만들고, 역할극을 통해 인물 면담 활동을 수행한다.",
      "source_pages": [
        26
      ]
    }
  ],
  "source_page_refs": [
    15,
    16,
    17,
    18,
    19,
    20,
    21,
    22,
    23,
    24,
    25,
    26
  ]
}

Target schema:
{
  "required_root_fields": [
    "schema_version",
    "generated_at",
    "lesson_id",
    "activities"
  ],
  "required_activity_fields": [
    "activity_id",
    "lesson_id",
    "object_role",
    "lesson_flow_stage",
    "activity_type",
    "level",
    "learning_goal",
    "prompt_text",
    "layout_template",
    "html_content",
    "source_refs",
    "student_writing_zones",
    "estimated_minutes",
    "review_status"
  ],
  "activity_type_enum": [
    "freeform_html",
    "learning_note",
    "see_think_wonder",
    "worksheet",
    "frayer_model",
    "reference_response",
    "spectrum_sorting"
  ],
  "level_enum": [
    "core",
    "on-level",
    "extension"
  ],
  "input_area_type_enum": [
    "lined",
    "free-writing",
    "inline-answer",
    "grid",
    "spectrum"
  ]
}

Shape example:
{
  "schema_version": "1.0.0",
  "generated_at": "2026-01-01T00:00:00+00:00",
  "lesson_id": "2차시",
  "activities": [
    {
      "activity_id": "act-2-1",
      "lesson_id": "2차시",
      "object_role": "activity_area",
      "lesson_flow_stage": "during",
      "activity_type": "freeform_html",
      "level": "core",
      "learning_goal": "핵심 개념을 새로운 상황에 적용해 설명할 수 있다.",
      "prompt_text": "새로운 사례를 보고 핵심 개념이 왜 필요한지 설명해 봅시다.",
      "layout_template": "freeform_html",
      "html_content": "<!DOCTYPE html><html lang='ko'><head><meta charset='UTF-8'><style>body{width:1600px;background:transparent;font-family:\"Noto Sans KR\",sans-serif;}.card{background:#fff;padding:32px;border-radius:24px;}.writing{background:#fff;border:2px solid #333;min-height:520px;border-radius:16px;}</style></head><body><div class='card'><h1>활동 제목</h1><div class='writing'></div></div></body></html>",
      "source_refs": [
        56,
        57
      ],
      "teacher_notes": "",
      "student_writing_zones": [
        {
          "zone_id": "main_response",
          "label": "핵심 생각 쓰기",
          "input_area_type": "free-writing",
          "min_height": 520
        }
      ],
      "estimated_minutes": 12,
      "review_status": "draft"
    }
  ]
}

Requirements:
- Return 1 to 3 activities.
- Keep every activity grounded in the lesson analysis.
- Set `lesson_id` to match the lesson analysis.
- Set `object_role` on every activity:
  - `learning_note`
  - `activity_area`
  - `reference_material`
  - `worksheet`
  - `ai_courseware`
- Set `lesson_flow_stage` on every activity:
  - `before`
  - `during`
  - `after`
- Use `activity_type: "freeform_html"` unless there is a strong reason not to.
- Put the full standalone HTML document for the card in `html_content`.
- The HTML must be self-contained and ready for screenshot capture.
- Each activity must clearly act as `보완`, `심화`, or `확장`.
- Avoid simply copying the textbook's own question structure or swapping a few words from the textbook prompt.
- The card should open a different path toward the same learning goal.
- Use `NumbersDesign.md` this way:
  - treat it as a constraint and composition guide
  - do not merely restate one known template pattern
  - decide the card's object role first
  - decide whether it belongs to before-class, during-class, or after-class flow
  - design the structure around what students should actually do on the card
- Keep the outer page background transparent or white. Do not add a gray canvas behind the card.
- Increase vertical writing space so students can handwrite with Apple Pencil comfortably.
- Prefer card heights that feel roomy, not compact.
- When a card expects sustained handwriting, make at least one main writing region visibly large, usually `420px+`.
- Use object roles from `ACTIVITY_RULE.md` implicitly:
  - learning note
  - activity area
  - reference material
  - worksheet
  - AI-linked reflection or follow-up
- Use learning functions from `ACTIVITY_RULE.md` implicitly:
  - creative expression
  - reasoning / problem solving
  - foundational practice
- If you generate a note-style card, treat it as a place to organize what students heard during class.
- For note-style cards, prefer labels such as `수업시간에 들은 내용 정리`, `오늘 수업 핵심 정리`, `설명 들으며 메모한 내용`.
- If you generate a creative card, provide a light scaffold or example cue.
- If you generate a reasoning card, make the thinking steps writable.
- If you generate a practice card, provide enough repeated writing space.
- Keep prompts short enough to fit an iPad worksheet.
- Even when `html_content` defines the full layout, include `student_writing_zones` that describe the real writable regions.
- Make the intended student action obvious without relying on long explanation text.
- Avoid making all cards look like the same repeated badge + intro + three-box pattern.
- Good directions include:
  - applying the idea to a new real-life case
  - making a claim and supporting it with evidence
  - comparing two choices, media messages, systems, or viewpoints
  - redesigning, planning, or proposing a better action
  - connecting the lesson to the student's own experience or decision
- Weak directions include:
  - rewriting textbook definitions
  - copying textbook diagrams into empty boxes
  - asking for an answer that is already directly printed on the textbook page
- The example above is only a shape contract.
- Do not copy its topic, wording, colors, or exact structure.
- Output a single JSON object only.
