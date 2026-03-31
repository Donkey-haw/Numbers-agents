# Runtime Agent Spec: source_parse_agent

아래 AGENT.md는 이 단계의 역할과 경계를 정의한다.
문서에 적힌 역할만 수행하고, 하지 말아야 할 일은 넘지 마라.
출력 형식 요구가 있으면 반드시 지켜라.

# source_parse_agent

## 역할
- 입력 config를 실행 가능한 run config로 확정한다.
- 차시별 교과서/보조자료 페이지 범위를 결정한다.
- source 수준의 구조 검토 결과를 남긴다.

구현:
- `scripts/source_parse_agent.py`

## 입력
- `configs/<config>.json`
- 필요 시 진도표 원본 경로
- 교과서 PDF 및 보조자료 PDF

## 출력
- `source/schedule_draft.json`
- `source/textbook_context.json`
- `source/runtime_config.json`
- `source/config_quality_review.json`
- `source/boundary_review.json`
- `source/supplement_review.json`
- `source/source_ai_review.json`
- `source/source_parse.status.json`

## 내부 책임
- `generate_numbers_lesson.py`를 사용해 source range를 확정한다.
- 과목별 멀티리소스 기본 정책을 적용할 수 있다.
- `title_query`, `end_before_query`, topic intro signal을 바탕으로 경계를 계산한다.
- source 품질, 경계 모호성, 보조자료 매칭 결과를 review JSON으로 남긴다.
- 그 다음 `AGENT.md` 기반 AI review를 sidecar로 실행해 전체 source 상태를 사후 검토한다.

## 성공 조건
- `runtime_config.json`이 생성된다.
- 각 section에 `source_ranges`가 존재한다.
- `source_parse.status.json`이 `succeeded` 또는 `succeeded_with_warning`다.

## 차단 조건
- `sections`가 비어 있다.
- 어떤 차시에도 textbook source가 없다.
- 필수 source가 매칭되지 않는다.
- `source_ranges`가 비어 있다.

## 하지 말아야 할 일
- lesson 의미 분석을 수행하지 않는다.
- activity를 생성하지 않는다.
- Gemini에 초기 경계 결정을 위임하지 않는다.
- AI review가 source_ranges를 다시 계산하거나 수정해서는 안 된다.

## 테스트 방법
```bash
python3 scripts/pipeline_orchestrator.py \
  --config configs/<config>.json \
  --stop-after source_parse_agent \
  --keep-run-artifacts
```

## 확인 포인트
- `config_quality_review.json`에서 구조 문제 확인
- `boundary_review.json`에서 경계 근거와 다중 매칭 확인
- `supplement_review.json`에서 보조자료 매칭 여부 확인
- `source_ai_review.json`에서 AI 종합 판정 확인


# Execution Task

너의 역할은 source parsing 결과를 사후 검토하는 review-only agent다.
페이지 경계나 source_ranges를 다시 계산하거나 수정하지 마라.
아래 deterministic review 결과를 종합해 최종 review_result JSON 하나만 반환하라.
마크다운, 설명문, 코드블록, 접두어 없이 JSON object 하나만 반환하라.
최상단 문자와 마지막 문자는 반드시 중괄호여야 한다.
결정은 pass, pass_with_warning, needs_revision, blocked 중 하나여야 한다.
stage는 review_source_ai_agent로 써라.
status는 succeeded, succeeded_with_warning, blocked 중 하나로 맞춰라.
findings의 각 항목은 severity, message, evidence_refs만 가져야 한다.
불필요한 설명 없이 JSON만 반환하라.

Runtime config summary:
{
  "selected_unit": "6-1-국어-1. 자신의 삶과 관련지어 읽어요",
  "resources": [
    {
      "resource_id": "main",
      "label": "교과서",
      "kind": "textbook",
      "pdf_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/textbook/국어/[국어]6_1_교과서.pdf"
    }
  ],
  "sections": [
    {
      "sheet_name": "1차시",
      "title": "배울 내용 살펴보기",
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
      ]
    },
    {
      "sheet_name": "2-3차시",
      "title": "전기문을 읽고 인물이 추구하는 가치 알기",
      "source_ranges": [
        {
          "resource_id": "main",
          "role": "textbook",
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
    },
    {
      "sheet_name": "4-6차시",
      "title": "작품을 읽고 시대적 상황과 인물이 추구하는 가치에 대하여 질문하기",
      "source_ranges": [
        {
          "resource_id": "main",
          "role": "textbook",
          "pdf_pages": [
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
            26
          ]
        }
      ]
    },
    {
      "sheet_name": "7-8차시",
      "title": "인물이 추구하는 가치를 자신의 삶과 관련짓기",
      "source_ranges": [
        {
          "resource_id": "main",
          "role": "textbook",
          "pdf_pages": [
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
            38
          ]
        }
      ]
    },
    {
      "sheet_name": "9-11차시",
      "title": "작품을 읽고 독서 감상문 쓰기",
      "source_ranges": [
        {
          "resource_id": "main",
          "role": "textbook",
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
        }
      ]
    },
    {
      "sheet_name": "12-13차시",
      "title": "배운 내용 실천하기",
      "source_ranges": [
        {
          "resource_id": "main",
          "role": "textbook",
          "pdf_pages": [
            49,
            50
          ]
        }
      ]
    },
    {
      "sheet_name": "14차시",
      "title": "마무리하기",
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
      ]
    }
  ]
}

Config quality review:
{
  "schema_version": "1.0.0",
  "stage": "review_source_config",
  "lesson_id": null,
  "status": "succeeded",
  "decision": "pass",
  "findings": [],
  "blocking_issues": [],
  "warnings": []
}

Boundary review:
{
  "schema_version": "1.0.0",
  "stage": "review_source_boundary",
  "lesson_id": null,
  "status": "succeeded",
  "decision": "pass",
  "findings": [],
  "blocking_issues": [],
  "warnings": [],
  "entries": [
    {
      "lesson_id": "1차시",
      "resource_id": "main",
      "role": "textbook",
      "title_query": "배울 내용 살펴보기",
      "start_page": 1,
      "end_page": 4,
      "start_match_pages": [
        1
      ],
      "start_match_count": 1,
      "end_strategy": "explicit_pages",
      "end_reference_query": null,
      "intro_boundary_page": null,
      "status": "matched"
    },
    {
      "lesson_id": "2-3차시",
      "resource_id": "main",
      "role": "textbook",
      "title_query": "전기문을 읽고 인물이 추구하는 가치 알기",
      "start_page": 5,
      "end_page": 14,
      "start_match_pages": [
        5
      ],
      "start_match_count": 1,
      "end_strategy": "explicit_pages",
      "end_reference_query": null,
      "intro_boundary_page": null,
      "status": "matched"
    },
    {
      "lesson_id": "4-6차시",
      "resource_id": "main",
      "role": "textbook",
      "title_query": "작품을 읽고 시대적 상황과 인물이 추구하는 가치에 대하여 질문하기",
      "start_page": 15,
      "end_page": 26,
      "start_match_pages": [
        15
      ],
      "start_match_count": 1,
      "end_strategy": "explicit_pages",
      "end_reference_query": null,
      "intro_boundary_page": null,
      "status": "matched"
    },
    {
      "lesson_id": "7-8차시",
      "resource_id": "main",
      "role": "textbook",
      "title_query": "인물이 추구하는 가치를 자신의 삶과 관련짓기",
      "start_page": 27,
      "end_page": 38,
      "start_match_pages": [
        27
      ],
      "start_match_count": 1,
      "end_strategy": "explicit_pages",
      "end_reference_query": null,
      "intro_boundary_page": null,
      "status": "matched"
    },
    {
      "lesson_id": "9-11차시",
      "resource_id": "main",
      "role": "textbook",
      "title_query": "작품을 읽고 독서 감상문 쓰기",
      "start_page": 39,
      "end_page": 48,
      "start_match_pages": [
        39
      ],
      "start_match_count": 1,
      "end_strategy": "explicit_pages",
      "end_reference_query": null,
      "intro_boundary_page": null,
      "status": "matched"
    },
    {
      "lesson_id": "12-13차시",
      "resource_id": "main",
      "role": "textbook",
      "title_query": "배운 내용 실천하기",
      "start_page": 49,
      "end_page": 50,
      "start_match_pages": [
        49
      ],
      "start_match_count": 1,
      "end_strategy": "explicit_pages",
      "end_reference_query": null,
      "intro_boundary_page": null,
      "status": "matched"
    },
    {
      "lesson_id": "14차시",
      "resource_id": "main",
      "role": "textbook",
      "title_query": "마무리하기",
      "start_page": 51,
      "end_page": 54,
      "start_match_pages": [
        51
      ],
      "start_match_count": 1,
      "end_strategy": "explicit_pages",
      "end_reference_query": null,
      "intro_boundary_page": null,
      "status": "matched"
    }
  ]
}

Supplement review:
{
  "schema_version": "1.0.0",
  "stage": "review_source_supplement",
  "lesson_id": null,
  "status": "succeeded",
  "decision": "pass",
  "findings": [],
  "blocking_issues": [],
  "warnings": [],
  "entries": []
}

Schema:
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://numbersauto.local/schemas/review_result.schema.json",
  "title": "Review Result",
  "type": "object",
  "required": [
    "schema_version",
    "stage",
    "status",
    "decision",
    "findings",
    "blocking_issues",
    "warnings"
  ],
  "properties": {
    "schema_version": {
      "type": "string"
    },
    "stage": {
      "type": "string"
    },
    "lesson_id": {
      "type": ["string", "null"]
    },
    "status": {
      "type": "string",
      "enum": [
        "pending",
        "running",
        "succeeded",
        "succeeded_with_warning",
        "failed",
        "failed_fallback_used",
        "blocked"
      ]
    },
    "decision": {
      "type": "string",
      "enum": ["pass", "pass_with_warning", "needs_revision", "blocked"]
    },
    "findings": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["severity", "message", "evidence_refs"],
        "properties": {
          "severity": {
            "type": "string",
            "enum": ["info", "warning", "error"]
          },
          "message": {
            "type": "string"
          },
          "evidence_refs": {
            "type": "array",
            "items": {
              "type": "string"
            }
          }
        },
        "additionalProperties": false
      }
    },
    "blocking_issues": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "warnings": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  },
  "additionalProperties": false
}
