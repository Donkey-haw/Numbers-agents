# Runtime Agent Spec: verify_agent

아래 AGENT.md는 이 단계의 역할과 경계를 정의한다.
문서에 적힌 역할만 수행하고, 하지 말아야 할 일은 넘지 마라.
출력 형식 요구가 있으면 반드시 지켜라.

# verify_agent

## identity
- status: active
- layer: verification
- implementation: `scripts/verify_agent.py`

## responsibility
- 최종 `.numbers` 출력이 존재하고 기본 검증을 통과하는지 확인한다.

## inputs
- required:
  - `output/<final>.numbers`

## outputs
- `output/verify.status.json`
- `output/verify_rule_review.json`
- `output/verify_review.json`

## allowed_tools
- local:
  - file existence check
  - verification rule checks
- model:
  - Gemini sidecar review

## allowed_actions
- 최종 output 존재 여부 검증
- verification status 기록
- 최종 run 상태 요약

## forbidden_actions
- Numbers 파일 재조합
- upstream 산출물 수정
- AI review로 최종 파일 생성/수정

## rules
- final output verification은 반드시 이 Agent를 통해서만 수행한다.

## hook_contract
- trigger_if_missing:
  - `output/verify.status.json`
- unlocks:
  - run finalization

## success_criteria
- `verify.status.json` 상태가 `succeeded`다.
- 최종 `.numbers` 파일이 존재한다.

## failure_modes
- output file 누락
- verification rule 실패
- AI sidecar review 실패


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
/Users/jonyeock/Desktop/Tool/NumbersAuto/artifacts/runs/social_6_1_unit4_globe_world-20260331-005325/output/사회_지구본과_지도로_보는_세계.numbers

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
        "/Users/jonyeock/Desktop/Tool/NumbersAuto/artifacts/runs/social_6_1_unit4_globe_world-20260331-005325/output/사회_지구본과_지도로_보는_세계.numbers"
      ]
    }
  ],
  "blocking_issues": [],
  "warnings": []
}

Run manifest summary:
{
  "run_id": "social_6_1_unit4_globe_world-20260331-005325",
  "final_status": "success",
  "selected_unit": "사회_지구본과_지도로_보는_세계",
  "stage_summary": [
    {
      "stage": "document_inventory_agent",
      "status": "succeeded",
      "fallback_used": false,
      "warning_count": 0,
      "error_count": 0,
      "details": {}
    },
    {
      "stage": "pdf_extract_agent",
      "status": "succeeded",
      "fallback_used": false,
      "warning_count": 0,
      "error_count": 0,
      "details": {}
    },
    {
      "stage": "page_index_agent",
      "status": "succeeded",
      "fallback_used": false,
      "warning_count": 0,
      "error_count": 0,
      "details": {}
    },
    {
      "stage": "schedule_parse_agent",
      "status": "succeeded",
      "fallback_used": false,
      "warning_count": 0,
      "error_count": 0,
      "details": {}
    },
    {
      "stage": "lesson_query_agent",
      "status": "succeeded",
      "fallback_used": false,
      "warning_count": 0,
      "error_count": 0,
      "details": {}
    },
    {
      "stage": "page_candidate_agent",
      "status": "succeeded",
      "fallback_used": false,
      "warning_count": 0,
      "error_count": 0,
      "details": {}
    },
    {
      "stage": "boundary_decision_agent",
      "status": "succeeded_with_warning",
      "fallback_used": false,
      "warning_count": 1,
      "error_count": 0,
      "details": {}
    },
    {
      "stage": "boundary_validation_agent",
      "status": "succeeded_with_warning",
      "fallback_used": false,
      "warning_count": 7,
      "error_count": 0,
      "details": {}
    },
    {
      "stage": "source_boundary_agent",
      "status": "succeeded_with_warning",
      "fallback_used": false,
      "warning_count": 7,
      "error_count": 0,
      "details": {}
    },
    {
      "stage": "source_validation_agent",
      "status": "succeeded_with_warning",
      "fallback_used": false,
      "warning_count": 12,
      "error_count": 0,
      "details": {}
    },
    {
      "stage": "lesson_analysis_agent",
      "status": "succeeded_with_warning",
      "fallback_used": true,
      "warning_count": 5,
      "error_count": 0,
      "details": {
        "fallback_category_counts": {
          "timeout": 5
        }
      }
    },
    {
      "stage": "lesson_review_agent",
      "status": "succeeded_with_warning",
      "fallback_used": false,
      "warning_count": 4,
      "error_count": 0,
      "details": {}
    },
    {
      "stage": "activity_plan_agent",
      "status": "succeeded_with_warning",
      "fallback_used": true,
      "warning_count": 5,
      "error_count": 0,
      "details": {
        "fallback_category_counts": {
          "timeout": 5
        }
      }
    },
    {
      "stage": "activity_review_agent",
      "status": "succeeded",
      "fallback_used": false,
      "warning_count": 0,
      "error_count": 0,
      "details": {}
    },
    {
      "stage": "html_card_agent",
      "status": "succeeded",
      "fallback_used": false,
      "warning_count": 0,
      "error_count": 0,
      "details": {}
    },
    {
      "stage": "capture_agent",
      "status": "succeeded",
      "fallback_used": false,
      "warning_count": 0,
      "error_count": 0,
      "details": {}
    },
    {
      "stage": "numbers_compose_agent",
      "status": "succeeded",
      "fallback_used": false,
      "warning_count": 0,
      "error_count": 0,
      "details": {}
    },
    {
      "stage": "review_manifest_agent",
      "status": "succeeded",
      "fallback_used": false,
      "warning_count": 0,
      "error_count": 0,
      "details": {}
    },
    {
      "stage": "verify_agent",
      "status": "succeeded_with_warning",
      "fallback_used": false,
      "warning_count": 1,
      "error_count": 0,
      "details": {}
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
