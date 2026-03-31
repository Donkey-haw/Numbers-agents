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
  "title": "세계의 대륙, 대양, 나라 — 아시아 주요 나라들의 위치 알아보기",
  "badge": "10차시",
  "pdf_pages": [
    131
  ],
  "textbook_source": {
    "resource_id": "main",
    "title_query": "세계의 대륙, 대양, 나라 — 아시아 주요 나라들의 위치 알아보기",
    "start_page": 131,
    "end_page": 131,
    "confidence": 0.45,
    "status": "matched"
  }
}

Baseline lesson analysis:
{
  "lesson_id": "10차시",
  "sheet_name": "10차시",
  "lesson_title": "세계의 대륙, 대양, 나라 — 아시아 주요 나라들의 위치 알아보기",
  "lesson_type": "core",
  "pdf_pages": [
    131
  ],
  "essential_question": "세계의 대륙, 대양, 나라 — 아시아 주요 나라들의 위치 알아보기",
  "learning_goals": [
    "세계의 대륙, 대양, 나라 — 아시아 주요 나라들의 위치 알아보기의 핵심 내용을 설명할 수 있다."
  ],
  "key_concepts": [
    "세계",
    "대륙",
    "대양",
    "아시아",
    "주요"
  ],
  "vocabulary": [
    "세계",
    "대륙",
    "대양"
  ],
  "misconceptions": [],
  "difficulty_band": "on-level",
  "content_chunks": [
    {
      "chunk_id": "10차시-chunk-1",
      "label": "학습 덩어리 1",
      "knowledge_type": "concept",
      "summary": "옳은 문장의 번호를 순서대로 써서 우주의 여행 준비물을 챙겨 봅시다.",
      "source_pages": [
        131
      ]
    }
  ],
  "source_page_refs": [
    131
  ],
  "analysis_confidence": 0.75,
  "notes": "자동 생성 초안. lesson title, key concepts, chunks를 검토 후 승인 필요."
}

Schedule draft:
{
  "schema_version": "1.0.0",
  "generated_at": "2026-03-30T15:14:42.342846+00:00",
  "sections": [
    {
      "sheet_name": "9차시",
      "lesson_title": "세계의 대륙, 대양, 나라 — 우리나라의 위치 특징 파악하기",
      "title_query": "세계의 대륙, 대양, 나라 — 우리나라의 위치 특징 파악하기"
    },
    {
      "sheet_name": "10차시",
      "lesson_title": "세계의 대륙, 대양, 나라 — 아시아 주요 나라들의 위치 알아보기",
      "title_query": "세계의 대륙, 대양, 나라 — 아시아 주요 나라들의 위치 알아보기"
    },
    {
      "sheet_name": "11차시",
      "lesson_title": "세계의 대륙, 대양, 나라 — 유럽 주요 나라들의 위치 알아보기",
      "title_query": "세계의 대륙, 대양, 나라 — 유럽 주요 나라들의 위치 알아보기"
    }
  ]
}

Section context:
{
  "schema_version": "1.0.0",
  "generated_at": "2026-03-30T15:35:13.556210+00:00",
  "pdf_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/textbook/사회/[사회]6_1_교과서.pdf",
  "current_section": {
    "section_key": "___10차시__세계의_대륙__대양__나라___아시아_주요_나라들의_위치_알아보기",
    "sheet_name": "10차시",
    "lesson_title": "세계의 대륙, 대양, 나라 — 아시아 주요 나라들의 위치 알아보기",
    "title_query": "세계의 대륙, 대양, 나라 — 아시아 주요 나라들의 위치 알아보기",
    "pdf_pages": [
      131
    ],
    "baseline_analysis_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/artifacts/runs/1-20260331-001435/source/local_baseline/___10차시__세계의_대륙__대양__나라___아시아_주요_나라들의_위치_알아보기.lesson_analysis.json",
    "extracted_text": "옳은 문장의 번호를 순서대로 써서 우주의 여행 준비물을 챙겨 봅시다.\n이번 주제에서 배운 내용을 정리하며 우리가 행복이를 만날 수 있는 길을 찾아봅시다.\n1  ‌\u0007세계지도는 세계 여러 나라의 위치, 거리, 영토 모양 등을 비교적 \n정확하게 나타낼 수 있다.\n2  ‌\u0007지구본은 세계 여러 나라의 위치와 영역을 한눈에 살펴볼 수 \n있다.\n3  ‌\u0007디지털 공간 영상 정보를 활용하면 세계에 관한 다양한 정보를 \n얻을 수 있다.\n4  ‌\u0007북반구와 남반구는 계절이 반대로 나타난다.\n5  경도에 따라 지역 간 시차가 생긴다.\n6  ‌\u0007위치는 위도로만 나타낼 수 있다.\n주제마무리\n되돌아가기를 만나면 교과서를 살펴본 후 처음부터 시작합니다.\n112~119쪽\n120~127쪽\n128~130쪽\n1.\t\u0007세계를 표현하는 다양한 공간 자료의 특징을 설명할 \n수 있나요?\n\t\n예 \n \n\t\n아니요 \n \n2.\t\u0007다양한 공간 자료를 활용해 세계의 기초적인 지리 \n정보를 찾을 수 있나요?\n\t\n예 \n \n\t\n아니요 \n \n3.\t\u0007위도와 경도의 의미를 이해하고, 이를 활용해 위치\n를 표현할 수 있나요?\n\t\n예 \n \n\t\n아니요 \n \n요약 정리\n131\n1   지구본과 지도로 보는 세계",
    "extracted_text_truncated": false
  },
  "neighbor_sections": [
    {
      "relation": "previous",
      "section_key": "___9차시__세계의_대륙__대양__나라___우리나라의_위치_특징_파악하기",
      "sheet_name": "9차시",
      "lesson_title": "세계의 대륙, 대양, 나라 — 우리나라의 위치 특징 파악하기",
      "title_query": "세계의 대륙, 대양, 나라 — 우리나라의 위치 특징 파악하기",
      "pdf_pages": [
        128,
        129,
        130
      ]
    },
    {
      "relation": "next",
      "section_key": "___11차시__세계의_대륙__대양__나라___유럽_주요_나라들의_위치_알아보기",
      "sheet_name": "11차시",
      "lesson_title": "세계의 대륙, 대양, 나라 — 유럽 주요 나라들의 위치 알아보기",
      "title_query": "세계의 대륙, 대양, 나라 — 유럽 주요 나라들의 위치 알아보기",
      "pdf_pages": [
        128,
        129,
        130
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
