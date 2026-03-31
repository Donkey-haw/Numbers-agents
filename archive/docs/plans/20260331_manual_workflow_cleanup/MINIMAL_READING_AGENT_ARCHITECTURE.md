# Minimal Reading Agent Architecture

## 목적

이 문서는 NumbersAuto의 교과서/진도표 읽기와 해석 계층을 최소 기능 Agent 단위로 분해하기 위한 설계 원칙과 권장 구조를 정리한다.

핵심 목표:

- 각 Agent가 단 1가지 기능만 수행하게 한다.
- 해당 기능은 반드시 그 Agent를 통해서만 수행되게 한다.
- 직렬 처리와 병렬 처리를 명확히 구분한다.
- 모델이 꼭 필요한 단계만 CLI Agent로 분리한다.

이 문서는 현재 `source_boundary_agent`를 더 크게 튜닝하는 문서가 아니다.
오히려 그 앞단을 더 잘게 쪼개서, boundary 단계가 작은 문제만 풀게 만들기 위한 설계 문서다.


## 핵심 전제

이 구조에서 Agent는 "단계 이름"이 아니라 "능력 단위"다.

즉 좋은 Agent는 아래를 만족해야 한다.

1. 입력이 하나의 책임만 가진다.
2. 출력이 하나의 책임만 가진다.
3. 실패 이유가 한 문장으로 설명된다.
4. 같은 기능은 항상 같은 Agent가 수행한다.
5. 다른 Agent가 그 기능을 우회해서 수행하면 안 된다.

예:

- PDF 텍스트 추출은 `pdf_extract_agent`만 수행한다.
- 진도표 구조 파싱은 `schedule_parse_agent`만 수행한다.
- 후보 페이지 선정은 `page_candidate_agent`만 수행한다.
- boundary 최종 결정은 `boundary_decision_agent`만 수행한다.


## 현재 구조의 문제

현재 source 계층은 다음 기능이 한 단계에 섞이기 쉽다.

- 문서 읽기
- 텍스트 추출
- 페이지 검색
- 진도표 구조 해석
- 차시 query 생성
- 후보 페이지 선정
- boundary 추론
- 결과 검증

이렇게 섞이면 아래 문제가 발생한다.

- timeout 원인을 단계별로 분리할 수 없다.
- deterministic 처리와 model 기반 처리가 뒤섞인다.
- 병렬 실행 시 어떤 단위를 독립 job으로 볼지 불명확하다.
- Rules와 hook으로 책임을 강제하기 어렵다.

즉 지금 필요한 것은 "더 강한 source agent"가 아니라 "더 작은 source agent들"이다.


## Agent 설계 원칙

### 1. 한 Agent는 한 기능만 수행한다

예:

- PDF에서 텍스트를 추출한다.
- 진도표에서 단원/차시 구조를 파싱한다.
- 페이지 후보를 찾는다.

이 세 가지를 한 Agent가 동시에 수행하면 안 된다.


### 2. 읽기와 해석을 분리한다

다음 둘은 다르다.

- 읽기: 문서에서 텍스트를 꺼내고 정리하는 일
- 해석: 그 텍스트가 무엇을 의미하는지 판단하는 일

이 둘이 분리되어야 deterministic layer와 model layer를 분리할 수 있다.


### 3. 후보 선정과 최종 판정을 분리한다

후보 선정은 로컬 규칙 기반으로 가능한 경우가 많다.
최종 판정은 모델이 필요한 경우가 있다.

따라서:

- `page_candidate_agent`: 후보만 고른다.
- `boundary_decision_agent`: 후보를 보고 최종 범위만 결정한다.

이 둘은 반드시 분리하는 편이 좋다.


### 4. 검증은 별도 Agent가 수행한다

생성 Agent가 자기 결과를 검증하게 하면 책임이 다시 섞인다.

따라서:

- `boundary_decision_agent`는 결정을 내리기만 한다.
- `boundary_validation_agent`는 그 결과를 검증하기만 한다.


### 5. 모델은 마지막에만 쓴다

가능한 한 앞단은 deterministic worker로 유지하는 편이 좋다.

이유:

- 속도
- 재현성
- 비용
- 디버깅 용이성

즉 모델 사용은 "정말 판단이 필요한 최소 지점"으로 미뤄야 한다.


## 권장 최소 Agent 분해안

## 1. `document_inventory_agent`

역할:

- 입력 파일 존재 확인
- 문서 종류 판별
- 교과서 / 진도표 / 보조자료 분류

입력:

- 파일 경로 목록

출력:

- `document_inventory.json`

하지 말아야 할 일:

- 문서 내용 해석 금지
- 페이지 텍스트 추출 금지


## 2. `pdf_extract_agent`

역할:

- PDF를 페이지별 텍스트로 추출

입력:

- PDF 파일 하나

출력:

- `page_texts.json`

하지 말아야 할 일:

- 단원/차시 판정 금지
- 제목 후보 판정 금지


## 3. `page_index_agent`

역할:

- 추출된 페이지 텍스트를 검색 가능한 index로 정리

예:

- page excerpt
- heading-like line 후보
- token index
- 페이지별 짧은 요약 텍스트

입력:

- `page_texts.json`

출력:

- `page_index.json`

하지 말아야 할 일:

- lesson boundary 판단 금지


## 4. `schedule_parse_agent`

역할:

- 진도표에서 단원/차시 구조를 파싱

입력:

- 진도표 PDF 또는 OCR 결과

출력:

- `schedule_structure.json`

하지 말아야 할 일:

- 교과서 PDF boundary 추론 금지
- 교과서 페이지 매칭 금지


## 5. `lesson_query_agent`

역할:

- 각 차시에 대한 boundary 탐색용 query 생성

예:

- 표시용 title
- 탐색용 `title_query`
- 종료 판정 보조용 `end_before_query`

입력:

- `schedule_structure.json`
- 필요 시 `document_inventory.json`

출력:

- `lesson_queries.json`

하지 말아야 할 일:

- 실제 페이지 매칭 금지
- start/end 페이지 판정 금지


## 6. `page_candidate_agent`

역할:

- 차시 query를 받아 후보 페이지 집합 생성

입력:

- `lesson_queries.json`
- `page_index.json`

출력:

- `page_candidates.json`

하지 말아야 할 일:

- boundary 최종 확정 금지

비고:

이 단계는 가능하면 deterministic worker로 유지한다.


## 7. `boundary_decision_agent`

역할:

- 후보 페이지 집합을 바탕으로 차시별 start/end 결정

입력:

- `page_candidates.json`

출력:

- `boundary_decisions.json`

하지 말아야 할 일:

- 결과 검증 금지
- schedule 재구성 금지

비고:

이 단계가 model 사용이 필요한 첫 지점이다.
가능하면 차시별 독립 호출로 나누는 것이 좋다.


## 8. `boundary_validation_agent`

역할:

- boundary 결정 결과 검증

검증 예시:

- 누락
- 중복
- 역전된 range
- 과도한 overlap
- candidate evidence 부족

입력:

- `boundary_decisions.json`

출력:

- `boundary_validation.json`

하지 말아야 할 일:

- boundary 재결정 금지


## 권장 처리 순서

직렬 처리:

1. `document_inventory_agent`
2. `pdf_extract_agent`
3. `page_index_agent`
4. `schedule_parse_agent`
5. `lesson_query_agent`

병렬 처리 가능:

1. 차시별 `page_candidate_agent`
2. 차시별 `boundary_decision_agent`
3. 차시별 `boundary_validation_agent`

즉 멀티 CLI는 앞단 전체에 붙이는 것이 아니라,
차시별 독립 단위가 생긴 뒤에만 붙이는 것이 맞다.


## 왜 이 구조가 필요한가

현재 `source_boundary_agent`는 아래를 한 번에 하려고 한다.

- 입력 해석
- 페이지 후보 생성
- 의미 판단
- 시작/끝 추론
- 부분적인 검토

이 구조에서는 다음이 어렵다.

- 왜 timeout이 났는지 분리
- 어떤 단계가 deterministic이어야 하는지 구분
- 병렬 job의 최소 단위 정의
- Rules와 hook 강제

위 구조로 쪼개면 다음이 가능해진다.

- timeout 원인 분리
- 모델 사용 지점 최소화
- per-lesson 병렬화
- artifact contract 명확화
- 단계별 재실행


## Rules와 Hook 적용 원칙

Rules는 "누가 어떤 기능을 담당하는가"를 강제해야 한다.

예:

- PDF 텍스트 추출은 `pdf_extract_agent`만 가능
- 진도표 구조 파싱은 `schedule_parse_agent`만 가능
- 후보 페이지 생성은 `page_candidate_agent`만 가능
- boundary 최종 결정은 `boundary_decision_agent`만 가능

Hook은 "필요 artifact를 만들기 위해 반드시 해당 Agent를 거치게 하는 장치"여야 한다.

예:

- `page_texts.json`이 필요하면 `pdf_extract_agent` hook 호출
- `lesson_queries.json`이 없으면 `lesson_query_agent` 외 다른 우회 경로 금지
- `boundary_decisions.json`은 `boundary_decision_agent`만 생성 가능

중요한 점:

- hook은 편의 기능이 아니라 책임 강제 장치다.
- 다른 Agent가 동일 기능을 몰래 수행하면 구조가 무너진다.


## 모델 사용 원칙

모델은 다음 조건을 만족하는 단계에만 쓴다.

1. deterministic rule로 충분히 해결되지 않는다.
2. 입력이 이미 충분히 작고 정리돼 있다.
3. 출력 contract가 명확하다.
4. 실패 시 재시도 또는 fallback이 가능하다.

따라서 교과서/진도표 읽기 계층에서 모델 사용은 기본적으로 아래 단계에만 허용하는 편이 좋다.

- `boundary_decision_agent`

필요 시 예외적으로 아래도 가능하다.

- `schedule_parse_agent`
  진도표 OCR이나 구조 파싱이 매우 약한 경우

그 외 앞단은 가능한 한 로컬 worker로 유지한다.


## 1차 구현 권장 범위

처음부터 전부 바꾸기보다 아래 4개부터 분리하는 것이 좋다.

1. `pdf_extract_agent`
2. `page_index_agent`
3. `schedule_parse_agent`
4. `lesson_query_agent`

이유:

- 입력 해석 계층의 contract가 먼저 안정돼야 한다.
- boundary 단계가 작아지려면 앞단이 정리되어야 한다.
- 지금의 병목도 사실 앞단 입력 품질 불안정에서 시작된다.


## 1차 구현 완료 기준

아래 상태가 되면 읽기/해석 계층 1차 분리가 성공한 것이다.

- 교과서 PDF에서 페이지별 텍스트를 안정적으로 추출할 수 있다.
- 진도표에서 단원/차시 구조를 독립 artifact로 만들 수 있다.
- 차시별 boundary query가 표시용 title과 분리되어 생성된다.
- 후보 페이지 선정이 모델 없이 가능하다.
- boundary 단계는 후보 페이지 집합만 받아서 판단한다.


## 이후 확장 방향

이 구조가 자리 잡으면 이후 아래 방향으로 자연스럽게 확장할 수 있다.

- `curriculum_alignment_agent`
- `activity_strategy_agent`
- `differentiation_agent`

중요한 점은, 상위 교육적 해석 레이어를 올리기 전에
하단 읽기/해석 계층의 기능 경계를 먼저 고정해야 한다는 점이다.


## 결론

지금 필요한 것은 `source_boundary_agent`를 더 크게 만드는 것이 아니다.

필요한 것은 아래와 같은 흐름으로 읽기/해석 계층을 쪼개는 것이다.

1. 추출한다.
2. 인덱싱한다.
3. 진도 구조를 파싱한다.
4. 탐색 query를 만든다.
5. 후보 페이지를 찾는다.
6. boundary를 결정한다.
7. 결과를 검증한다.

즉 현재의 큰 source 단계는 앞으로 아래처럼 재구성되는 것이 바람직하다.

- `pdf_extract_agent`
- `page_index_agent`
- `schedule_parse_agent`
- `lesson_query_agent`
- `page_candidate_agent`
- `boundary_decision_agent`
- `boundary_validation_agent`

이 구조가 자리 잡아야, 이후의 직렬/병렬 orchestration, Rules/hook 강제, 멀티 CLI 실행도 안정적으로 설계할 수 있다.
