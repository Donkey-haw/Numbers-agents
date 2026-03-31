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
  "sheet_name": "10차시",
  "card_file": "___10차시",
  "title": "민주화와 산업화로 달라진 생활 문화 — 대통령 직선제와 지방 자치제의 부활 이해하기",
  "badge": "10차시",
  "pdf_pages": [
    29
  ],
  "textbook_source": {
    "resource_id": "main",
    "title_query": "민주화와 산업화로 달라진 생활 문화 — 대통령 직선제와 지방 자치제의 부활 이해하기",
    "start_page": 29,
    "end_page": 29,
    "confidence": 0.45,
    "status": "matched"
  }
}

Baseline lesson analysis:
{
  "lesson_id": "10차시",
  "sheet_name": "10차시",
  "lesson_title": "민주화와 산업화로 달라진 생활 문화 — 대통령 직선제와 지방 자치제의 부활 이해하기",
  "lesson_type": "core",
  "pdf_pages": [
    29
  ],
  "essential_question": "민주화와 산업화로 달라진 생활 문화 — 대통령 직선제와 지방 자치제의 부활 이해하기",
  "learning_goals": [
    "민주화와 산업화로 달라진 생활 문화 — 대통령 직선제와 지방 자치제의 부활 이해하기의 핵심 내용을 설명할 수 있다."
  ],
  "key_concepts": [
    "민주화",
    "산업화",
    "달라진",
    "생활",
    "문화"
  ],
  "vocabulary": [
    "민주화",
    "산업화",
    "달라진"
  ],
  "misconceptions": [],
  "difficulty_band": "on-level",
  "content_chunks": [
    {
      "chunk_id": "10차시-chunk-1",
      "label": "학습 덩어리 1",
      "knowledge_type": "concept",
      "summary": "민주화 산업화 생활 문화 4.19 혁명 5.18 민주화 운동 6월 민주 항쟁 지방 자치제 시민 의식 중화학 공업 생태환경 경제성장 시민운동 직선제 독재 경공업 1 낱말 구름을 보고, 이 주제에서 배울 내용이 무엇인지 생각해 봅시다.",
      "source_pages": [
        29
      ]
    }
  ],
  "source_page_refs": [
    29
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
      "sheet_name": "8-9차시",
      "lesson_title": "민주화와 산업화로 달라진 생활 문화 — 4·19 혁명 이해하기",
      "title_query": "민주화와 산업화로 달라진 생활 문화 — 4·19 혁명 이해하기"
    },
    {
      "sheet_name": "10차시",
      "lesson_title": "민주화와 산업화로 달라진 생활 문화 — 대통령 직선제와 지방 자치제의 부활 이해하기",
      "title_query": "민주화와 산업화로 달라진 생활 문화 — 대통령 직선제와 지방 자치제의 부활 이해하기"
    },
    {
      "sheet_name": "11차시",
      "lesson_title": "민주화와 산업화로 달라진 생활 문화 — 산업화 과정 이해하기",
      "title_query": "민주화와 산업화로 달라진 생활 문화 — 산업화 과정 이해하기"
    }
  ]
}

Section context:
{
  "schema_version": "1.0.0",
  "generated_at": "2026-03-30T15:19:53.496508+00:00",
  "pdf_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/textbook/사회/[사회]6_1_교과서.pdf",
  "current_section": {
    "section_key": "___10차시__민주화와_산업화로_달라진_생활_문화___대통령_직선제와_지방_자치제의_부활_이해하기",
    "sheet_name": "10차시",
    "lesson_title": "민주화와 산업화로 달라진 생활 문화 — 대통령 직선제와 지방 자치제의 부활 이해하기",
    "title_query": "민주화와 산업화로 달라진 생활 문화 — 대통령 직선제와 지방 자치제의 부활 이해하기",
    "pdf_pages": [
      29
    ],
    "baseline_analysis_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/artifacts/runs/1-20260331-001652/source/local_baseline/___10차시__민주화와_산업화로_달라진_생활_문화___대통령_직선제와_지방_자치제의_부활_이해하기.lesson_analysis.json",
    "extracted_text": "민주화\n산업화\n생활 문화\n4.19 혁명\n5.18 민주화 운동\n6월 민주 항쟁\n  지방 자치제\n시민 의식\n중화학 공업\n생태환경\n경제성장\n시민운동\n직선제\n독재\n경공업\n1  낱말 구름을 보고, 이 주제에서 배울 내용이 무엇인지 생각해 봅시다.\n2  낱말 구름에 있는 낱말 9개를 골라서 빙고 놀이를 해 봅시다.\n우리나라에 \n본격적으로 컴퓨터가\n보급된 시기는 언제일까?\n2\n27\n2   민주화와 산업화로 달라진 생활 문화",
    "extracted_text_truncated": false
  },
  "neighbor_sections": [
    {
      "relation": "previous",
      "section_key": "___8-9차시__민주화와_산업화로_달라진_생활_문화___4_19_혁명_이해하기",
      "sheet_name": "8-9차시",
      "lesson_title": "민주화와 산업화로 달라진 생활 문화 — 4·19 혁명 이해하기",
      "title_query": "민주화와 산업화로 달라진 생활 문화 — 4·19 혁명 이해하기",
      "pdf_pages": [
        29
      ]
    },
    {
      "relation": "next",
      "section_key": "___11차시__민주화와_산업화로_달라진_생활_문화___산업화_과정_이해하기",
      "sheet_name": "11차시",
      "lesson_title": "민주화와 산업화로 달라진 생활 문화 — 산업화 과정 이해하기",
      "title_query": "민주화와 산업화로 달라진 생활 문화 — 산업화 과정 이해하기",
      "pdf_pages": [
        10
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
