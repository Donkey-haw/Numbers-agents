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
  "lesson_id": "12-13차시",
  "sheet_name": "12-13차시",
  "lesson_title": "배운 내용 실천하기",
  "lesson_type": "core",
  "pdf_pages": [
    49,
    50
  ],
  "essential_question": "인물이 추구하는 가치가 잘 드러나게 인물을 소개하고, 작품에서 배운 가치를 우리 삶 속에서 어떻게 실천할 수 있을까?",
  "learning_goals": [
    "인물이 추구하는 가치가 드러나게 인물을 소개하는 자료를 만들고 친구들에게 발표할 수 있다.",
    "작품을 통해 배운 가치를 실천하기 위한 활동을 계획하고 적극적으로 참여할 수 있다."
  ],
  "key_concepts": [
    "인물 소개",
    "가치 실천",
    "소개 자료 제작",
    "발표",
    "활동 소감"
  ],
  "vocabulary": [
    "실천",
    "가치",
    "본받다",
    "소개",
    "추구"
  ],
  "misconceptions": [
    "인물 소개는 단순한 인물 정보나 사건의 나열이다.",
    "가치 실천은 거창하고 어려운 일로만 생각한다."
  ],
  "content_chunks": [
    {
      "chunk_id": "12-13차시-chunk-1",
      "label": "인물 소개 자료 만들고 발표하기",
      "knowledge_type": "procedure",
      "summary": "친구들에게 소개하고 싶은 인물을 선택하여, 선택한 까닭과 가치가 잘 드러나는 장면 등을 포함한 소개 자료(글, 광고지, 동영상 등)를 만들고 계획에 따라 발표한다.",
      "source_pages": [
        49
      ]
    },
    {
      "chunk_id": "12-13차시-chunk-2",
      "label": "배운 내용 실천하기",
      "knowledge_type": "application",
      "summary": "우리가 정한 활동(개인, 짝, 모둠 등)을 바탕으로 인물이 추구하는 가치를 실제 활동으로 실천해보고 그 소감을 나눈다.",
      "source_pages": [
        50
      ]
    }
  ],
  "source_page_refs": [
    49,
    50
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
