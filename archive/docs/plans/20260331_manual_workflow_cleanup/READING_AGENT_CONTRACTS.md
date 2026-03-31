# Reading Agent Contracts

## 목적

이 문서는 읽기/해석 레이어 Agent의 입출력 artifact contract를 정리한다.

대상 Agent:

1. `document_inventory_agent`
2. `pdf_extract_agent`
3. `page_index_agent`
4. `schedule_parse_agent`
5. `lesson_query_agent`
6. `page_candidate_agent`
7. `boundary_decision_agent`
8. `boundary_validation_agent`

이 문서의 목적은 구현 이전에 artifact 이름과 schema 경계를 고정하는 것이다.


## 기본 원칙

모든 artifact는 아래 원칙을 따른다.

1. JSON 파일로 저장한다.
2. `schema_version`을 반드시 포함한다.
3. 한 artifact는 한 Agent의 출력만 담는다.
4. downstream Agent는 upstream artifact만 읽는다.
5. 중간 계산 결과를 다른 Agent 출력에 몰래 섞지 않는다.


## Agent별 계약

## 1. `document_inventory_agent`

출력:

- `source/document_inventory.json`
- `source/document_inventory.status.json`

schema:

- [document_inventory.schema.json](/Users/jonyeock/Desktop/Tool/NumbersAuto/schemas/document_inventory.schema.json)

역할:

- 입력 문서 경로와 문서 유형을 정리한다.


## 2. `pdf_extract_agent`

출력:

- `source/<doc_id>.page_texts.json`
- `source/<doc_id>.pdf_extract.status.json`

schema:

- [page_texts.schema.json](/Users/jonyeock/Desktop/Tool/NumbersAuto/schemas/page_texts.schema.json)

역할:

- PDF를 페이지별 raw text로 변환한다.


## 3. `page_index_agent`

출력:

- `source/<doc_id>.page_index.json`
- `source/<doc_id>.page_index.status.json`

schema:

- [page_index.schema.json](/Users/jonyeock/Desktop/Tool/NumbersAuto/schemas/page_index.schema.json)

역할:

- page texts를 검색 가능한 page index로 정리한다.


## 4. `schedule_parse_agent`

출력:

- `source/schedule_structure.json`
- `source/schedule_parse.status.json`

schema:

- [schedule_structure.schema.json](/Users/jonyeock/Desktop/Tool/NumbersAuto/schemas/schedule_structure.schema.json)

역할:

- 진도표에서 단원/차시 구조를 파싱한다.


## 5. `lesson_query_agent`

출력:

- `source/lesson_queries.json`
- `source/lesson_query.status.json`

schema:

- [lesson_queries.schema.json](/Users/jonyeock/Desktop/Tool/NumbersAuto/schemas/lesson_queries.schema.json)

역할:

- 차시별 boundary 탐색 query를 생성한다.


## 6. `page_candidate_agent`

출력:

- `source/page_candidates.json`
- `source/page_candidate.status.json`

schema:

- [page_candidates.schema.json](/Users/jonyeock/Desktop/Tool/NumbersAuto/schemas/page_candidates.schema.json)

역할:

- query별 후보 페이지 집합을 생성한다.


## 7. `boundary_decision_agent`

출력:

- `source/boundary_decisions.json`
- `source/boundary_decision.status.json`

schema:

- [boundary_decisions.schema.json](/Users/jonyeock/Desktop/Tool/NumbersAuto/schemas/boundary_decisions.schema.json)

역할:

- candidate pages를 기반으로 start/end를 결정한다.


## 8. `boundary_validation_agent`

출력:

- `source/boundary_validation.json`
- `source/boundary_validation.status.json`

schema:

- [boundary_validation.schema.json](/Users/jonyeock/Desktop/Tool/NumbersAuto/schemas/boundary_validation.schema.json)

역할:

- boundary consistency를 검증한다.


## 연결 흐름

권장 연결 순서:

1. `document_inventory.json`
2. `page_texts.json`
3. `page_index.json`
4. `schedule_structure.json`
5. `lesson_queries.json`
6. `page_candidates.json`
7. `boundary_decisions.json`
8. `boundary_validation.json`

즉 source 계층은 "읽기 -> 구조화 -> query 생성 -> 후보 선정 -> 결정 -> 검증"의 artifact chain으로 연결된다.


## 비고

- 현재 실사용 중인 `source_boundary_agent`는 이 chain을 한 단계에 묶은 transitional agent다.
- 장기적으로는 위 artifact chain을 기준으로 실제 구현을 분리하는 것이 목표다.
