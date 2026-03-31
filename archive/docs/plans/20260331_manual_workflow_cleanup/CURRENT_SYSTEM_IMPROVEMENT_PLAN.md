# Current System Improvement Plan

## 목적

이 문서는 현재 NumbersAuto 구조의 완성도를 높이기 위한 단기 개선 계획을 정리한다.

대상 범위:

- 웹 UI 흐름 안정화
- 서버 run 상태 관리 정합성
- config 생성 품질
- source 단계 병목 제거
- 관측성과 운영 복구성 향상

이 문서는 미래형 workflow 확장안이 아니라, 현재 구조를 실제로 더 안정적으로 돌리기 위한 실행 계획에 집중한다.


## 현재 시스템 요약

현재 시스템의 큰 흐름은 아래와 같다.

1. 웹에서 교과서 선택
2. 진도표 파싱
3. 단원 선택
4. config 생성
5. pipeline run 시작
6. source boundary / validation
7. lesson / activity 생성 및 review
8. render / capture / compose / verify

기본 뼈대는 이미 갖춰져 있다.

문제는 아래 세 축에서 품질 저하가 발생하고 있다는 점이다.

- 입력 품질 불안정
- run 상태와 실제 프로세스 상태 불일치
- 첫 stage의 병목으로 전체 파이프라인 차단


## 핵심 문제 요약

### 1. stale run이 Live로 보이는 상태 정합성 문제

현재 `/api/runs`는 manifest 기반으로 run을 보여주고, cancel은 메모리의 `_active_runs`를 기준으로 처리한다.

이 구조 때문에 아래 상황이 발생한다.

- 서버 재시작 후 실제 프로세스는 없음
- manifest에는 `pending` 또는 `running` 비슷한 상태가 남음
- UI는 이를 `LIVE` run으로 표시
- 사용자가 cancel을 눌러도 서버는 `No active process`를 반환

즉, UI 관점의 실행 상태와 실제 실행 상태가 분리되어 있다.


### 2. `source_boundary_agent`가 현재 전체 병목이다

현재 source boundary 단계는 PDF의 페이지 발췌 카탈로그를 크게 만든 뒤, 이를 거의 그대로 Gemini prompt에 전달한다.

이 구조는 아래 문제를 만든다.

- prompt 크기 과대
- Gemini timeout 증가
- 첫 stage에서 run 전체 정지
- 이후 lesson/activity 품질 개선이 있어도 체감되지 않음

즉 현재 파이프라인의 성능 병목과 성공률 병목이 모두 source boundary에 집중되어 있다.


### 3. 진도표 파서 결과 검증이 약하다

현재 `generate-config` 결과가 아래처럼 부정확해도 UI와 서버가 그대로 다음 단계로 넘긴다.

- `units=[]`
- 과목 전체가 1개 단원으로 합쳐짐
- 단원/차시 명칭이 boundary query로 부적합

이 상태에서 step 2로 넘어가면 사용자는 빈 단원 선택 화면을 보거나, 이후 source 단계에서 실패하게 된다.


### 4. config naming 규칙이 한글 데이터에 취약하다

현재 slug 생성이 영문/숫자 중심 정규식에 기대고 있어서 아래 문제가 생긴다.

- `configs/1.json` 같은 비의미적 파일명
- `card_file` 충돌 가능성 증가
- section 식별자 중복 위험

즉 config와 artifact naming contract가 한글 교과 데이터와 잘 맞지 않는다.


### 5. UI 에러 피드백이 부족하다

현재 UI는 아래 상황을 잘 구분하지 못한다.

- 파싱 실패
- 파싱 성공 but 단원 0개
- stale run
- cancel 실패
- source stage timeout

결과적으로 사용자는 "멈췄다"는 사실만 보게 되고, 어디를 고쳐야 하는지 알기 어렵다.


## 개선 원칙

이번 개선은 아래 원칙으로 진행한다.

1. 실제 프로세스 상태와 표시 상태를 맞춘다.
2. source 단계 성공률을 먼저 끌어올린다.
3. 잘못된 입력은 최대한 앞단에서 차단한다.
4. 사용자가 실패 원인을 UI에서 볼 수 있게 한다.
5. 구조 리팩터링보다 운영 안정화를 우선한다.


## 우선순위별 실행 계획

## Phase 1. 상태 정합성과 사용자 피드백 복구

목표:

- stale run을 더 이상 `LIVE`로 보이지 않게 한다.
- 사용자가 실패를 실패로 인지할 수 있게 한다.

작업:

### 1-1. run 상태 재분류 로직 추가

대상:

- `app/server/run_manager.py`

작업 내용:

- manifest 기준 `pending/running`처럼 보이더라도 실제 active process가 없으면 `stale` 또는 `abandoned`로 재분류
- `/api/runs`
- `/api/runs/{run_id}`
- `/api/runs/{run_id}/cancel`
  응답에 process-truth를 함께 반영

권장 방식:

- `runtime_state`
  - `active`
  - `finished`
  - `stale`
- `cancelable`
  - `true/false`

기대 효과:

- 서버 재시작 후 죽은 run이 `LIVE`처럼 보이지 않음
- cancel 버튼의 표시 조건이 명확해짐


### 1-2. stale run UI 반영

대상:

- `app/web/src/pages/RunDetailPage.tsx`
- `app/web/src/components/RunHeader.tsx`
- `app/web/src/types/events.ts`

작업 내용:

- `LIVE` 표시는 실제 active run에만 한정
- stale run은 별도 badge로 표시
- cancel 실패 시 toast 또는 inline error 표시
- cancel 불가능한 run은 버튼 숨기기 또는 비활성화

기대 효과:

- 사용자가 현재 run이 실제로 돌아가는지 즉시 알 수 있음
- 운영 혼란 감소


### 1-3. New Run 모달 empty/error state 추가

대상:

- `app/web/src/components/NewRunModal.tsx`

작업 내용:

- `parsedUnits.length === 0`일 때 step 2로 자동 이동하지 않도록 변경
- 파싱 실패와 단원 없음 상태를 구분
- 빈 결과일 경우 안내 문구와 재시도/다른 교과 선택 유도

기대 효과:

- "빈 화면" 문제 제거
- 사용자가 parser 문제를 더 빨리 인지


## Phase 2. 입력 품질 안정화

목표:

- source 단계가 처리 가능한 config를 앞단에서 생성한다.

작업:

### 2-1. 진도표 파서 결과 검증 강화

대상:

- `app/server/run_manager.py`
- 진도표 파싱 스크립트

작업 내용:

- `units=[]`이면 성공 응답으로 넘기지 않고 validation warning 또는 failure로 처리
- 단원 수와 차시 수가 비정상일 때 서버에서 검증 메시지 포함
- UI에 parser quality message 전달

권장 검증 예시:

- 단원 0개면 실패
- 차시 30개 이상이 단일 단원에 몰리면 경고
- lesson title이 지나치게 긴 경우 경고

기대 효과:

- 잘못된 진도표 결과가 뒤 단계까지 전염되지 않음


### 2-2. config naming 전략 교체

대상:

- `app/server/run_manager.py`

작업 내용:

- 한글 과목명/단원명 기반의 slug-safe naming 전략 도입
- slug가 비면 숫자 fallback만 쓰지 말고 stable hash 또는 run-local id 사용
- `card_file`, `section_dir`, config filename이 서로 충돌하지 않게 분리

권장 방향:

- 표시용 name과 시스템용 id를 분리
- 시스템 id는 `lesson-001`, `lesson-002` 같은 stable id 사용
- 사람이 읽는 label은 한글 그대로 유지

기대 효과:

- 파일 충돌 감소
- artifact 구조 예측 가능성 향상


### 2-3. boundary-friendly config contract 도입

대상:

- config 생성 로직
- `source_boundary_agent`

작업 내용:

- `title`과 `title_query` 분리
- 필요 시 `end_before_query` 별도 포함
- UI에 보이는 lesson 제목과 source 탐색용 query를 구분

기대 효과:

- source boundary 정확도 향상
- title formatting 변화가 boundary 실패로 직결되지 않음


## Phase 3. source 병목 제거

목표:

- `source_boundary_agent` timeout 제거
- 첫 stage 성공률 회복

작업:

### 3-1. 전체 페이지 카탈로그 투입 방식 중단

대상:

- `scripts/source_boundary_agent.py`

작업 내용:

- 전체 페이지를 모두 prompt에 넣는 방식 중단
- 먼저 candidate page preselection 수행
- title keyword, TOC signal, page density 등으로 후보 페이지 집합 축소

권장 구조:

1. local preselector
2. compact page digest 생성
3. Gemini boundary inference

기대 효과:

- prompt 크기 급감
- timeout 감소


### 3-2. 2단계 boundary 추론 도입

대상:

- `scripts/source_boundary_agent.py`

작업 내용:

- 1차: 시작 페이지 후보 범위 추론
- 2차: 좁혀진 범위 안에서 시작/끝 페이지 정밀 추론

기대 효과:

- 전체 페이지 문맥을 한 번에 던지는 구조보다 훨씬 안정적
- 추론 실패 원인 분리 가능


### 3-3. source stage fallback 전략 정리

대상:

- `scripts/source_boundary_agent.py`
- `scripts/pipeline_orchestrator.py`

작업 내용:

- Gemini timeout 시 무조건 전체 run을 실패시키기보다,
  - 재시도
  - 범위 축소 재시도
  - low-confidence boundary 결과 저장
  중 하나를 선택 가능하게 설계

기대 효과:

- 첫 stage 단일 실패가 전체 파이프라인을 모두 차단하지 않음


## Phase 4. 관측성 및 운영 복구성 향상

목표:

- 어디서 왜 실패했는지 빠르게 알 수 있게 한다.

작업:

### 4-1. run summary 개선

대상:

- server run response
- run detail UI

작업 내용:

- 현재 stage
- 마지막 성공 stage
- 마지막 오류 메시지
- retry 가능 여부
- stale 여부
  를 요약해서 노출


### 4-2. source stage artifact 가시화

대상:

- run detail page

작업 내용:

- `source_boundary.status.json`
- `source_validation.status.json`
- boundary warning count
- prompt size 또는 candidate page count
  등을 요약 노출

기대 효과:

- source 병목이 UI에서 바로 드러남


### 4-3. subprocess I/O drain 안정화

대상:

- `app/server/run_manager.py`

작업 내용:

- orchestrator subprocess의 stdout/stderr를 장기적으로 drain하도록 개선
- pipe buffer blockage 가능성 제거

비고:

현재는 즉시 재현된 문제는 아니지만, 장시간 로그가 늘면 deadlock 위험이 있다.


## 구현 우선순위

실제 구현 순서는 아래가 적절하다.

1. stale run 재분류 + UI 반영
2. New Run 모달 empty/error state 추가
3. config naming 전략 수정
4. 진도표 결과 검증 강화
5. source boundary preselection 도입
6. source boundary 2단계 추론
7. run summary / source artifact UI 개선
8. subprocess I/O drain 개선

이 순서가 맞는 이유:

- 먼저 사용자 혼란을 줄이고
- 그 다음 잘못된 입력을 차단하고
- 그 다음 실제 병목을 제거하는 편이 효과가 가장 크다


## 완료 기준

이번 개선 작업은 아래 상태가 되면 1차 완료로 본다.

- stale run이 UI에서 `LIVE`로 보이지 않는다.
- cancel 불가 run에서 버튼이 숨겨지거나 명확히 비활성화된다.
- 진도표 파싱 결과가 비어 있으면 step 2 빈 화면 대신 명시적 오류가 보인다.
- config filename과 `card_file`이 한글 교과 데이터에서도 충돌 없이 생성된다.
- `source_boundary_agent` timeout 빈도가 의미 있게 낮아진다.
- run detail에서 마지막 실패 지점이 사용자에게 보인다.


## 기대 효과

이 개선이 완료되면 현재 구조 자체를 갈아엎지 않아도 아래 변화가 생긴다.

- 사용자가 현재 시스템을 더 신뢰할 수 있다.
- 실패 원인을 훨씬 빨리 좁힐 수 있다.
- source 단계 성공률이 올라가 downstream 검증이 가능해진다.
- 이후 curriculum alignment, differentiation 같은 상위 목표 구현도 더 안정된 기반 위에서 진행할 수 있다.


## 다음 권장 작업

가장 먼저 시작할 작업은 아래 둘이다.

1. stale run 상태 재분류와 UI 반영
2. New Run 모달의 parser empty/error state 처리

이 둘은 구현 난이도에 비해 사용자 체감 개선이 크고, 현재 운영 혼란을 가장 빠르게 줄일 수 있다.
