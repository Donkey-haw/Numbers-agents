# lesson_query_agent

## identity
- status: planned
- layer: reading
- implementation: runtime-driven

## responsibility
- 차시별 boundary 탐색용 query를 생성한다.

## inputs
- required:
  - `source/schedule_structure.json`
- optional:
  - `source/document_inventory.json`

## outputs
- `source/lesson_queries.json`
- `source/lesson_query.status.json`

## allowed_tools
- local:
  - text normalization
  - token filtering
  - query shaping rules

## allowed_actions
- 표시용 title 생성
- `title_query` 생성
- `end_before_query` 생성

## forbidden_actions
- 실제 페이지 검색
- 후보 페이지 선정
- boundary 확정

## rules
- lesson boundary 탐색 query 생성은 반드시 이 Agent를 통해서만 수행한다.

## hook_contract
- trigger_if_missing:
  - `source/lesson_queries.json`
- unlocks:
  - `page_candidate_agent`

## success_criteria
- 모든 lesson에 대해 display_title과 title_query가 생성된다.

## failure_modes
- schedule_structure 누락
- query shaping 실패
