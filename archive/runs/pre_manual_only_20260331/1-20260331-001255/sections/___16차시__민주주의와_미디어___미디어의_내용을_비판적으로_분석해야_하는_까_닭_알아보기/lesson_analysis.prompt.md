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
  "sheet_name": "16차시",
  "card_file": "___16차시",
  "title": "민주주의와 미디어 — 미디어의 내용을 비판적으로 분석해야 하는 까 닭 알아보기",
  "badge": "16차시",
  "pdf_pages": [
    90
  ],
  "textbook_source": {
    "resource_id": "main",
    "title_query": "민주주의와 미디어 — 미디어의 내용을 비판적으로 분석해야 하는 까 닭 알아보기",
    "start_page": 90,
    "end_page": 90,
    "confidence": 0.45,
    "status": "matched"
  }
}

Baseline lesson analysis:
{
  "lesson_id": "16차시",
  "sheet_name": "16차시",
  "lesson_title": "민주주의와 미디어 — 미디어의 내용을 비판적으로 분석해야 하는 까 닭 알아보기",
  "lesson_type": "core",
  "pdf_pages": [
    90
  ],
  "essential_question": "민주주의와 미디어 — 미디어의 내용을 비판적으로 분석해야 하는 까 닭 알아보기",
  "learning_goals": [
    "민주주의와 미디어 — 미디어의 내용을 비판적으로 분석해야 하는 까 닭 알아보기의 핵심 내용을 설명할 수 있다."
  ],
  "key_concepts": [
    "미디어",
    "비판적",
    "분석해야",
    "하는",
    "알아보기"
  ],
  "vocabulary": [
    "미디어",
    "비판적",
    "분석해야"
  ],
  "misconceptions": [
    "민주주의의 핵심이 참여보다 결과에만 있다고 오해할 수 있다."
  ],
  "difficulty_band": "on-level",
  "content_chunks": [
    {
      "chunk_id": "16차시-chunk-1",
      "label": "학습 덩어리 1",
      "knowledge_type": "concept",
      "summary": "영상이나 사진을 찍어 공유해 본 경험이 있니?",
      "source_pages": [
        90
      ]
    }
  ],
  "source_page_refs": [
    90
  ],
  "analysis_confidence": 0.75,
  "notes": "자동 생성 초안. lesson title, key concepts, chunks를 검토 후 승인 필요."
}

Schedule draft:
{
  "schema_version": "1.0.0",
  "generated_at": "2026-03-30T15:13:01.760315+00:00",
  "sections": [
    {
      "sheet_name": "15차시",
      "lesson_title": "민주주의와 미디어 — 미디어의 정보 제공 역할 알아보기",
      "title_query": "민주주의와 미디어 — 미디어의 정보 제공 역할 알아보기"
    },
    {
      "sheet_name": "16차시",
      "lesson_title": "민주주의와 미디어 — 미디어의 내용을 비판적으로 분석해야 하는 까 닭 알아보기",
      "title_query": "민주주의와 미디어 — 미디어의 내용을 비판적으로 분석해야 하는 까 닭 알아보기"
    },
    {
      "sheet_name": "17-18차시",
      "lesson_title": "민주주의와 미디어 — 미디어를 올바르게 이용하는 방법 알아보기",
      "title_query": "민주주의와 미디어 — 미디어를 올바르게 이용하는 방법 알아보기"
    }
  ]
}

Section context:
{
  "schema_version": "1.0.0",
  "generated_at": "2026-03-30T15:25:16.966649+00:00",
  "pdf_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/textbook/사회/[사회]6_1_교과서.pdf",
  "current_section": {
    "section_key": "___16차시__민주주의와_미디어___미디어의_내용을_비판적으로_분석해야_하는_까_닭_알아보기",
    "sheet_name": "16차시",
    "lesson_title": "민주주의와 미디어 — 미디어의 내용을 비판적으로 분석해야 하는 까 닭 알아보기",
    "title_query": "민주주의와 미디어 — 미디어의 내용을 비판적으로 분석해야 하는 까 닭 알아보기",
    "pdf_pages": [
      90
    ],
    "baseline_analysis_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/artifacts/runs/1-20260331-001255/source/local_baseline/___16차시__민주주의와_미디어___미디어의_내용을_비판적으로_분석해야_하는_까_닭_알아보기.lesson_analysis.json",
    "extracted_text": "영상이나 사진을 찍어\n공유해 본 경험이 있니?\n 민주주의에서 미디어의 의미와 역할을 이해할 수 있어요.\n 미디어의 내용을 비판적으로 분석하고 평가할 수 있어요.\n 미디어를 올바르게 이용하는 태도를 지닐 수 있어요.\n이 주제를 배우면 나는\n민주주의와 미디어\n3\n1\n90\n2 민주주의와 시민 참여",
    "extracted_text_truncated": false
  },
  "neighbor_sections": [
    {
      "relation": "previous",
      "section_key": "___15차시__민주주의와_미디어___미디어의_정보_제공_역할_알아보기",
      "sheet_name": "15차시",
      "lesson_title": "민주주의와 미디어 — 미디어의 정보 제공 역할 알아보기",
      "title_query": "민주주의와 미디어 — 미디어의 정보 제공 역할 알아보기",
      "pdf_pages": [
        83,
        84,
        85,
        86,
        87,
        88,
        89
      ]
    },
    {
      "relation": "next",
      "section_key": "___17-18차시__민주주의와_미디어___미디어를_올바르게_이용하는_방법_알아보기",
      "sheet_name": "17-18차시",
      "lesson_title": "민주주의와 미디어 — 미디어를 올바르게 이용하는 방법 알아보기",
      "title_query": "민주주의와 미디어 — 미디어를 올바르게 이용하는 방법 알아보기",
      "pdf_pages": [
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
        48
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
