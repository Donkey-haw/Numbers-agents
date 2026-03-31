# Runtime Agent Spec: activity_plan_agent

아래 AGENT.md는 이 단계의 역할과 경계를 정의한다.
문서에 적힌 역할만 수행하고, 하지 말아야 할 일은 넘지 마라.
출력 형식 요구가 있으면 반드시 지켜라.

# activity_plan_agent

## identity
- status: active
- layer: generation
- implementation: `scripts/activity_plan_agent.py`

## responsibility
- lesson analysis를 바탕으로 차시별 activity plan을 생성한다.
- 생성 결과를 정규화해 최종 `activity_plan.json`으로 확정한다.

## inputs
- required:
  - `sections/<lesson>/lesson_analysis.json`

## outputs
- `sections/<lesson>/activity_plan.prompt.md`
- `sections/<lesson>/activity_plan_ai.json`
- `sections/<lesson>/activity_plan.repair.prompt.md`
- `sections/<lesson>/activity_plan_ai_repair.json`
- `sections/<lesson>/activity_plan.json`
- `sections/<lesson>/activity_plan.status.json`

## allowed_tools
- local:
  - prompt assembly
  - local fallback builder
  - JSON normalization
- model:
  - Gemini CLI

## allowed_actions
- activity plan 생성
- repair prompt 재시도
- local fallback 사용
- lesson 단위 병렬 실행

## forbidden_actions
- source 경계 수정
- lesson analysis 수정
- HTML 렌더링 및 캡처
- Numbers 배치 제어

## rules
- activity plan generation은 반드시 이 Agent를 통해서만 수행한다.

## hook_contract
- trigger_if_missing:
  - `sections/<lesson>/activity_plan.json`
- unlocks:
  - `activity_review_agent`
  - `html_card_agent`

## success_criteria
- 각 lesson에 `activity_plan.json`이 생성된다.
- status에서 attempt, repair, fallback 여부가 기록된다.

## failure_modes
- Gemini timeout
- AI JSON 생성 실패
- repair 실패
- local fallback 사용


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
  "lesson_id": "3차시",
  "sheet_name": "3차시",
  "lesson_title": "평화 통일을 위한 노력 — 분단의 흔적이 남아 있는 장소 알아보기",
  "lesson_type": "core",
  "pdf_pages": [
    16
  ],
  "essential_question": "한반도 곳곳에는 어떤 분단의 흔적들이 남아 있으며, 이러한 흔적들이 우리에게 전하는 메시지는 무엇일까?",
  "learning_goals": [
    "한반도에 남아 있는 분단의 장소와 시설물을 찾아 그 의미를 설명할 수 있다.",
    "비무장 지대(DMZ), 판문점, 용치, 방호벽 등 분단의 상징적 장소와 시설물의 특징을 이해한다."
  ],
  "key_concepts": [
    "분단의 흔적",
    "비무장 지대(DMZ)",
    "군사 분계선(휴전선)",
    "판문점",
    "정전 협정"
  ],
  "vocabulary": [
    "비무장 지대(DMZ)",
    "용치",
    "방호벽",
    "아바이 마을",
    "공동 경비 구역"
  ],
  "misconceptions": [
    "분단의 흔적은 휴전선 부근에만 존재한다고 생각할 수 있으나, 속초의 아바이 마을처럼 후방 지역이나 일상 속에도 분단의 아픔이 서려 있음을 인지해야 함."
  ],
  "content_chunks": [
    {
      "chunk_id": "3차시-chunk-1",
      "label": "생각 깨우기: 아바이 마을",
      "knowledge_type": "fact",
      "summary": "강원특별자치도 속초시 아바이 마을의 명칭 유래를 통해 실향민의 아픔과 분단의 현실을 도입함.",
      "source_pages": [
        16
      ]
    },
    {
      "chunk_id": "3차시-chunk-2",
      "label": "분단의 상징적 장소",
      "knowledge_type": "concept",
      "summary": "군사 분계선, 비무장 지대(DMZ), 판문점(공동 경비 구역) 등 정전 협정 이후 형성된 대표적인 분단 장소를 살펴봄.",
      "source_pages": [
        16
      ]
    },
    {
      "chunk_id": "3차시-chunk-3",
      "label": "분단의 시설물과 흔적",
      "knowledge_type": "concept",
      "summary": "끊어진 철길(금강산 철교), 멈춰 선 기관차, 탱크 공격을 막기 위한 용치와 방호벽 등 물리적인 분단의 흔적을 조사함.",
      "source_pages": [
        16
      ]
    }
  ],
  "source_page_refs": [
    16
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
