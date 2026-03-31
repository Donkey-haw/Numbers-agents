# schedule_parse_agent

## identity
- status: planned
- layer: reading
- implementation: runtime-driven

## responsibility
- 진도표에서 단원/차시 구조를 파싱한다.
- transitional 단계에서는 `config.sections`를 기반으로 schedule structure를 구성할 수 있다.

## inputs
- required:
  - 진도표 PDF
- optional:
  - OCR 결과
  - `source/<doc_id>.page_texts.json`

## outputs
- `source/schedule_structure.json`
- `source/schedule_parse.status.json`

## allowed_tools
- local:
  - regex / table normalization
  - OCR post-processing
- model:
  - optional model inference

## allowed_actions
- 단원 추출
- 차시 추출
- 단원-차시 관계 정리

## forbidden_actions
- 교과서 boundary 추론
- 교과서 페이지 매칭
- lesson analysis 생성

## rules
- 진도표 구조 파싱은 반드시 이 Agent를 통해서만 수행한다.

## hook_contract
- trigger_if_missing:
  - `source/schedule_structure.json`
- unlocks:
  - `lesson_query_agent`

## success_criteria
- 각 unit와 lesson 구조가 안정적인 JSON으로 생성된다.

## failure_modes
- OCR / parse 실패
- 단원 0개
- lesson 구조 불완전
