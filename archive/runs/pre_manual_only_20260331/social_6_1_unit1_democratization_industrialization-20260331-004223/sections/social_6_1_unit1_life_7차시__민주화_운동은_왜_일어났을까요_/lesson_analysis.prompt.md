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
  "sheet_name": "7차시",
  "card_file": "social_6_1_unit1_life_7차시",
  "title": "민주화 운동은 왜 일어났을까요?",
  "badge": "7차시",
  "pdf_pages": [
    28
  ],
  "textbook_source": {
    "resource_id": "main",
    "title_query": "민주화 운동은 왜 일어났을까요?",
    "start_page": 28,
    "end_page": 28,
    "confidence": 0.45,
    "status": "matched"
  }
}

Baseline lesson analysis:
{
  "lesson_id": "7차시",
  "sheet_name": "7차시",
  "lesson_title": "민주화 운동은 왜 일어났을까요?",
  "lesson_type": "core",
  "pdf_pages": [
    28
  ],
  "essential_question": "민주화 운동은 왜 일어났을까요?",
  "learning_goals": [
    "민주화 운동은 왜 일어났을까요의 핵심 내용을 설명할 수 있다."
  ],
  "key_concepts": [
    "민주화",
    "운동",
    "일어났을까요",
    "산업화",
    "사람들"
  ],
  "vocabulary": [
    "민주화",
    "운동",
    "일어났을까요"
  ],
  "misconceptions": [],
  "difficulty_band": "on-level",
  "content_chunks": [
    {
      "chunk_id": "7차시-chunk-1",
      "label": "학습 덩어리 1",
      "knowledge_type": "concept",
      "summary": "2 민주화와 산업화로 달라진 생활 문화 민주화를 이루려는 다양한 분야 사람들의 노력을 설명할 수 있어요.",
      "source_pages": [
        28
      ]
    }
  ],
  "source_page_refs": [
    28
  ],
  "analysis_confidence": 0.75,
  "notes": "자동 생성 초안. lesson title, key concepts, chunks를 검토 후 승인 필요."
}

Schedule draft:
{
  "schema_version": "1.0.0",
  "generated_at": "2026-03-30T15:42:29.543220+00:00",
  "sections": [
    {
      "sheet_name": "7차시",
      "lesson_title": "민주화 운동은 왜 일어났을까요?",
      "title_query": "민주화 운동은 왜 일어났을까요?"
    },
    {
      "sheet_name": "8-9차시",
      "lesson_title": "민주화를 위한 노력을 살펴볼까요?",
      "title_query": "민주화를 위한 노력을 살펴볼까요?"
    }
  ]
}

Section context:
{
  "schema_version": "1.0.0",
  "generated_at": "2026-03-30T15:42:30.680004+00:00",
  "pdf_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/textbook/사회/[사회]6_1_교과서.pdf",
  "current_section": {
    "section_key": "social_6_1_unit1_life_7차시__민주화_운동은_왜_일어났을까요_",
    "sheet_name": "7차시",
    "lesson_title": "민주화 운동은 왜 일어났을까요?",
    "title_query": "민주화 운동은 왜 일어났을까요?",
    "pdf_pages": [
      28
    ],
    "baseline_analysis_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/artifacts/runs/social_6_1_unit1_democratization_industrialization-20260331-004223/source/local_baseline/social_6_1_unit1_life_7차시__민주화_운동은_왜_일어났을까요_.lesson_analysis.json",
    "extracted_text": "2\n민주화와 산업화로 \n달라진 생활 문화\n 민주화를 이루려는 다양한 분야 사람들의 노력을 설명할 수 있어요.\n 우리나라 산업화의 성과와 한계를 파악할 수 있어요.\n 민주화와 산업화로 달라진 사람들의 생활 모습과 문화를 이해할 수 있어요. \n이 주제를 배우면 나는\n사람들이 왜 촛불을 들고 \n광장에 모여 있을까?\n1\n26\n1 평화 통일을 위한 노력, 민주화와 산업화",
    "extracted_text_truncated": false
  },
  "neighbor_sections": [
    {
      "relation": "next",
      "section_key": "social_6_1_unit1_life_8-9차시__민주화를_위한_노력을_살펴볼까요_",
      "sheet_name": "8-9차시",
      "lesson_title": "민주화를 위한 노력을 살펴볼까요?",
      "title_query": "민주화를 위한 노력을 살펴볼까요?",
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
        27
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
