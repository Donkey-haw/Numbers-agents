# Runtime Agent Spec: verify_agent

아래 AGENT.md는 이 단계의 역할과 경계를 정의한다.
문서에 적힌 역할만 수행하고, 하지 말아야 할 일은 넘지 마라.
출력 형식 요구가 있으면 반드시 지켜라.

# verify_agent

## 역할
- 최종 `.numbers` 출력이 존재하고 기본 검증을 통과하는지 확인한다.

구현:
- `scripts/verify_agent.py`

## 입력
- `output/<final>.numbers`

## 출력
- `output/verify.status.json`
- `output/verify_rule_review.json`
- `output/verify_review.json`

## 내부 책임
- 현재 config를 다시 읽어 최종 output 존재 여부를 검증한다.
- verification status를 기록한다.
- 그 다음 `AGENT.md` 기반 AI review를 sidecar로 실행해 최종 run 상태를 해석한다.

## 성공 조건
- `verify.status.json` 상태가 `succeeded`
- 최종 `.numbers`가 존재

## 하지 말아야 할 일
- Numbers 파일을 다시 조합하지 않는다.
- upstream 산출물을 수정하지 않는다.
- AI review가 최종 파일을 다시 생성하거나 수정해서는 안 된다.

## 테스트 방법
```bash
python3 scripts/pipeline_orchestrator.py \
  --config configs/<config>.json \
  --stop-after verify_agent \
  --keep-run-artifacts
```

## 확인 포인트
- `verify.status.json`
- `verify_rule_review.json`
- `verify_review.json`
- output 경로 실제 존재 여부


# Execution Task

너의 역할은 최종 verify 결과를 사후 검토하는 review-only agent다.
파일을 수정하거나 다시 생성하지 마라.
review_result JSON 하나만 반환하라.
마크다운, 설명문, 코드블록 없이 JSON object 하나만 반환하라.
stage는 review_verify_agent로 써라.
decision은 pass, pass_with_warning, needs_revision, blocked 중 하나여야 한다.
status는 succeeded, succeeded_with_warning, blocked 중 하나여야 한다.
findings의 각 항목은 severity, message, evidence_refs만 가져야 한다.

Final output path:
/Users/jonyeock/Desktop/Tool/NumbersAuto/artifacts/runs/korean_6_1_unit1_related_to_life_reading-20260326-220856/output/6-1-국어-1. 자신의 삶과 관련지어 읽어요.numbers

Rule review:
{
  "schema_version": "1.0.0",
  "stage": "review_verify_rule_agent",
  "lesson_id": null,
  "status": "succeeded",
  "decision": "pass",
  "findings": [
    {
      "severity": "info",
      "message": "최종 Numbers 파일이 생성되어 있습니다.",
      "evidence_refs": [
        "/Users/jonyeock/Desktop/Tool/NumbersAuto/artifacts/runs/korean_6_1_unit1_related_to_life_reading-20260326-220856/output/6-1-국어-1. 자신의 삶과 관련지어 읽어요.numbers"
      ]
    }
  ],
  "blocking_issues": [],
  "warnings": []
}

Run manifest summary:
{
  "run_id": "korean_6_1_unit1_related_to_life_reading-20260326-220856",
  "final_status": "pending",
  "selected_unit": "6-1-국어-1. 자신의 삶과 관련지어 읽어요",
  "stage_summary": [
    {
      "stage": "source_parse_agent",
      "status": "succeeded",
      "fallback_used": false,
      "warning_count": 0,
      "error_count": 0
    },
    {
      "stage": "lesson_analysis_agent",
      "status": "failed_fallback_used",
      "fallback_used": true,
      "warning_count": 1,
      "error_count": 1
    },
    {
      "stage": "review_lesson_agent",
      "status": "succeeded_with_warning",
      "fallback_used": false,
      "warning_count": 1,
      "error_count": 0
    },
    {
      "stage": "activity_plan_agent",
      "status": "failed_fallback_used",
      "fallback_used": true,
      "warning_count": 0,
      "error_count": 1
    },
    {
      "stage": "review_activity_agent",
      "status": "succeeded",
      "fallback_used": false,
      "warning_count": 0,
      "error_count": 0
    },
    {
      "stage": "html_card_agent",
      "status": "succeeded",
      "fallback_used": false,
      "warning_count": 0,
      "error_count": 0
    },
    {
      "stage": "capture_agent",
      "status": "succeeded",
      "fallback_used": false,
      "warning_count": 0,
      "error_count": 0
    },
    {
      "stage": "numbers_compose_agent",
      "status": "succeeded",
      "fallback_used": false,
      "warning_count": 0,
      "error_count": 0
    },
    {
      "stage": "review_manifest_agent",
      "status": "succeeded",
      "fallback_used": false,
      "warning_count": 0,
      "error_count": 0
    },
    {
      "stage": "verify_agent",
      "status": "pending",
      "fallback_used": false,
      "warning_count": 0,
      "error_count": 0
    }
  ]
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
