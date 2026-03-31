# Pipeline Agent Catalog

## 목적

이 문서는 NumbersAuto 전체 자동화 과정을 구성하는 Agent를 한곳에서 정의한다.

목표:

- 전체 파이프라인의 Agent 목록을 고정한다.
- 각 Agent의 단일 책임을 명확히 적는다.
- 각 Agent가 사용할 수 있는 툴과 기능 범위를 명시한다.
- Rules와 hook으로 어떤 기능을 어떤 Agent가 독점하는지 기준을 만든다.


## 분류 기준

전체 Agent는 아래 4개 레이어로 본다.

1. 입력 식별 레이어
2. 읽기/해석 레이어
3. 생성/검증 레이어
4. 렌더/출력 레이어

현재 실사용 중인 Agent와 legacy source parsing 경로의 최소 Agent를 함께 적는다.


## Agent 목록

### 입력 식별 레이어

- `document_inventory_agent`

### 읽기/해석 레이어

이 레이어는 자동 차시 분류가 필요한 legacy/optional path다.
manual page selection으로 `pdf_pages`가 확정되면 기본 경로에서 skip 가능하다.

- `pdf_extract_agent`
- `page_index_agent`
- `schedule_parse_agent`
- `lesson_query_agent`
- `page_candidate_agent`
- `boundary_decision_agent`
- `boundary_validation_agent`

### 생성/검증 레이어

- `lesson_analysis_agent`
- `lesson_review_agent`
- `activity_plan_agent`
- `activity_review_agent`

### 렌더/출력 레이어

- `html_card_agent`
- `capture_agent`
- `numbers_compose_agent`
- `review_manifest_agent`
- `verify_agent`


## Agent별 단일 책임

### `document_inventory_agent`

- 파일 존재 여부를 확인한다.
- 입력 파일을 교과서 / 진도표 / 보조자료로 분류한다.

독점 기능:

- 입력 문서 유형 판별


### `pdf_extract_agent`

- PDF를 페이지별 텍스트로 추출한다.

독점 기능:

- PDF raw text extraction


### `page_index_agent`

- 페이지 텍스트를 검색 가능한 index로 정리한다.

독점 기능:

- page excerpt / heading 후보 / token index 생성


### `schedule_parse_agent`

- 진도표에서 단원/차시 구조를 파싱한다.

독점 기능:

- schedule structure extraction


### `lesson_query_agent`

- 차시별 탐색 query를 생성한다.

독점 기능:

- lesson title을 boundary query로 정규화


### `page_candidate_agent`

- query별 후보 페이지 집합을 생성한다.

독점 기능:

- boundary candidate page selection


### `boundary_decision_agent`

- 후보 페이지를 보고 차시 start/end를 결정한다.

독점 기능:

- boundary final decision


### `boundary_validation_agent`

- boundary 결과를 검증한다.

독점 기능:

- boundary consistency validation


### `lesson_analysis_agent`

- 차시 교육 내용을 분석한다.

독점 기능:

- lesson semantic analysis generation


### `lesson_review_agent`

- lesson analysis 결과를 검토한다.

독점 기능:

- lesson analysis structural review


### `activity_plan_agent`

- lesson analysis를 바탕으로 활동을 생성한다.

독점 기능:

- activity plan generation


### `activity_review_agent`

- activity plan 결과를 검토한다.

독점 기능:

- activity plan structural review


### `html_card_agent`

- 최종 activity/source 산출물을 HTML 카드로 렌더한다.

독점 기능:

- HTML card rendering


### `capture_agent`

- HTML 카드를 이미지 또는 배치 가능한 렌더 결과로 캡처한다.

독점 기능:

- card capture


### `numbers_compose_agent`

- 캡처 결과를 Numbers 파일로 합성한다.

독점 기능:

- Numbers composition


### `review_manifest_agent`

- 최종 render manifest와 배치 규칙을 검토한다.

독점 기능:

- render manifest review


### `verify_agent`

- 최종 output을 검증한다.

독점 기능:

- final output verification


## 툴 분류 기준

Agent가 사용할 수 있는 툴은 아래처럼 분류한다.

### 1. Local deterministic tool

예:

- filesystem read/write
- JSON schema validation
- regex
- token matching
- PyMuPDF
- local Python utility

권장 사용처:

- 읽기
- 인덱싱
- 후보 선정
- 구조 검증


### 2. Model inference tool

예:

- Gemini CLI
- Codex CLI

권장 사용처:

- 경계 최종 판정
- lesson 의미 분석
- activity 생성


### 3. Rendering / platform tool

예:

- Playwright
- AppleScript
- Numbers composition helper

권장 사용처:

- html capture
- Numbers 반영


## Rules

아래 Rules는 전체 파이프라인의 책임 경계를 강제한다.

1. PDF 텍스트 추출은 `pdf_extract_agent`만 수행한다.
2. 진도표 구조 파싱은 `schedule_parse_agent`만 수행한다.
3. lesson boundary query 생성은 `lesson_query_agent`만 수행한다.
4. candidate page selection은 `page_candidate_agent`만 수행한다.
5. boundary final decision은 `boundary_decision_agent`만 수행한다.
6. boundary validation은 `boundary_validation_agent`만 수행한다.
7. lesson meaning analysis는 `lesson_analysis_agent`만 수행한다.
8. activity generation은 `activity_plan_agent`만 수행한다.
9. HTML rendering은 `html_card_agent`만 수행한다.
10. Numbers composition은 `numbers_compose_agent`만 수행한다.


## Hook 적용 원칙

각 Agent는 자기 출력 artifact를 통해서만 downstream과 연결된다.

예:

- `page_texts.json`이 없으면 `pdf_extract_agent`를 호출해야 한다.
- `lesson_queries.json`이 없으면 `lesson_query_agent`를 호출해야 한다.
- `boundary_decisions.json`은 `boundary_decision_agent` 외 다른 경로로 생성하면 안 된다.

중요한 점:

- hook은 편의 장치가 아니라 책임 강제 장치다.
- 다른 Agent가 같은 기능을 우회 수행하면 문서상의 분리가 의미가 없어진다.


## 직렬/병렬 기준

기본 원칙:

- 전역 문맥을 형성하는 단계는 직렬
- 차시 단위 독립 작업만 병렬

권장 직렬 단계:

1. `document_inventory_agent`
2. `pdf_extract_agent`
3. `page_index_agent`
4. `schedule_parse_agent`
5. `lesson_query_agent`

권장 병렬 단계:

1. 차시별 `page_candidate_agent`
2. 차시별 `boundary_decision_agent`
3. 차시별 `boundary_validation_agent`
4. 차시별 `lesson_analysis_agent`
5. 차시별 `lesson_review_agent`
6. 차시별 `activity_plan_agent`
7. 차시별 `activity_review_agent`


## 현재 우선순위

지금 가장 먼저 문서화와 구현 기준을 고정해야 하는 영역은 읽기/해석 레이어다.

우선순위:

1. `document_inventory_agent`
2. `pdf_extract_agent`
3. `page_index_agent`
4. `schedule_parse_agent`
5. `lesson_query_agent`
6. `page_candidate_agent`
7. `boundary_decision_agent`
8. `boundary_validation_agent`

이 레이어가 정리돼야 이후 lesson/activity Agent도 더 작은 입력만 받게 된다.
