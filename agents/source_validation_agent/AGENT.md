# source_validation_agent

## identity
- status: active
- layer: verification
- implementation: `scripts/source_validation_agent.py`

## responsibility
- source boundary 결과를 검토한다.
- 구조 문제, 경계 모호성, 보조자료 매칭 여부를 기록한다.

## inputs
- required:
  - `configs/<config>.json`
  - `source/runtime_config.json`

## outputs
- `source/config_quality_review.json`
- `source/boundary_review.json`
- `source/supplement_review.json`
- `source/source_validation.status.json`

## allowed_tools
- local:
  - local JSON inspection
  - deterministic review rules

## allowed_actions
- source config 품질 검토
- boundary ambiguity 검토
- supplement matching 검토

## forbidden_actions
- source range 재계산
- lesson/activity 생성
- render/output 변경

## rules
- source consistency validation은 반드시 이 Agent를 통해서만 수행한다.

## hook_contract
- trigger_if_missing:
  - `source/config_quality_review.json`
  - `source/boundary_review.json`
- unlocks:
  - `lesson_analysis_agent`

## success_criteria
- 세 종류의 review JSON이 생성된다.
- blocking issue가 없으면 `source_validation.status.json`이 `succeeded` 또는 `succeeded_with_warning`다.

## failure_modes
- runtime config 누락
- review build 실패
- blocking issue 존재
