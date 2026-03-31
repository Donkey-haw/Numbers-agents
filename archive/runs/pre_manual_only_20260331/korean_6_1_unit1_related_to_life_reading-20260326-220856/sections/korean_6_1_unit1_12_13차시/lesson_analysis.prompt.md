# Runtime Agent Spec: lesson_analysis_agent

아래 AGENT.md는 이 단계의 역할과 경계를 정의한다.
문서에 적힌 역할만 수행하고, 하지 말아야 할 일은 넘지 마라.
출력 형식 요구가 있으면 반드시 지켜라.

# lesson_analysis_agent

## 역할
- 차시별 lesson analysis를 생성한다.
- Gemini 결과를 정규화해 최종 `lesson_analysis.json`으로 확정한다.
- 같은 단계 안에서 `review_lesson_agent` 산출물을 함께 만든다.

구현:
- `scripts/lesson_analysis_agent.py`

## 입력
- `source/schedule_draft.json`
- `source/textbook_context.json`
- `source/local_baseline/<lesson>.lesson_analysis.json`

## 출력
- `sections/<lesson>/lesson_analysis.context.json`
- `sections/<lesson>/lesson_analysis.prompt.md`
- `sections/<lesson>/lesson_analysis_ai.json`
- `sections/<lesson>/lesson_analysis.json`
- `sections/<lesson>/lesson_review.json`
- `sections/<lesson>/lesson_analysis.status.json`

## 내부 책임
- lesson별 prompt를 구성한다.
- Gemini를 호출해 lesson analysis를 생성한다.
- 실패 시 baseline analysis로 fallback한다.
- review 단계에서 최소 필수 필드와 경고를 기록한다.
- lesson 단위 병렬 실행을 지원한다.

## 성공 조건
- 각 lesson에 `lesson_analysis.json`이 생성된다.
- 각 lesson에 `lesson_review.json`이 생성된다.
- `lesson_analysis.status.json`이 lesson별로 존재한다.

## fallback
- Gemini timeout 또는 생성 실패 시 baseline analysis를 사용한다.
- fallback 여부는 `lesson_analysis.status.json`의 `fallback_used`와 `errors`에 남긴다.

## review_lesson_agent 내장 규칙
- `learning_goals` 필수
- `key_concepts` 필수
- `source_page_refs` 필수
- `misconceptions` 비어 있으면 warning

## 하지 말아야 할 일
- source 경계를 다시 바꾸지 않는다.
- activity를 생성하지 않는다.
- Numbers 배치를 다루지 않는다.

## 테스트 방법
```bash
python3 scripts/pipeline_orchestrator.py \
  --config configs/<config>.json \
  --stop-after review_lesson_agent \
  --keep-run-artifacts
```

## 확인 포인트
- `lesson_analysis.status.json`의 `fallback_used`
- `lesson_review.json`의 `decision`
- lesson별 prompt와 ai 결과 비교



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
  "sheet_name": "12-13차시",
  "card_file": "korean_6_1_unit1_12_13차시",
  "title": "배운 내용 실천하기",
  "badge": "12-13차시",
  "accent": [
    "#0f766e",
    "#99f6e4"
  ],
  "sources": [
    {
      "resource_id": "main",
      "role": "textbook",
      "pdf_pages": [
        49,
        50
      ],
      "title_query": "배운 내용 실천하기"
    }
  ],
  "source_ranges": [
    {
      "resource_id": "main",
      "role": "textbook",
      "pdf_pages": [
        49,
        50
      ]
    }
  ],
  "pdf_pages": [
    49,
    50
  ]
}

Baseline lesson analysis:
{
  "schema_version": "1.0.0",
  "generated_at": "2026-03-26T13:08:56.468496+00:00",
  "lesson_id": "12-13차시",
  "sheet_name": "12-13차시",
  "lesson_title": "배운 내용 실천하기",
  "lesson_type": "core",
  "pdf_pages": [
    49,
    50
  ],
  "essential_question": "배운 내용 실천하기",
  "learning_goals": [
    "배운 내용 실천하기의 핵심 내용을 설명할 수 있다."
  ],
  "key_concepts": [
    "배운",
    "실천하기",
    "인물",
    "추구하",
    "가치"
  ],
  "vocabulary": [
    "배운",
    "실천하기",
    "인물"
  ],
  "misconceptions": [],
  "difficulty_band": "on-level",
  "content_chunks": [
    {
      "chunk_id": "12-13차시-chunk-1",
      "label": "학습 덩어리 1",
      "content_type": "mixed",
      "knowledge_type": "concept",
      "summary": "인물이 추구하는 가치가 드러나게 인물 소개하기 배운 내용 실 이런 활동도 있어요 좋아하는 문학 작품 속 인물 소개하기 3 인물이 추구하는 가치가 드러나게 인물을 소개하는 자료 만들기 소개하는 글 광고지 동영상 기타: 5 반 친구들에게 인물을 소개하는 ",
      "source_pages": [
        49,
        50
      ],
      "suggested_activity_types": [
        "see_think_wonder",
        "learning_note",
        "worksheet"
      ]
    }
  ],
  "source_page_refs": [
    49,
    50
  ],
  "analysis_confidence": 0.75,
  "review_status": "draft",
  "notes": "자동 생성 초안. lesson title, key concepts, chunks를 검토 후 승인 필요."
}

Schedule draft:
{
  "schema_version": "1.0.0",
  "generated_at": "2026-03-26T13:08:56.230131+00:00",
  "sections": [
    {
      "sheet_name": "1차시",
      "lesson_title": "배울 내용 살펴보기",
      "title_query": "배울 내용 살펴보기"
    },
    {
      "sheet_name": "2-3차시",
      "lesson_title": "전기문을 읽고 인물이 추구하는 가치 알기",
      "title_query": "전기문을 읽고 인물이 추구하는 가치 알기"
    },
    {
      "sheet_name": "4-6차시",
      "lesson_title": "작품을 읽고 시대적 상황과 인물이 추구하는 가치에 대하여 질문하기",
      "title_query": "작품을 읽고 시대적 상황과 인물이 추구하는 가치에 대하여 질문하기"
    },
    {
      "sheet_name": "7-8차시",
      "lesson_title": "인물이 추구하는 가치를 자신의 삶과 관련짓기",
      "title_query": "인물이 추구하는 가치를 자신의 삶과 관련짓기"
    },
    {
      "sheet_name": "9-11차시",
      "lesson_title": "작품을 읽고 독서 감상문 쓰기",
      "title_query": "작품을 읽고 독서 감상문 쓰기"
    },
    {
      "sheet_name": "12-13차시",
      "lesson_title": "배운 내용 실천하기",
      "title_query": "배운 내용 실천하기"
    },
    {
      "sheet_name": "14차시",
      "lesson_title": "마무리하기",
      "title_query": "마무리하기"
    }
  ]
}

Section context:
{
  "schema_version": "1.0.0",
  "generated_at": "2026-03-26T13:10:59.509510+00:00",
  "pdf_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/textbook/국어/[국어]6_1_교과서.pdf",
  "current_section": {
    "sheet_name": "12-13차시",
    "lesson_title": "배운 내용 실천하기",
    "title_query": "배운 내용 실천하기",
    "pdf_pages": [
      49,
      50
    ],
    "baseline_analysis_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/artifacts/runs/korean_6_1_unit1_related_to_life_reading-20260326-220856/source/local_baseline/korean_6_1_unit1_12_13차시.lesson_analysis.json",
    "extracted_text": "인물이 추구하는 가치가 드러나게 인물 소개하기\n배운 내용 \n실\n이런 활동도 \n있어요\n좋아하는 문학 작품 속 인물 소개하기\n3 \t 인물이 추구하는 가치가 드러나게 인물을 소개하는 자료 만들기\n\t\n 소개하는 글  \n 광고지  \n 동영상  \n 기타:\n5 \t 반 친구들에게 인물을 소개하는 자료 발표하기 \n1 \u0007\t ‌\u0007문학 작품에 나오는 인물 가운데에서 친구들에게 소개할 인물 선택하기\n4 \t 발표할 내용 계획하기 \n●\u0007 책 제목과 작가:\n● 소개할 인물 이름: \n●\u0007 \n●\u0007  \n●\u0007 \n●\u0007  \n처음\n가운데\n끝\n2 \u0007\t 질문에 답하며 인물을 소개하는 자료에 넣을 내용 정하기\n● ‌\u0001이 인물을 선택한 까닭은 무엇인가요?\n● ‌\u0001인물이 추구하는 가치가 잘 드러나는 장면은 무엇인가요?\n● ‌\u0001인물을 보며 새롭게 안 점이나 본받고 싶은 점은 무엇인가요? \n책 제목\n인물 이름\n인물이 추구하는 가치\n82\n\n4\n 하고 싶은 활동 정하기\n인물이 추구하는\n가치가 드러나게 \n인물 소개하기\n 활동하기\n 활동 소감 나누기\n우리가 정한 활동을  \n반 전체가 할지, 모둠으로 할지, \n짝과 할지, 혼자 할지 정해요.\n83\n1"
  },
  "neighbor_sections": [
    {
      "relation": "previous",
      "sheet_name": "9-11차시",
      "lesson_title": "작품을 읽고 독서 감상문 쓰기",
      "title_query": "작품을 읽고 독서 감상문 쓰기",
      "pdf_pages": [
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
    },
    {
      "relation": "next",
      "sheet_name": "14차시",
      "lesson_title": "마무리하기",
      "title_query": "마무리하기",
      "pdf_pages": [
        51,
        52,
        53,
        54
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
