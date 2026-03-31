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
  "lesson_id": "12-13차시",
  "sheet_name": "12-13차시",
  "lesson_title": "민주화와 산업화로 달라진 생활 문화 — 산업화로 달라진 사회와 생활 문화 이해하기",
  "lesson_type": "core",
  "pdf_pages": [
    10,
    11,
    12,
    13,
    14,
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
    26,
    27,
    28,
    29,
    30,
    31,
    32,
    33,
    34,
    35,
    36,
    37,
    38,
    39,
    40,
    41,
    42,
    43,
    44,
    45,
    46,
    47,
    48
  ],
  "essential_question": "남북 분단은 우리 삶에 어떤 영향을 미쳤으며, 산업화와 민주화 이후 우리의 생활 문화는 어떻게 달라졌을까?",
  "learning_goals": [
    "남북 분단으로 인해 발생하는 군사적, 사회적, 문화적 문제점을 설명할 수 있다.",
    "우리 주변에 남아 있는 분단의 흔적을 찾아보고 평화 통일의 필요성을 이해한다.",
    "산업화와 민주화 과정을 거치며 변화한 우리 사회의 생활 모습과 문화를 파악한다."
  ],
  "key_concepts": [
    "남북 분단",
    "평화 통일",
    "군사적 긴장",
    "문화 차이",
    "비무장 지대(DMZ)"
  ],
  "vocabulary": [
    "국방비",
    "이산가족",
    "북한 이탈 주민",
    "휴전선",
    "판문점",
    "용치",
    "방호벽",
    "경공업"
  ],
  "misconceptions": [
    "남북한의 언어와 문화 차이가 단순히 사투리 수준의 미미한 차이라고 오해할 수 있다.",
    "분단으로 인한 문제가 우리 일상생활과는 상관없는 군사적 영역에만 국한된다고 생각할 수 있다.",
    "산업화가 단순히 경제적인 성장만을 의미하며 생활 방식의 전반적인 변화를 포함한다는 점을 간과할 수 있다."
  ],
  "content_chunks": [
    {
      "chunk_id": "12-13차시-chunk-1",
      "label": "분단으로 생겨난 문제점",
      "knowledge_type": "cause-effect",
      "summary": "광복 후 한반도 분단과 6·25 전쟁 이후 고착화된 분단 상황에서 발생하는 군사적 긴장, 국방비 증가, 언어 및 생활 방식의 차이, 이산가족의 아픔 등 다양한 사회·문화적 문제점을 다룬다.",
      "source_pages": [
        12,
        13
      ]
    },
    {
      "chunk_id": "12-13차시-chunk-2",
      "label": "한반도 곳곳에 남은 분단의 흔적",
      "knowledge_type": "fact",
      "summary": "휴전선, 비무장 지대(DMZ), 판문점, 용치, 방호벽, 끊어진 철길(신탄리역 철도 중단점) 등 우리 주변에 여전히 남아 있는 분단의 아픈 흔적들을 시각 자료와 함께 살펴본다.",
      "source_pages": [
        14,
        15
      ]
    },
    {
      "chunk_id": "12-13차시-chunk-3",
      "label": "산업화와 민주화로 달라진 생활 문화",
      "knowledge_type": "comparison",
      "summary": "산업화 과정을 통해 발전한 경공업과 중화학 공업, 경제 성장과 더불어 시민 의식의 성장과 민주화 운동(4·19, 5·18, 6월 항쟁)이 우리 삶의 문화와 사회 구조를 어떻게 변화시켰는지 이해한다.",
      "source_pages": [
        29,
        30,
        31,
        32,
        33,
        34,
        35,
        36,
        37,
        38,
        39,
        40,
        41,
        42,
        43,
        44,
        45,
        46,
        47,
        48
      ]
    }
  ],
  "source_page_refs": [
    10,
    11,
    12,
    13,
    14,
    15,
    29,
    30,
    48
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
