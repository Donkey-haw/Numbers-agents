# Runtime Agent Spec: lesson_analysis_agent

아래 AGENT.md는 이 단계의 역할과 경계를 정의한다.
문서에 적힌 역할만 수행하고, 하지 말아야 할 일은 넘지 마라.
출력 형식 요구가 있으면 반드시 지켜라.

# lesson_analysis_agent

## identity
- status: active
- layer: generation
- implementation: `scripts/lesson_analysis_agent.py`

## responsibility
- 차시별 lesson analysis를 생성한다.
- 생성 결과를 정규화해 최종 `lesson_analysis.json`으로 확정한다.

## inputs
- required:
  - `source/schedule_draft.json`
  - `source/textbook_context.json`
- optional:
  - `source/local_baseline/<lesson>.lesson_analysis.json`

## outputs
- `sections/<lesson>/lesson_analysis.context.json`
- `sections/<lesson>/lesson_analysis.prompt.md`
- `sections/<lesson>/lesson_analysis_ai.json`
- `sections/<lesson>/lesson_analysis.json`
- `sections/<lesson>/lesson_analysis.status.json`

## allowed_tools
- local:
  - prompt/context assembly
  - JSON normalization
- model:
  - Gemini CLI

## allowed_actions
- lesson별 prompt 구성
- lesson analysis 생성
- baseline fallback 사용
- lesson 단위 병렬 실행

## forbidden_actions
- source 경계 수정
- activity 생성
- render/output 조작

## rules
- lesson semantic analysis generation은 반드시 이 Agent를 통해서만 수행한다.

## hook_contract
- trigger_if_missing:
  - `sections/<lesson>/lesson_analysis.json`
- unlocks:
  - `lesson_review_agent`
  - `activity_plan_agent`

## success_criteria
- 각 lesson에 `lesson_analysis.json`이 생성된다.
- lesson별 status file이 존재한다.

## failure_modes
- Gemini timeout
- AI JSON 생성 실패
- normalization 실패
- baseline fallback 사용


# Execution Task

You are helping a local textbook-to-Numbers pipeline.

Rules:
- Ignore progress-chart page numbers entirely.
- Treat the textbook PDF as the primary source of truth.
- Do not invent page boundaries.
- Return JSON only.
- Do not include markdown fences.
- Do not include fields outside the provided schema unless they already appear in the baseline object.
- If a value is uncertain, keep the baseline value or explain uncertainty in `notes`.
- Keep `review_status` as `draft`.
- Keep the output grounded in the supplied section context only.
- Do not infer details from other lessons unless they are explicitly included as neighboring boundary hints.


Generate one `lesson_analysis` JSON object for the section below.

Section:
{
  "sheet_name": "2차시",
  "card_file": "___2차시",
  "title": "민주주의와 선거 — 선거의 의미와 중요성 파악하기",
  "badge": "2차시",
  "pdf_pages": [
    54
  ],
  "textbook_source": {
    "resource_id": "main",
    "title_query": "민주주의와 선거 — 선거의 의미와 중요성 파악하기",
    "start_page": 54,
    "end_page": 54,
    "confidence": 0.45,
    "status": "matched"
  }
}

Baseline lesson analysis:
{
  "lesson_id": "2차시",
  "sheet_name": "2차시",
  "lesson_title": "민주주의와 선거 — 선거의 의미와 중요성 파악하기",
  "lesson_type": "core",
  "pdf_pages": [
    54
  ],
  "essential_question": "민주주의와 선거 — 선거의 의미와 중요성 파악하기",
  "learning_goals": [
    "민주주의와 선거 — 선거의 의미와 중요성 파악하기의 핵심 내용을 설명할 수 있다."
  ],
  "key_concepts": [
    "선거",
    "의미",
    "중요성",
    "파악하기",
    "파악할"
  ],
  "vocabulary": [
    "선거",
    "의미",
    "중요성"
  ],
  "misconceptions": [
    "선거를 단순히 사람을 뽑는 행사로만 이해할 수 있다.",
    "민주주의의 핵심이 참여보다 결과에만 있다고 오해할 수 있다."
  ],
  "difficulty_band": "on-level",
  "content_chunks": [
    {
      "chunk_id": "2차시-chunk-1",
      "label": "학습 덩어리 1",
      "knowledge_type": "procedure",
      "summary": "사람들이 몸으로 만든 저 모양은 무엇을 의미하는 걸까?",
      "source_pages": [
        54
      ]
    }
  ],
  "source_page_refs": [
    54
  ],
  "analysis_confidence": 0.75,
  "notes": "자동 생성 초안. lesson title, key concepts, chunks를 검토 후 승인 필요."
}

Schedule draft:
{
  "schema_version": "1.0.0",
  "generated_at": "2026-03-30T15:16:59.267020+00:00",
  "sections": [
    {
      "sheet_name": "1차시",
      "lesson_title": "2단원 도입 — [단원 도입] 우리 친구는 누구?",
      "title_query": "2단원 도입 — [단원 도입] 우리 친구는 누구?"
    },
    {
      "sheet_name": "2차시",
      "lesson_title": "민주주의와 선거 — 선거의 의미와 중요성 파악하기",
      "title_query": "민주주의와 선거 — 선거의 의미와 중요성 파악하기"
    },
    {
      "sheet_name": "3차시",
      "lesson_title": "민주주의와 선거 — 민주주의에서 선거의 역할 파악하기",
      "title_query": "민주주의와 선거 — 민주주의에서 선거의 역할 파악하기"
    }
  ]
}

Section context:
{
  "schema_version": "1.0.0",
  "generated_at": "2026-03-30T15:23:29.651732+00:00",
  "pdf_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/textbook/사회/[사회]6_1_교과서.pdf",
  "current_section": {
    "section_key": "___2차시__민주주의와_선거___선거의_의미와_중요성_파악하기",
    "sheet_name": "2차시",
    "lesson_title": "민주주의와 선거 — 선거의 의미와 중요성 파악하기",
    "title_query": "민주주의와 선거 — 선거의 의미와 중요성 파악하기",
    "pdf_pages": [
      54
    ],
    "baseline_analysis_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/artifacts/runs/1-20260331-001652/source/local_baseline/___2차시__민주주의와_선거___선거의_의미와_중요성_파악하기.lesson_analysis.json",
    "extracted_text": "사람들이\n몸으로 만든 저 모양은 무엇을\n의미하는 걸까?\n 민주주의에서 선거의 의미와 역할 및 중요성을 파악할 수 있어요.\n 민주 국가의 선거 과정과 선거 원칙을 파악할 수 있어요.\n 선거에 주체적으로 참여하는 태도를 지닐 수 있어요.\n이 주제를 배우면 나는\n민주주의와 선거\n1\n1\n54\n2 민주주의와 시민 참여",
    "extracted_text_truncated": false
  },
  "neighbor_sections": [
    {
      "relation": "previous",
      "section_key": "___1차시__2단원_도입____단원_도입__우리_친구는_누구_",
      "sheet_name": "1차시",
      "lesson_title": "2단원 도입 — [단원 도입] 우리 친구는 누구?",
      "title_query": "2단원 도입 — [단원 도입] 우리 친구는 누구?",
      "pdf_pages": [
        4,
        5,
        6,
        7,
        8,
        9,
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
        48,
        49,
        50,
        51,
        52,
        53
      ]
    },
    {
      "relation": "next",
      "section_key": "___3차시__민주주의와_선거___민주주의에서_선거의_역할_파악하기",
      "sheet_name": "3차시",
      "lesson_title": "민주주의와 선거 — 민주주의에서 선거의 역할 파악하기",
      "title_query": "민주주의와 선거 — 민주주의에서 선거의 역할 파악하기",
      "pdf_pages": [
        54
      ]
    }
  ]
}

Target schema:
{
  "required_root_fields": [
    "schema_version",
    "generated_at",
    "lesson_id",
    "sheet_name",
    "lesson_title",
    "pdf_pages",
    "essential_question",
    "learning_goals",
    "key_concepts",
    "vocabulary",
    "misconceptions",
    "content_chunks",
    "source_page_refs",
    "analysis_confidence"
  ],
  "optional_root_fields": [
    "lesson_type",
    "difficulty_band",
    "review_status",
    "notes"
  ],
  "lesson_type_enum": [
    "intro",
    "core",
    "review",
    "summary",
    "mixed"
  ],
  "difficulty_band_enum": [
    "core",
    "on-level",
    "extension",
    "mixed"
  ],
  "review_status_enum": [
    "draft",
    "reviewed",
    "approved",
    "rejected"
  ],
  "required_content_chunk_fields": [
    "chunk_id",
    "label",
    "content_type",
    "knowledge_type",
    "summary",
    "source_pages"
  ],
  "content_type_enum": [
    "text",
    "image",
    "diagram",
    "map",
    "activity",
    "summary",
    "mixed"
  ],
  "knowledge_type_enum": [
    "fact",
    "concept",
    "procedure",
    "comparison",
    "cause-effect",
    "opinion",
    "application",
    "mixed"
  ],
  "constraints": {
    "pdf_pages_min_items": 1,
    "learning_goals_min_items": 1,
    "key_concepts_min_items": 1,
    "content_chunks_min_items": 1,
    "source_page_refs_min_items": 1,
    "analysis_confidence_range": [
      0,
      1
    ],
    "additional_properties": false
  }
}

Requirements:
- Preserve `sheet_name`, `lesson_id`, `lesson_title`, and `pdf_pages`.
- Improve `essential_question`, `learning_goals`, `key_concepts`, `vocabulary`, `misconceptions`, and `content_chunks` if the context supports it.
- `content_chunks` must stay grounded in the supplied `pdf_pages`.
- `source_page_refs` must match the actual section pages.
- Use `current_section.extracted_text` as the primary evidence.
- Use `neighbor_sections` only to avoid crossing lesson boundaries.
- Keep the result concise and classroom-usable.
- Output a single JSON object only.
