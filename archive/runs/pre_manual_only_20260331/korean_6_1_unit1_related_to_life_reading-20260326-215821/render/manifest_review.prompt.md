# Runtime Agent Spec: review_manifest_agent

아래 AGENT.md는 이 단계의 역할과 경계를 정의한다.
문서에 적힌 역할만 수행하고, 하지 말아야 할 일은 넘지 마라.
출력 형식 요구가 있으면 반드시 지켜라.

# review_manifest_agent

## 역할
- render manifest의 배치 논리를 사후 검토한다.
- 교과서 카드 우선 배치와 before/during/after 흐름을 확인한다.

구현:
- `scripts/review_manifest_agent.py`

## 입력
- `render/render_manifest.json`

## 출력
- `render/manifest_review.json`
- `render/manifest_rule_review.json`

## 내부 책임
- sheet별 자산 존재 여부 확인
- 첫 자산이 textbook card인지 확인
- activity flow 순서가 before/during/after인지 확인
- 그 다음 `AGENT.md` 기반 AI review를 sidecar로 실행해 manifest 해석을 보강한다.

## 성공 조건
- `manifest_review.json` 생성
- decision이 `pass` 또는 `pass_with_warning`

## 차단 조건
- 어떤 시트에도 asset이 없음

## 하지 말아야 할 일
- 실제 Numbers 파일을 수정하지 않는다.
- 자산을 다시 생성하지 않는다.
- AI review가 manifest의 좌표나 순서를 직접 수정해서는 안 된다.

## 테스트 방법
```bash
python3 scripts/pipeline_orchestrator.py \
  --config configs/<config>.json \
  --stop-after review_manifest_agent \
  --keep-run-artifacts
```

## 확인 포인트
- `manifest_rule_review.json`
- `manifest_review.json`의 `warnings`
- 시트별 asset order 확인


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
  "status": "succeeded_with_warning",
  "decision": "pass_with_warning",
  "findings": [],
  "blocking_issues": [],
  "warnings": [
    "4-6차시: activity flow order is not before/during/after"
  ]
}

Render manifest summary:
{
  "asset_count": 27,
  "sheet_names": [
    "12-13차시",
    "14차시",
    "1차시",
    "2-3차시",
    "4-6차시",
    "7-8차시",
    "9-11차시"
  ],
  "assets": [
    {
      "sheet_name": "12-13차시",
      "asset_type": "textbook_card",
      "insert_order": 1,
      "lesson_flow_stage": null,
      "x": null,
      "y": null,
      "width": null,
      "height": null
    },
    {
      "sheet_name": "12-13차시",
      "asset_type": "activity_sheet",
      "insert_order": 2,
      "lesson_flow_stage": "during",
      "x": null,
      "y": null,
      "width": null,
      "height": null
    },
    {
      "sheet_name": "12-13차시",
      "asset_type": "activity_sheet",
      "insert_order": 3,
      "lesson_flow_stage": "during",
      "x": null,
      "y": null,
      "width": null,
      "height": null
    },
    {
      "sheet_name": "12-13차시",
      "asset_type": "activity_sheet",
      "insert_order": 4,
      "lesson_flow_stage": "after",
      "x": null,
      "y": null,
      "width": null,
      "height": null
    },
    {
      "sheet_name": "14차시",
      "asset_type": "textbook_card",
      "insert_order": 1,
      "lesson_flow_stage": null,
      "x": null,
      "y": null,
      "width": null,
      "height": null
    },
    {
      "sheet_name": "14차시",
      "asset_type": "activity_sheet",
      "insert_order": 2,
      "lesson_flow_stage": "during",
      "x": null,
      "y": null,
      "width": null,
      "height": null
    },
    {
      "sheet_name": "14차시",
      "asset_type": "activity_sheet",
      "insert_order": 3,
      "lesson_flow_stage": "after",
      "x": null,
      "y": null,
      "width": null,
      "height": null
    },
    {
      "sheet_name": "1차시",
      "asset_type": "textbook_card",
      "insert_order": 1,
      "lesson_flow_stage": null,
      "x": null,
      "y": null,
      "width": null,
      "height": null
    },
    {
      "sheet_name": "1차시",
      "asset_type": "activity_sheet",
      "insert_order": 2,
      "lesson_flow_stage": "before",
      "x": null,
      "y": null,
      "width": null,
      "height": null
    },
    {
      "sheet_name": "1차시",
      "asset_type": "activity_sheet",
      "insert_order": 3,
      "lesson_flow_stage": "during",
      "x": null,
      "y": null,
      "width": null,
      "height": null
    },
    {
      "sheet_name": "1차시",
      "asset_type": "activity_sheet",
      "insert_order": 4,
      "lesson_flow_stage": "after",
      "x": null,
      "y": null,
      "width": null,
      "height": null
    },
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
      "sheet_name": "4-6차시",
      "asset_type": "textbook_card",
      "insert_order": 1,
      "lesson_flow_stage": null,
      "x": null,
      "y": null,
      "width": null,
      "height": null
    },
    {
      "sheet_name": "4-6차시",
      "asset_type": "activity_sheet",
      "insert_order": 2,
      "lesson_flow_stage": "during",
      "x": null,
      "y": null,
      "width": null,
      "height": null
    },
    {
      "sheet_name": "4-6차시",
      "asset_type": "activity_sheet",
      "insert_order": 3,
      "lesson_flow_stage": "after",
      "x": null,
      "y": null,
      "width": null,
      "height": null
    },
    {
      "sheet_name": "4-6차시",
      "asset_type": "activity_sheet",
      "insert_order": 4,
      "lesson_flow_stage": "before",
      "x": null,
      "y": null,
      "width": null,
      "height": null
    },
    {
      "sheet_name": "7-8차시",
      "asset_type": "textbook_card",
      "insert_order": 1,
      "lesson_flow_stage": null,
      "x": null,
      "y": null,
      "width": null,
      "height": null
    },
    {
      "sheet_name": "7-8차시",
      "asset_type": "activity_sheet",
      "insert_order": 2,
      "lesson_flow_stage": "during",
      "x": null,
      "y": null,
      "width": null,
      "height": null
    },
    {
      "sheet_name": "7-8차시",
      "asset_type": "activity_sheet",
      "insert_order": 3,
      "lesson_flow_stage": "during",
      "x": null,
      "y": null,
      "width": null,
      "height": null
    },
    {
      "sheet_name": "7-8차시",
      "asset_type": "activity_sheet",
      "insert_order": 4,
      "lesson_flow_stage": "after",
      "x": null,
      "y": null,
      "width": null,
      "height": null
    },
    {
      "sheet_name": "9-11차시",
      "asset_type": "textbook_card",
      "insert_order": 1,
      "lesson_flow_stage": null,
      "x": null,
      "y": null,
      "width": null,
      "height": null
    },
    {
      "sheet_name": "9-11차시",
      "asset_type": "activity_sheet",
      "insert_order": 2,
      "lesson_flow_stage": "during",
      "x": null,
      "y": null,
      "width": null,
      "height": null
    },
    {
      "sheet_name": "9-11차시",
      "asset_type": "activity_sheet",
      "insert_order": 3,
      "lesson_flow_stage": "during",
      "x": null,
      "y": null,
      "width": null,
      "height": null
    },
    {
      "sheet_name": "9-11차시",
      "asset_type": "activity_sheet",
      "insert_order": 4,
      "lesson_flow_stage": "after",
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
