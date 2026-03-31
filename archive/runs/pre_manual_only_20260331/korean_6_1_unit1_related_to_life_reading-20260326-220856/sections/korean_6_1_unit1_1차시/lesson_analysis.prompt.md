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
  "sheet_name": "1차시",
  "card_file": "korean_6_1_unit1_1차시",
  "title": "배울 내용 살펴보기",
  "badge": "1차시",
  "accent": [
    "#0f766e",
    "#5eead4"
  ],
  "sources": [
    {
      "resource_id": "main",
      "role": "textbook",
      "pdf_pages": [
        1,
        2,
        3,
        4
      ],
      "title_query": "배울 내용 살펴보기"
    }
  ],
  "source_ranges": [
    {
      "resource_id": "main",
      "role": "textbook",
      "pdf_pages": [
        1,
        2,
        3,
        4
      ]
    }
  ],
  "pdf_pages": [
    1,
    2,
    3,
    4
  ]
}

Baseline lesson analysis:
{
  "schema_version": "1.0.0",
  "generated_at": "2026-03-26T13:08:56.289610+00:00",
  "lesson_id": "1차시",
  "sheet_name": "1차시",
  "lesson_title": "배울 내용 살펴보기",
  "lesson_type": "core",
  "pdf_pages": [
    1,
    2,
    3,
    4
  ],
  "essential_question": "배울 내용 살펴보기",
  "learning_goals": [
    "배울 내용 살펴보기의 핵심 내용을 설명할 수 있다."
  ],
  "key_concepts": [
    "배울",
    "살펴보기",
    "인물",
    "자신",
    "가치"
  ],
  "vocabulary": [
    "배울",
    "살펴보기",
    "인물"
  ],
  "misconceptions": [],
  "difficulty_band": "on-level",
  "content_chunks": [
    {
      "chunk_id": "1차시-chunk-1",
      "label": "학습 덩어리 1",
      "content_type": "mixed",
      "knowledge_type": "concept",
      "summary": "자신의 삶과 관련지어 읽어요 인물이 추구하는 가치를 이해하고 자신의 삶 되돌아보기1 인물이 추구하는 가치 파악하기 인물이 추구하는 가치를 자신과 관련지으며 독서 감상문 쓰기 1 2 문화 향유 역량 34 장영실은 사람들의 삶을 소중히 여겨서 해시계, 물",
      "source_pages": [
        1,
        2
      ],
      "suggested_activity_types": [
        "see_think_wonder",
        "learning_note",
        "worksheet"
      ]
    },
    {
      "chunk_id": "1차시-chunk-2",
      "label": "학습 덩어리 2",
      "content_type": "mixed",
      "knowledge_type": "concept",
      "summary": "작품 속 인물에 대해 경주가 쓴 독서 감상문을 읽고 물음에 답해 봅시다.",
      "source_pages": [
        3,
        4
      ],
      "suggested_activity_types": [
        "learning_note",
        "worksheet"
      ]
    }
  ],
  "source_page_refs": [
    1,
    2,
    3,
    4
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
  "generated_at": "2026-03-26T13:09:20.942157+00:00",
  "pdf_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/textbook/국어/[국어]6_1_교과서.pdf",
  "current_section": {
    "sheet_name": "1차시",
    "lesson_title": "배울 내용 살펴보기",
    "title_query": "배울 내용 살펴보기",
    "pdf_pages": [
      1,
      2,
      3,
      4
    ],
    "baseline_analysis_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/artifacts/runs/korean_6_1_unit1_related_to_life_reading-20260326-220856/source/local_baseline/korean_6_1_unit1_1차시.lesson_analysis.json",
    "extracted_text": "자신의 삶과\n관련지어 읽어요\n인물이 추구하는 가치를 이해하고\n자신의 삶 되돌아보기1\n인물이 추구하는 가치 파악하기\n인물이 추구하는 가치를 자신과 관련지으며\n독서 감상문 쓰기\n1\n2\n문화 향유 역량\n34\n\n장영실은 사람들의 삶을 소중히 \n여겨서 해시계, 물시계를 만들어 \n사람들을 편리하게 해 주었습니다.\n이 위인들은 무엇을 소중하게 \n생각하며 살았을까요?\n세종 대왕은 백성을 소중히 여겨서 \n훈민정음을 창제해 누구나 한글을 쓸 \n수 있도록 해 주었습니다.\n자신이 소중하게 생각하는 것은 무엇인가요?\n세종 대왕\n장영실\n준\n비\n준\n비\n배울 내용 \n배울 내용 \n각\n생\n열기\n35\n1\n\n작품 속 인물에 대해 경주가 쓴 독서 감상문을 읽고 물음에 답해 봅시다.\n1.\n(1)\u0001\t 경주가 읽은 책의 제목은 무엇인가요?\n(2)\t경주는 인물이 어떤 가치를 추구한다고 생각했나요?\n사람들이 자신의 삶에서 \n중요하게 여기는 것을 \n가치라고 해요. \n이야기 속에도 저마다의 \n가치를 추구하며 살아가는 \n인물이 등장해요.\n경주\n나는 전기문 『권기옥』을 읽었다. 권기옥은 \n우리나라 최초 여성 비행사이다. 일제 강점기에 \n조선 여성이 비행사가 된다는 것은 상상하기 어려운 \n일이었다. 그런데도 자신의 꿈을 이루려고 끝까지 \n노력하고 마침내 꿈을 이루어 낸 권기옥은 용기 \n있는 사람이다. \n배워요\n1.\t인물이 추구하는 가치 파악하기\n•\t \u0007전기문을 읽고 인물이 추구하는 \n가치 알기\n•\t \u0007작품을 읽고 인물이 추구하는 \n가치 질문하기\n이 단원에서는\n2.\t\u0007인물이 추구하는 가치를 자신과\b\n \n관련지으며 독서 감상문 쓰기\n•\t\u0007인물이 추구하는 가치를 자신의\b\n \n삶과 관련짓기\n•\t\u0007작품을 읽고 독서 감상문 쓰기\n36\n\n이야기 속 인물의 삶에서 영향받은 경험을 이야기해 봅시다. \n(1)\u0001\t 자신에게 영향을 준 이야기 속 인물을 떠올려 보세요.\n2.\n(2)\u0001\t이야기 속 인물이 자신에게 어떤 영향을 주었는지 친구들과 이야\n기해 보세요. \n「긴긴밤」의 주인공인 펭귄이 \n끝내 바다에 도착하는 모습을 \n보고 내가 추구하는 삶이 \n무엇인지 생각해 봤어. \n「나비를 잡는 아버지」의 \n주인공 바우와 바우 아버지를 \n보고 가족 간의 사랑이 얼마나 \n소중한지 알 수 있었어.\n \n이 단원에서 알고 싶은 내용을 빈칸에 써 보세요.\n알고 싶어요\n시대 상황 \n인물이 추구하는 가치\n독서 감상문 \n자신의 삶과\n관련지어 읽어요\n이야기 제목\n인물\n인물이 한 일\n37\n1"
  },
  "neighbor_sections": [
    {
      "relation": "next",
      "sheet_name": "2-3차시",
      "lesson_title": "전기문을 읽고 인물이 추구하는 가치 알기",
      "title_query": "전기문을 읽고 인물이 추구하는 가치 알기",
      "pdf_pages": [
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14
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
