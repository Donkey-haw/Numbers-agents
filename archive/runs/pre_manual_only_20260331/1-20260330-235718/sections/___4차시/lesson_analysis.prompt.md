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
  "sheet_name": "4차시",
  "card_file": "___4차시",
  "title": "지구본과 지도로 보는 세계 — 디지털 공간 영상 정보의 의미 알아보기",
  "badge": "4차시",
  "accent": [
    "#d97706",
    "#f59e0b"
  ],
  "sources": [
    {
      "resource_id": "main",
      "role": "textbook",
      "title_query": "지구본과 지도로 보는 세계 — 디지털 공간 영상 정보의 의미 알아보기",
      "_inference": {
        "status": "matched",
        "start_page": 116,
        "end_page": 116,
        "start_query": "지구본과 지도로 보는 세계 — 디지털 공간 영상 정보의 의미 알아보기",
        "start_match_pages": [
          116,
          118,
          119,
          150,
          151
        ],
        "start_match_count": 5,
        "end_strategy": "boundary_decision_agent",
        "end_reference_query": null,
        "intro_boundary_page": null,
        "reason": "Transitional heuristic: choose highest-ranked candidate and cut before next lesson candidate",
        "confidence": 0.45
      },
      "pdf_pages": [
        116
      ]
    }
  ],
  "source_ranges": [
    {
      "resource_id": "main",
      "role": "textbook",
      "pdf_pages": [
        116
      ]
    }
  ],
  "pdf_pages": [
    116
  ]
}

Baseline lesson analysis:
{
  "schema_version": "1.0.0",
  "generated_at": "2026-03-30T14:57:49.100520+00:00",
  "lesson_id": "4차시",
  "sheet_name": "4차시",
  "lesson_title": "지구본과 지도로 보는 세계 — 디지털 공간 영상 정보의 의미 알아보기",
  "lesson_type": "core",
  "pdf_pages": [
    116
  ],
  "essential_question": "지구본과 지도로 보는 세계 — 디지털 공간 영상 정보의 의미 알아보기",
  "learning_goals": [
    "지구본과 지도로 보는 세계 — 디지털 공간 영상 정보의 의미 알아보기의 핵심 내용을 설명할 수 있다."
  ],
  "key_concepts": [
    "지구본",
    "지도",
    "보는",
    "세계",
    "디지털"
  ],
  "vocabulary": [
    "지구본",
    "지도",
    "보는"
  ],
  "misconceptions": [],
  "difficulty_band": "on-level",
  "content_chunks": [
    {
      "chunk_id": "4차시-chunk-1",
      "label": "학습 덩어리 1",
      "content_type": "mixed",
      "knowledge_type": "concept",
      "summary": "아시아 대한 민국 대한 민국 아시아 태 평 양 동해 황해 남해 3D 레이어 역사적인 이미지 지구의 과거 모습을 담은 이미지를 확인해 보세요.",
      "source_pages": [
        116
      ],
      "suggested_activity_types": [
        "see_think_wonder",
        "learning_note",
        "worksheet"
      ]
    }
  ],
  "source_page_refs": [
    116
  ],
  "analysis_confidence": 0.75,
  "review_status": "draft",
  "notes": "자동 생성 초안. lesson title, key concepts, chunks를 검토 후 승인 필요."
}

Schedule draft:
{
  "schema_version": "1.0.0",
  "generated_at": "2026-03-30T14:57:25.043936+00:00",
  "sections": [
    {
      "sheet_name": "1차시",
      "lesson_title": "1단원 도입 — [단원 도입] 우리 친구는 누구?",
      "title_query": "1단원 도입 — [단원 도입] 우리 친구는 누구?"
    },
    {
      "sheet_name": "2차시",
      "lesson_title": "평화 통일을 위한 노력 — 분단으로 나타난 문제점과 분단이 사회와 생활 에 끼친 영향 알아보기",
      "title_query": "평화 통일을 위한 노력 — 분단으로 나타난 문제점과 분단이 사회와 생활 에 끼친 영향 알아보기"
    },
    {
      "sheet_name": "3차시",
      "lesson_title": "평화 통일을 위한 노력 — 분단의 흔적이 남아 있는 장소 알아보기",
      "title_query": "평화 통일을 위한 노력 — 분단의 흔적이 남아 있는 장소 알아보기"
    },
    {
      "sheet_name": "4차시",
      "lesson_title": "평화 통일을 위한 노력 — 분단의 장소가 평화의 장소로 바뀐 사례 알아보기",
      "title_query": "평화 통일을 위한 노력 — 분단의 장소가 평화의 장소로 바뀐 사례 알아보기"
    },
    {
      "sheet_name": "5-6차시",
      "lesson_title": "평화 통일을 위한 노력 — 평화 통일을 위한 노력 살펴보기",
      "title_query": "평화 통일을 위한 노력 — 평화 통일을 위한 노력 살펴보기"
    },
    {
      "sheet_name": "7차시",
      "lesson_title": "민주화와 산업화로 달라진 생활 문화 — [주제 도입] 열려라 이야기 / 외쳐라 빙고",
      "title_query": "민주화와 산업화로 달라진 생활 문화 — [주제 도입] 열려라 이야기 / 외쳐라 빙고"
    },
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
    },
    {
      "sheet_name": "12-13차시",
      "lesson_title": "민주화와 산업화로 달라진 생활 문화 — 산업화로 달라진 사회와 생활 문화 이해하기",
      "title_query": "민주화와 산업화로 달라진 생활 문화 — 산업화로 달라진 사회와 생활 문화 이해하기"
    },
    {
      "sheet_name": "14차시",
      "lesson_title": "1단원 정리 — [단원 마무리] 나만의 누리집 완성하기 / 창의·융 합 사고력 쑥쑥",
      "title_query": "1단원 정리 — [단원 마무리] 나만의 누리집 완성하기 / 창의·융 합 사고력 쑥쑥"
    },
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
    },
    {
      "sheet_name": "4-5차시",
      "lesson_title": "민주주의와 선거 — 우리나라의 선거 과정 살펴보기",
      "title_query": "민주주의와 선거 — 우리나라의 선거 과정 살펴보기"
    },
    {
      "sheet_name": "6-7차시",
      "lesson_title": "민주주의와 선거 — 선거에 적극적으로 참여해야 하는 까닭 알아보기",
      "title_query": "민주주의와 선거 — 선거에 적극적으로 참여해야 하는 까닭 알아보기"
    },
    {
      "sheet_name": "8차시",
      "lesson_title": "국가기관이 하는 일 — [주제 도입] 열려라 이야기 / 외쳐라 빙고",
      "title_query": "국가기관이 하는 일 — [주제 도입] 열려라 이야기 / 외쳐라 빙고"
    },
    {
      "sheet_name": "9-10차시",
      "lesson_title": "국가기관이 하는 일 — 국회의 구성과 하는 일 파악하기",
      "title_query": "국가기관이 하는 일 — 국회의 구성과 하는 일 파악하기"
    },
    {
      "sheet_name": "11차시",
      "lesson_title": "국가기관이 하는 일 — 행정부의 구성과 하는 일 파악하기",
      "title_query": "국가기관이 하는 일 — 행정부의 구성과 하는 일 파악하기"
    },
    {
      "sheet_name": "12차시",
      "lesson_title": "국가기관이 하는 일 — 법원의 구성과 하는 일 파악하기",
      "title_query": "국가기관이 하는 일 — 법원의 구성과 하는 일 파악하기"
    },
    {
      "sheet_name": "13차시",
      "lesson_title": "국가기관이 하는 일 — 권력 분립의 의미와 중요성 탐구하기",
      "title_query": "국가기관이 하는 일 — 권력 분립의 의미와 중요성 탐구하기"
    },
    {
      "sheet_name": "14차시",
      "lesson_title": "민주주의와 미디어 — [주제 도입] 열려라 이야기 / 외쳐라 빙고",
      "title_query": "민주주의와 미디어 — [주제 도입] 열려라 이야기 / 외쳐라 빙고"
    },
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
    },
    {
      "sheet_name": "19차시",
      "lesson_title": "2단원 정리 — [단원 마무리] 나만의 누리집 완성하기 / 창의·융 합 사고력 쑥쑥",
      "title_query": "2단원 정리 — [단원 마무리] 나만의 누리집 완성하기 / 창의·융 합 사고력 쑥쑥"
    },
    {
      "sheet_name": "1차시",
      "lesson_title": "3단원 도입 — [단원 도입] 우리 친구는 누구?",
      "title_query": "3단원 도입 — [단원 도입] 우리 친구는 누구?"
    },
    {
      "sheet_name": "2-3차시",
      "lesson_title": "지구본과 지도로 보는 세계 — 지구본의 특징 살펴보기",
      "title_query": "지구본과 지도로 보는 세계 — 지구본의 특징 살펴보기"
    },
    {
      "sheet_name": "4차시",
      "lesson_title": "지구본과 지도로 보는 세계 — 디지털 공간 영상 정보의 의미 알아보기",
      "title_query": "지구본과 지도로 보는 세계 — 디지털 공간 영상 정보의 의미 알아보기"
    },
    {
      "sheet_name": "5차시",
      "lesson_title": "지구본과 지도로 보는 세계 — 위도와 위선의 의미 알아보기",
      "title_query": "지구본과 지도로 보는 세계 — 위도와 위선의 의미 알아보기"
    },
    {
      "sheet_name": "6차시",
      "lesson_title": "지구본과 지도로 보는 세계 — 경도와 경선의 의미 알아보기",
      "title_query": "지구본과 지도로 보는 세계 — 경도와 경선의 의미 알아보기"
    },
    {
      "sheet_name": "7차시",
      "lesson_title": "지구본과 지도로 보는 세계 — 위도와 경도를 이용해 위치를 표현하는 방법 살 펴보기",
      "title_query": "지구본과 지도로 보는 세계 — 위도와 경도를 이용해 위치를 표현하는 방법 살 펴보기"
    },
    {
      "sheet_name": "8차시",
      "lesson_title": "세계의 대륙, 대양, 나라 — [주제 도입] 열려라 이야기 / 외쳐라 빙고",
      "title_query": "세계의 대륙, 대양, 나라 — [주제 도입] 열려라 이야기 / 외쳐라 빙고"
    },
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
    },
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
    },
    {
      "sheet_name": "15차시",
      "lesson_title": "3단원 정리 — [단원 마무리] 나만의 누리집 완성하기 / 창의·융 합 사고력 쑥쑥",
      "title_query": "3단원 정리 — [단원 마무리] 나만의 누리집 완성하기 / 창의·융 합 사고력 쑥쑥"
    }
  ]
}

Section context:
{
  "schema_version": "1.0.0",
  "generated_at": "2026-03-30T15:15:22.341017+00:00",
  "pdf_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/textbook/사회/[사회]6_1_교과서.pdf",
  "current_section": {
    "sheet_name": "4차시",
    "lesson_title": "평화 통일을 위한 노력 — 분단의 장소가 평화의 장소로 바뀐 사례 알아보기",
    "title_query": "평화 통일을 위한 노력 — 분단의 장소가 평화의 장소로 바뀐 사례 알아보기",
    "pdf_pages": [
      12
    ],
    "baseline_analysis_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/artifacts/runs/1-20260330-235718/source/local_baseline/___4차시.lesson_analysis.json",
    "extracted_text": "1\n평화 통일을 \n위한 노력\n 분단으로 생겨난 문제점과 평화 통일의 필요성을 설명할 수 있어요.\n 분단과 관련된 장소를 평화의 장소로 만들려는 노력을 찾아볼 수 있어요.\n 평화 통일을 위해 우리가 할 수 있는 일을 탐색할 수 있어요.\n이 주제를 배우면 나는\n이 산책로에 있는\n푯말은 무엇을 의미할까?\n1\n10\n1 평화 통일을 위한 노력, 민주화와 산업화"
  },
  "neighbor_sections": [
    {
      "relation": "previous",
      "sheet_name": "3차시",
      "lesson_title": "평화 통일을 위한 노력 — 분단의 흔적이 남아 있는 장소 알아보기",
      "title_query": "평화 통일을 위한 노력 — 분단의 흔적이 남아 있는 장소 알아보기",
      "pdf_pages": [
        16
      ]
    },
    {
      "relation": "next",
      "sheet_name": "5-6차시",
      "lesson_title": "평화 통일을 위한 노력 — 평화 통일을 위한 노력 살펴보기",
      "title_query": "평화 통일을 위한 노력 — 평화 통일을 위한 노력 살펴보기",
      "pdf_pages": [
        10,
        11,
        12
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
