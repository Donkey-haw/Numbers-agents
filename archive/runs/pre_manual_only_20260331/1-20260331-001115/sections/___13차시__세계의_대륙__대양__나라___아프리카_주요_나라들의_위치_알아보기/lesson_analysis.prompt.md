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
  "sheet_name": "13차시",
  "card_file": "___13차시",
  "title": "세계의 대륙, 대양, 나라 — 아프리카 주요 나라들의 위치 알아보기",
  "badge": "13차시",
  "accent": [
    "#4f46e5",
    "#7c3aed"
  ],
  "sources": [
    {
      "resource_id": "main",
      "role": "textbook",
      "title_query": "세계의 대륙, 대양, 나라 — 아프리카 주요 나라들의 위치 알아보기",
      "_inference": {
        "status": "matched",
        "start_page": 131,
        "end_page": 131,
        "start_query": "세계의 대륙, 대양, 나라 — 아프리카 주요 나라들의 위치 알아보기",
        "start_match_pages": [
          131,
          132,
          133,
          145,
          147
        ],
        "start_match_count": 5,
        "end_strategy": "boundary_decision_agent",
        "end_reference_query": null,
        "intro_boundary_page": null,
        "reason": "Transitional heuristic: choose highest-ranked candidate and cut before next lesson candidate",
        "confidence": 0.45
      },
      "pdf_pages": [
        131
      ]
    }
  ],
  "source_ranges": [
    {
      "resource_id": "main",
      "role": "textbook",
      "pdf_pages": [
        131
      ]
    }
  ],
  "pdf_pages": [
    131
  ]
}

Baseline lesson analysis:
{
  "lesson_id": "13차시",
  "sheet_name": "13차시",
  "lesson_title": "세계의 대륙, 대양, 나라 — 아프리카 주요 나라들의 위치 알아보기",
  "lesson_type": "core",
  "pdf_pages": [
    131
  ],
  "essential_question": "세계의 대륙, 대양, 나라 — 아프리카 주요 나라들의 위치 알아보기",
  "learning_goals": [
    "세계의 대륙, 대양, 나라 — 아프리카 주요 나라들의 위치 알아보기의 핵심 내용을 설명할 수 있다."
  ],
  "key_concepts": [
    "세계",
    "대륙",
    "대양",
    "아프리카",
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
      "chunk_id": "13차시-chunk-1",
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
  "generated_at": "2026-03-30T15:11:22.756492+00:00",
  "sections": [
    {
      "sheet_name": "12차시",
      "lesson_title": "세계의 대륙, 대양, 나라 — 북아메리카와 남아메리카 주요 나라들의 위치 알아보기",
      "title_query": "세계의 대륙, 대양, 나라 — 북아메리카와 남아메리카 주요 나라들의 위치 알아보기"
    },
    {
      "sheet_name": "13차시",
      "lesson_title": "세계의 대륙, 대양, 나라 — 아프리카 주요 나라들의 위치 알아보기",
      "title_query": "세계의 대륙, 대양, 나라 — 아프리카 주요 나라들의 위치 알아보기"
    },
    {
      "sheet_name": "14차시",
      "lesson_title": "세계의 대륙, 대양, 나라 — 오세아니아 주요 나라들의 위치 알아보기",
      "title_query": "세계의 대륙, 대양, 나라 — 오세아니아 주요 나라들의 위치 알아보기"
    }
  ]
}

Section context:
{
  "schema_version": "1.0.0",
  "generated_at": "2026-03-30T15:30:24.925807+00:00",
  "pdf_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/textbook/사회/[사회]6_1_교과서.pdf",
  "current_section": {
    "section_key": "___13차시__세계의_대륙__대양__나라___아프리카_주요_나라들의_위치_알아보기",
    "sheet_name": "13차시",
    "lesson_title": "세계의 대륙, 대양, 나라 — 아프리카 주요 나라들의 위치 알아보기",
    "title_query": "세계의 대륙, 대양, 나라 — 아프리카 주요 나라들의 위치 알아보기",
    "pdf_pages": [
      131
    ],
    "baseline_analysis_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/artifacts/runs/1-20260331-001115/source/local_baseline/___13차시__세계의_대륙__대양__나라___아프리카_주요_나라들의_위치_알아보기.lesson_analysis.json",
    "extracted_text": "옳은 문장의 번호를 순서대로 써서 우주의 여행 준비물을 챙겨 봅시다.\n이번 주제에서 배운 내용을 정리하며 우리가 행복이를 만날 수 있는 길을 찾아봅시다.\n1  ‌\u0007세계지도는 세계 여러 나라의 위치, 거리, 영토 모양 등을 비교적 \n정확하게 나타낼 수 있다.\n2  ‌\u0007지구본은 세계 여러 나라의 위치와 영역을 한눈에 살펴볼 수 \n있다.\n3  ‌\u0007디지털 공간 영상 정보를 활용하면 세계에 관한 다양한 정보를 \n얻을 수 있다.\n4  ‌\u0007북반구와 남반구는 계절이 반대로 나타난다.\n5  경도에 따라 지역 간 시차가 생긴다.\n6  ‌\u0007위치는 위도로만 나타낼 수 있다.\n주제마무리\n되돌아가기를 만나면 교과서를 살펴본 후 처음부터 시작합니다.\n112~119쪽\n120~127쪽\n128~130쪽\n1.\t\u0007세계를 표현하는 다양한 공간 자료의 특징을 설명할 \n수 있나요?\n\t\n예 \n \n\t\n아니요 \n \n2.\t\u0007다양한 공간 자료를 활용해 세계의 기초적인 지리 \n정보를 찾을 수 있나요?\n\t\n예 \n \n\t\n아니요 \n \n3.\t\u0007위도와 경도의 의미를 이해하고, 이를 활용해 위치\n를 표현할 수 있나요?\n\t\n예 \n \n\t\n아니요 \n \n요약 정리\n131\n1   지구본과 지도로 보는 세계",
    "extracted_text_truncated": false
  },
  "neighbor_sections": [
    {
      "relation": "previous",
      "section_key": "___12차시__세계의_대륙__대양__나라___북아메리카와_남아메리카_주요_나라들의_위치_알아보기",
      "sheet_name": "12차시",
      "lesson_title": "세계의 대륙, 대양, 나라 — 북아메리카와 남아메리카 주요 나라들의 위치 알아보기",
      "title_query": "세계의 대륙, 대양, 나라 — 북아메리카와 남아메리카 주요 나라들의 위치 알아보기",
      "pdf_pages": [
        131
      ]
    },
    {
      "relation": "next",
      "section_key": "___14차시__세계의_대륙__대양__나라___오세아니아_주요_나라들의_위치_알아보기",
      "sheet_name": "14차시",
      "lesson_title": "세계의 대륙, 대양, 나라 — 오세아니아 주요 나라들의 위치 알아보기",
      "title_query": "세계의 대륙, 대양, 나라 — 오세아니아 주요 나라들의 위치 알아보기",
      "pdf_pages": [
        131
      ]
    }
  ]
}

Target schema:
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://numbersauto.local/schemas/lesson_analysis.schema.json",
  "title": "Lesson Analysis",
  "type": "object",
  "required": [
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
  "properties": {
    "schema_version": {
      "type": "string"
    },
    "generated_at": {
      "type": "string",
      "format": "date-time"
    },
    "lesson_id": {
      "type": "string"
    },
    "sheet_name": {
      "type": "string"
    },
    "lesson_title": {
      "type": "string"
    },
    "lesson_type": {
      "type": "string",
      "enum": ["intro", "core", "review", "summary", "mixed"]
    },
    "pdf_pages": {
      "type": "array",
      "items": {
        "type": "integer",
        "minimum": 1
      },
      "minItems": 1
    },
    "essential_question": {
      "type": "string"
    },
    "learning_goals": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "minItems": 1
    },
    "key_concepts": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "minItems": 1
    },
    "vocabulary": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "misconceptions": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "difficulty_band": {
      "type": "string",
      "enum": ["core", "on-level", "extension", "mixed"]
    },
    "content_chunks": {
      "type": "array",
      "items": {
        "type": "object",
        "required": [
          "chunk_id",
          "label",
          "content_type",
          "knowledge_type",
          "summary",
          "source_pages"
        ],
        "properties": {
          "chunk_id": {
            "type": "string"
          },
          "label": {
            "type": "string"
          },
          "content_type": {
            "type": "string",
            "enum": ["text", "image", "diagram", "map", "activity", "summary", "mixed"]
          },
          "knowledge_type": {
            "type": "string",
            "enum": ["fact", "concept", "procedure", "comparison", "cause-effect", "opinion", "application", "mixed"]
          },
          "summary": {
            "type": "string"
          },
          "source_pages": {
            "type": "array",
            "items": {
              "type": "integer",
              "minimum": 1
            },
            "minItems": 1
          },
          "suggested_activity_types": {
            "type": "array",
            "items": {
              "type": "string"
            }
          }
        },
        "additionalProperties": false
      }
    },
    "source_page_refs": {
      "type": "array",
      "items": {
        "type": "integer",
        "minimum": 1
      },
      "minItems": 1
    },
    "analysis_confidence": {
      "type": "number",
      "minimum": 0,
      "maximum": 1
    },
    "review_status": {
      "type": "string",
      "enum": ["draft", "reviewed", "approved", "rejected"]
    },
    "notes": {
      "type": "string"
    }
  },
  "additionalProperties": false
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
