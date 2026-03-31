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
  "sheet_name": "14차시",
  "card_file": "korean_6_1_unit1_14차시",
  "title": "마무리하기",
  "badge": "14차시",
  "accent": [
    "#164e63",
    "#67e8f9"
  ],
  "sources": [
    {
      "resource_id": "main",
      "role": "textbook",
      "pdf_pages": [
        51,
        52,
        53,
        54
      ],
      "title_query": "마무리하기"
    }
  ],
  "source_ranges": [
    {
      "resource_id": "main",
      "role": "textbook",
      "pdf_pages": [
        51,
        52,
        53,
        54
      ]
    }
  ],
  "pdf_pages": [
    51,
    52,
    53,
    54
  ]
}

Baseline lesson analysis:
{
  "schema_version": "1.0.0",
  "generated_at": "2026-03-26T12:58:21.636416+00:00",
  "lesson_id": "14차시",
  "sheet_name": "14차시",
  "lesson_title": "마무리하기",
  "lesson_type": "core",
  "pdf_pages": [
    51,
    52,
    53,
    54
  ],
  "essential_question": "마무리하기",
  "learning_goals": [
    "마무리하기의 핵심 내용을 설명할 수 있다."
  ],
  "key_concepts": [
    "마무리하기",
    "추구하",
    "말하",
    "가치",
    "탐험"
  ],
  "vocabulary": [
    "마무리하기",
    "추구하",
    "말하"
  ],
  "misconceptions": [],
  "difficulty_band": "on-level",
  "content_chunks": [
    {
      "chunk_id": "14차시-chunk-1",
      "label": "학습 덩어리 1",
      "content_type": "mixed",
      "knowledge_type": "concept",
      "summary": "시에서 말하는 이가 추구하는 가치가 무엇인지 생각하며 「난 탐험가」를 읽어 봅시다.",
      "source_pages": [
        51,
        52
      ],
      "suggested_activity_types": [
        "see_think_wonder",
        "learning_note",
        "worksheet"
      ]
    },
    {
      "chunk_id": "14차시-chunk-2",
      "label": "학습 덩어리 2",
      "content_type": "mixed",
      "knowledge_type": "comparison",
      "summary": "이 단원에서 공부한 내용을 되돌아봅시다.",
      "source_pages": [
        53,
        54
      ],
      "suggested_activity_types": [
        "learning_note",
        "worksheet"
      ]
    }
  ],
  "source_page_refs": [
    51,
    52,
    53,
    54
  ],
  "analysis_confidence": 0.75,
  "review_status": "draft",
  "notes": "자동 생성 초안. lesson title, key concepts, chunks를 검토 후 승인 필요."
}

Schedule draft:
{
  "schema_version": "1.0.0",
  "generated_at": "2026-03-26T12:58:21.363022+00:00",
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
  "generated_at": "2026-03-26T13:00:03.436644+00:00",
  "pdf_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/textbook/국어/[국어]6_1_교과서.pdf",
  "current_section": {
    "sheet_name": "14차시",
    "lesson_title": "마무리하기",
    "title_query": "마무리하기",
    "pdf_pages": [
      51,
      52,
      53,
      54
    ],
    "baseline_analysis_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/artifacts/runs/korean_6_1_unit1_related_to_life_reading-20260326-215821/source/local_baseline/korean_6_1_unit1_14차시.lesson_analysis.json",
    "extracted_text": "시에서 말하는 이가 추구하는 가치가 무엇인지 생각하며 「난 탐험가」를 \n읽어 봅시다.\n1.\n마무리\n기\n실\n정리\n기\n난 탐험가\n글: 장세정, 그림: 손미현　 \n길 잃는 게 특기야\n오늘도 낯선 곳에서 길을 잃었어\n길 한가운데서\n코는 벌름대고\n눈은 빛나고\n손은 태양의 길이를 재고\n발은 짐승의 흔적을 찾고 있어\n길은 잃어도 마음속에선\n휘파람 소리가 나\n아직 길이 남아 있기 때문일 거야\n심장이 뛰는 소리를 느끼며 걷다 보면\n내가 길이 되기도 해\n불쑥불쑥 마주치는 것들이 알려 주었어 \n잃어버려야만 만날 수 있는 것들이 있다고 \n같이 놀다 보면 나름 재미있다고\n84\n\n「난 탐험가」를 읽고 물음에 답해 봅시다.\n(1)\u0001\t 시에서 말하는 이는 자신의 특기를 무엇이라고 했나요?\n(2)\u0001\t시에서 말하는 이가 “길은 잃어도 마음속에선 / 휘파람 소리가 나”\n라고 표현한 까닭은 무엇인가요? \n2.\n「난 탐험가」에서 말하는 이가 추구하는 가치가 무엇인지 알아봅시다.\n(1)\t 탐험가는 어떤 사람인가요? \n(2)\u0001\t시의 제목이 ‘난 탐험가’인 까닭은 무엇일까요? \n(3)\u0001\t시에서 말하는 이가 추구하는 가치는 무엇일지 친구들과 이야기해 \n보세요.\n3.\n자신만의 길을 찾으려는 \n모습을 보니 나다움을 \n중요하게 여기는 것 같아.\n \n85\n1\n\n이 단원에서 공부한 내용을 되돌아봅시다.\n(1)\u0001\t 공부한 내용 가운데에서 스스로 할 수 있게 된 활동의 정도를 점수로 \n나타내 보세요.\n(2)\u0001\t이 단원에서 공부한 내용을 생활에서 어떻게 실천할 수 있는지\u0001\n생각해 보세요.\n5\n5\n5\n5\n5\n4\n3 \n2\n1\n1\n1\n1\n1\n2\n2\n2\n2\n3\n3\n3\n3\n4\n4\n4\n4\n0\n전기문 속 인물이 \n추구하는 가치를 파악\n할 수 있다.\n인물이 추구하는 가\n치와 관련 있는 경험\n을 떠올릴 수 있다.\n인물이 추구하는 가\n치에 대한 자신의 생\n각을 말할 수 있다.\n자신이 추구하는 가치\n를 삶에서 실천하기 위해 \n노력할 일을 말할 수 있다.\n인물들이 추구하는 가\n치를 비교해 같은 점과 다\n른 점을 설명할 수 있다.\n매우 그렇다: 5, 그렇다: 4, 보통이다: 3, 그렇지 않다: 2, 매우 그렇지 않다: 1 \n스스로 \n인\n기\n86\n\n4\n교과 학습에 자주 나오는 낱말의 뜻을 알아봅시다.\n1.\n1에서 알아본 낱말의 뜻을 생각하며 문장을 만들어 봅시다. \n2.\n개선하다\n적용하다\n종합하다\n●\t\u0007여러 가지 생각이나 내용을 모아서 합할 때 ‘종합하다’를 \n써요.\n\t\n예 내용을 종합하다.\n\t\n 의견을 종합하다.\n여러 가지를 한데 모아서 합하다.\n종합하다\n●\t\u0007기준이나 원칙을 무엇에 맞추거나 쓸 때 ‘적용하다’를 써요.\n\t\n예 규칙을 적용하다.\n\t\n 배운 것을 적용하다.\n알맞게 이용하거나 맞추어 쓰다.\n적용하다\n●\t\u0007어떤 상황이나 상태를 현재보다 더 좋게 바꿀 때 ‘개선\u0001\n하다’를 써요.\n\t\n예 품질을 개선하다.\n\t\n 습관을 개선하다.\n잘못된 것이나 부족한 것, 나쁜 것을 고쳐 더 좋게 만들다.\n개선하다\n87\n1"
  },
  "neighbor_sections": [
    {
      "relation": "previous",
      "sheet_name": "12-13차시",
      "lesson_title": "배운 내용 실천하기",
      "title_query": "배운 내용 실천하기",
      "pdf_pages": [
        49,
        50
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
