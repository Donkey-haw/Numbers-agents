# page_candidate_agent

## identity
- status: planned
- layer: reading
- implementation: model-driven

## responsibility
- 차시 query를 바탕으로 후보 페이지 집합을 생성한다.

## inputs
- required:
  - `source/lesson_queries.json`
  - `source/<doc_id>.page_index.json`

## outputs
- `source/page_candidates.json`
- `source/page_candidate.status.json`

## allowed_tools
- model:
  - Gemini CLI 또는 Codex CLI
- local:
  - JSON schema validation

## allowed_actions
- query와 page summary를 비교해 후보 페이지 판단
- candidate page ranking
- candidate window 제한

## forbidden_actions
- boundary 최종 확정
- lesson meaning 판단
- schedule 수정

## rules
- boundary candidate page selection은 반드시 이 Agent를 통해서만 수행한다.

## hook_contract
- trigger_if_missing:
  - `source/page_candidates.json`
- unlocks:
  - `boundary_decision_agent`

## success_criteria
- 각 lesson에 대해 candidate_pages가 생성된다.

## failure_modes
- lesson query 누락
- page index 누락
- model timeout
- schema 불일치
