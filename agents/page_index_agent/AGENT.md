# page_index_agent

## identity
- status: planned
- layer: reading
- implementation: runtime-driven

## responsibility
- 추출된 페이지 텍스트를 검색 가능한 page index로 정리한다.

## inputs
- required:
  - `source/<doc_id>.page_texts.json`

## outputs
- `source/<doc_id>.page_index.json`
- `source/<doc_id>.page_index.status.json`

## allowed_tools
- local:
  - regex
  - tokenization
  - local text processing

## allowed_actions
- page excerpt 생성
- heading candidate 생성
- token index 생성
- page metadata 생성

## forbidden_actions
- 단원/차시 boundary 추론
- schedule 해석
- candidate page 확정

## rules
- page excerpt / heading 후보 / token index 생성은 반드시 이 Agent를 통해서만 수행한다.

## hook_contract
- trigger_if_missing:
  - `source/<doc_id>.page_index.json`
- unlocks:
  - `page_candidate_agent`

## success_criteria
- 각 페이지에 대해 excerpt, tokens, heading_candidates가 생성된다.

## failure_modes
- page_texts 누락
- 인덱싱 실패
