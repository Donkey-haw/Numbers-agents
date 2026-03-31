# boundary_validation_agent

## identity
- status: planned
- layer: verification
- implementation: runtime-driven

## responsibility
- boundary 결정 결과를 검증한다.

## inputs
- required:
  - `source/boundary_decisions.json`

## outputs
- `source/boundary_validation.json`
- `source/boundary_validation.status.json`

## allowed_tools
- local:
  - JSON schema validation
  - overlap / range validation
  - consistency checks

## allowed_actions
- 누락 검출
- 중복 검출
- 역전 range 검출
- overlap 검출

## forbidden_actions
- boundary 재결정
- candidate 재생성
- lesson meaning 해석

## rules
- boundary consistency validation은 반드시 이 Agent를 통해서만 수행한다.

## hook_contract
- trigger_if_missing:
  - `source/boundary_validation.json`
- unlocks:
  - `lesson_analysis_agent`

## success_criteria
- validation JSON과 status가 생성된다.
- blocking issue가 없으면 downstream이 진행 가능하다.

## failure_modes
- boundary decisions 누락
- validation rule 실패
