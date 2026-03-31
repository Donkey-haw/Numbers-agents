# pdf_extract_agent

## identity
- status: planned
- layer: reading
- implementation: runtime-driven

## responsibility
- PDF를 페이지별 텍스트로 추출한다.

## inputs
- required:
  - 교과서 PDF 또는 진도표 PDF

## outputs
- `source/<doc_id>.page_texts.json`
- `source/<doc_id>.pdf_extract.status.json`

## allowed_tools
- local:
  - PyMuPDF
  - JSON serialization

## allowed_actions
- 페이지별 raw text extraction
- 페이지 번호 보존
- 추출 실패 페이지 기록

## forbidden_actions
- 제목 판단
- 단원/차시 구조 파싱
- boundary 판단

## rules
- PDF raw text extraction은 반드시 이 Agent를 통해서만 수행한다.

## hook_contract
- trigger_if_missing:
  - `source/<doc_id>.page_texts.json`
- unlocks:
  - `page_index_agent`
  - `schedule_parse_agent`

## success_criteria
- 모든 페이지에 대해 `page`와 `text`가 기록된다.

## failure_modes
- PDF 열기 실패
- 페이지 추출 실패
