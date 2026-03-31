# Runtime Agent Spec: review_manifest_agent

아래 AGENT.md는 이 단계의 역할과 경계를 정의한다.
문서에 적힌 역할만 수행하고, 하지 말아야 할 일은 넘지 마라.
출력 형식 요구가 있으면 반드시 지켜라.

# review_manifest_agent

## identity
- status: active
- layer: verification
- implementation: `scripts/review_manifest_agent.py`

## responsibility
- render manifest의 배치 논리를 사후 검토한다.
- 교과서 카드 우선 배치와 before/during/after 흐름을 확인한다.

## inputs
- required:
  - `render/render_manifest.json`

## outputs
- `render/manifest_review.json`
- `render/manifest_rule_review.json`

## allowed_tools
- local:
  - manifest rule checks
- model:
  - Gemini sidecar review

## allowed_actions
- sheet별 asset 존재 여부 확인
- textbook-first 규칙 확인
- activity flow 순서 확인
- sidecar review 생성

## forbidden_actions
- Numbers 파일 수정
- 자산 재생성
- AI review로 manifest 직접 수정

## rules
- render manifest review는 반드시 이 Agent를 통해서만 수행한다.

## hook_contract
- trigger_if_missing:
  - `render/manifest_review.json`
- unlocks:
  - `verify_agent`

## success_criteria
- `manifest_review.json`이 생성된다.
- decision이 `pass` 또는 `pass_with_warning`다.

## failure_modes
- asset 없음
- manifest rule 위반
- AI sidecar review 실패


# Execution Task

너의 역할은 render manifest를 사후 검토하는 review-only agent다.
manifest를 수정하거나 재배치안을 직접 실행하지 마라.
아래 자료를 보고 review_result JSON 하나만 반환하라.
마크다운, 설명문, 코드블록 없이 JSON object 하나만 반환하라.
최상단 문자와 마지막 문자는 반드시 중괄호여야 한다.
stage는 review_manifest_agent로 써라.
decision은 pass, pass_with_warning, needs_revision, blocked 중 하나여야 한다.
status는 succeeded, succeeded_with_warning, blocked 중 하나여야 한다.
findings의 각 항목은 severity, message, evidence_refs만 가져야 한다.
NumbersDesign.md 관점에서 객체 순서와 흐름이 자연스러운지 검토하라.

Rule review:
{
  "schema_version": "1.0.0",
  "stage": "review_manifest_rule_agent",
  "lesson_id": null,
  "status": "succeeded",
  "decision": "pass",
  "findings": [],
  "blocking_issues": [],
  "warnings": []
}

Render manifest summary:
{
  "asset_count": 16,
  "sheet_names": [
    "2-3차시",
    "4차시",
    "5차시",
    "6차시",
    "7차시"
  ],
  "assets": [
    {
      "sheet_name": "2-3차시",
      "asset_type": "textbook_card",
      "insert_order": 1,
      "lesson_flow_stage": null,
      "x": null,
      "y": null,
      "width": null,
      "height": null
    },
    {
      "sheet_name": "2-3차시",
      "asset_type": "activity_sheet",
      "insert_order": 2,
      "lesson_flow_stage": "during",
      "x": null,
      "y": null,
      "width": null,
      "height": null
    },
    {
      "sheet_name": "2-3차시",
      "asset_type": "activity_sheet",
      "insert_order": 3,
      "lesson_flow_stage": "during",
      "x": null,
      "y": null,
      "width": null,
      "height": null
    },
    {
      "sheet_name": "2-3차시",
      "asset_type": "activity_sheet",
      "insert_order": 4,
      "lesson_flow_stage": "after",
      "x": null,
      "y": null,
      "width": null,
      "height": null
    },
    {
      "sheet_name": "4차시",
      "asset_type": "textbook_card",
      "insert_order": 1,
      "lesson_flow_stage": null,
      "x": null,
      "y": null,
      "width": null,
      "height": null
    },
    {
      "sheet_name": "4차시",
      "asset_type": "activity_sheet",
      "insert_order": 2,
      "lesson_flow_stage": "during",
      "x": null,
      "y": null,
      "width": null,
      "height": null
    },
    {
      "sheet_name": "4차시",
      "asset_type": "activity_sheet",
      "insert_order": 3,
      "lesson_flow_stage": "after",
      "x": null,
      "y": null,
      "width": null,
      "height": null
    },
    {
      "sheet_name": "5차시",
      "asset_type": "textbook_card",
      "insert_order": 1,
      "lesson_flow_stage": null,
      "x": null,
      "y": null,
      "width": null,
      "height": null
    },
    {
      "sheet_name": "5차시",
      "asset_type": "activity_sheet",
      "insert_order": 2,
      "lesson_flow_stage": "during",
      "x": null,
      "y": null,
      "width": null,
      "height": null
    },
    {
      "sheet_name": "5차시",
      "asset_type": "activity_sheet",
      "insert_order": 3,
      "lesson_flow_stage": "after",
      "x": null,
      "y": null,
      "width": null,
      "height": null
    },
    {
      "sheet_name": "6차시",
      "asset_type": "textbook_card",
      "insert_order": 1,
      "lesson_flow_stage": null,
      "x": null,
      "y": null,
      "width": null,
      "height": null
    },
    {
      "sheet_name": "6차시",
      "asset_type": "activity_sheet",
      "insert_order": 2,
      "lesson_flow_stage": "during",
      "x": null,
      "y": null,
      "width": null,
      "height": null
    },
    {
      "sheet_name": "6차시",
      "asset_type": "activity_sheet",
      "insert_order": 3,
      "lesson_flow_stage": "after",
      "x": null,
      "y": null,
      "width": null,
      "height": null
    },
    {
      "sheet_name": "7차시",
      "asset_type": "textbook_card",
      "insert_order": 1,
      "lesson_flow_stage": null,
      "x": null,
      "y": null,
      "width": null,
      "height": null
    },
    {
      "sheet_name": "7차시",
      "asset_type": "activity_sheet",
      "insert_order": 2,
      "lesson_flow_stage": "during",
      "x": null,
      "y": null,
      "width": null,
      "height": null
    },
    {
      "sheet_name": "7차시",
      "asset_type": "activity_sheet",
      "insert_order": 3,
      "lesson_flow_stage": "during",
      "x": null,
      "y": null,
      "width": null,
      "height": null
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
