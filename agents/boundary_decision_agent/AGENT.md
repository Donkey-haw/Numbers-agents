# boundary_decision_agent

## identity
- status: planned
- layer: reading
- implementation: model-driven

## responsibility
- 후보 페이지를 보고 차시별 start/end를 결정한다.

## inputs
- required:
  - `source/page_candidates.json`
  - `source/<doc_id>.page_index.json`

## outputs
- `source/boundary_decisions.json`
- `source/boundary_decision.status.json`

## allowed_tools
- local:
  - JSON schema validation
- model:
  - Gemini CLI 또는 Codex CLI

## allowed_actions
- 후보 페이지 비교
- start/end range 결정
- low-confidence decision 표시

## forbidden_actions
- candidate 재생성
- 결과 검증
- lesson/activity 생성

## rules
- boundary final decision은 반드시 이 Agent를 통해서만 수행한다.

## hook_contract
- trigger_if_missing:
  - `source/boundary_decisions.json`
- unlocks:
  - `boundary_validation_agent`

## success_criteria
- 각 lesson에 대해 start/end 또는 not_found 판정이 생성된다.

## failure_modes
- candidate 누락
- model timeout
- schema 불일치
