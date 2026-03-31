# document_inventory_agent

## identity
- status: planned
- layer: reading
- implementation: runtime-driven

## responsibility
- 입력 파일 존재 여부를 확인한다.
- 입력 파일을 교과서 / 진도표 / 보조자료로 분류한다.

## inputs
- required:
  - 사용자 또는 config가 제공한 파일 경로 목록

## outputs
- `source/document_inventory.json`
- `source/document_inventory.status.json`

## allowed_tools
- local:
  - filesystem read
  - path normalization
  - filename / extension classification

## allowed_actions
- 파일 존재 확인
- 문서 유형 분류
- 절대/상대 경로 정규화

## forbidden_actions
- PDF 텍스트 추출
- 문서 내용 해석
- 진도표 파싱

## rules
- 입력 문서 유형 판별은 반드시 이 Agent를 통해서만 수행한다.

## hook_contract
- trigger_if_missing:
  - `source/document_inventory.json`
- unlocks:
  - `pdf_extract_agent`
  - `schedule_parse_agent`

## success_criteria
- 모든 입력 파일에 대해 `document_id`, `path`, `kind`, `exists`가 기록된다.

## failure_modes
- 입력 경로 누락
- 경로 정규화 실패
