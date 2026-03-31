# Lesson-Level Pipelined DAG Plan

## 목적

현재 파이프라인은 stage barrier 방식으로 동작한다.  
즉 한 stage의 모든 차시 작업이 끝나야 다음 stage로 넘어간다.

이 구조는 구현은 단순하지만, 차시별 병렬 CLI를 이미 쓰고 있는 현재 구조에서는 비효율이 크다.

이 문서는 현재 구조의 한계와, `lesson-level pipelined DAG` 방식으로 전환하는 계획을 정리한다.

## 현재 구조

현재 manual workflow 기준 stage 순서는 아래와 같다.

1. `lesson_analysis_agent`
2. `lesson_review_agent`
3. `activity_plan_agent`
4. `activity_review_agent`
5. `html_card_agent`
6. `capture_agent`
7. `numbers_compose_agent`
8. `review_manifest_agent`
9. `verify_agent`

실행 방식은 stage barrier다.

- 예를 들어 4차시가 있으면 `lesson_analysis_agent`에서 4개 차시를 병렬 실행한다.
- 하지만 4개가 전부 끝나야 `lesson_review_agent`가 시작된다.
- 즉 `1차시`가 먼저 끝나도 `4차시`가 끝날 때까지 다음 단계로 못 간다.

## 현재 구조의 문제

### 1. 느린 차시 하나가 전체 stage를 막는다

예:

- `1차시 lesson_analysis` 20초
- `2차시 lesson_analysis` 25초
- `3차시 lesson_analysis` 18초
- `4차시 lesson_analysis` 80초

이 경우 `1차시`는 20초 만에 다음 단계로 갈 수 있지만, 실제론 80초를 기다린다.

### 2. 병렬 CLI 활용도가 낮다

현재는 stage 내부 병렬만 있고, stage 간 파이프라이닝은 없다.  
즉 CLI를 병렬로 많이 띄워도 stage barrier 때문에 전체 throughput이 낮아진다.

### 3. 대시보드상 진행률이 실제 체감보다 느리다

어떤 차시는 이미 activity까지 갈 준비가 됐는데, UI에서는 다음 stage가 아직 시작되지 않은 것처럼 보인다.

### 4. 생성 계층의 장점을 충분히 못 쓴다

`lesson_analysis`, `lesson_review`, `activity_plan`, `activity_review`는 사실상 차시별 독립 작업이다.  
이런 작업은 stage 단위보다 lesson-level dependency로 묶는 편이 더 자연스럽다.

## 권장 구조

## 핵심 아이디어

`lesson-level pipelined DAG`로 바꾼다.

즉 각 차시는 자기 흐름대로 아래 단계를 진행한다.

1. `lesson_analysis`
2. `lesson_review`
3. `activity_plan`
4. `activity_review`
5. `html_card`

그리고 모든 차시의 `html_card`가 끝난 뒤에만 global 단계로 넘어간다.

1. `capture`
2. `numbers_compose`
3. `review_manifest`
4. `verify`

## 새 실행 모델

### lesson-level 단계

각 차시마다 아래 dependency를 가진다.

`lesson_analysis -> lesson_review -> activity_plan -> activity_review -> html_card`

이 체인은 차시별로 독립적이다.

예:

- `1차시 lesson_analysis`가 끝나면 바로 `1차시 lesson_review` 시작
- `1차시 lesson_review`가 끝나면 바로 `1차시 activity_plan` 시작
- 동시에 `2차시 lesson_analysis`는 아직 진행 중일 수 있음

### global barrier 단계

아래 단계는 모든 차시가 준비된 뒤에만 시작한다.

- `capture_agent`
- `numbers_compose_agent`
- `review_manifest_agent`
- `verify_agent`

즉 barrier는 완전히 없애는 것이 아니라, 꼭 필요한 지점에만 둔다.

## 권장 DAG

### 차시별 DAG

For each lesson:

1. `lesson_analysis_agent[lesson]`
2. `lesson_review_agent[lesson]`
3. `activity_plan_agent[lesson]`
4. `activity_review_agent[lesson]`
5. `html_card_agent[lesson]`

### 전체 DAG

1. 모든 `html_card_agent[lesson]` 완료
2. `capture_agent`
3. `numbers_compose_agent`
4. `review_manifest_agent`
5. `verify_agent`

## 기대 효과

### 1. 총 실행 시간 단축

느린 차시가 있더라도 빠른 차시는 먼저 다음 단계로 이동한다.

### 2. 병렬 CLI 활용도 증가

`gemini`와 `codex` runner를 차시별로 더 촘촘하게 사용하게 된다.

### 3. 대시보드 가시성 향상

현재 차시가 어느 단계까지 갔는지가 더 정확하게 보인다.

### 4. 오케스트레이터 구조와 더 잘 맞음

지금도 이미 `job_manifest.json`과 worker status가 있다.  
즉 stage 중심보다는 job dependency 중심으로 확장하는 게 자연스럽다.

## 어떤 stage를 lesson-level로 풀어야 하나

lesson-level로 풀 대상:

- `lesson_analysis_agent`
- `lesson_review_agent`
- `activity_plan_agent`
- `activity_review_agent`
- `html_card_agent`

global로 유지할 대상:

- `capture_agent`
- `numbers_compose_agent`
- `review_manifest_agent`
- `verify_agent`

## 구현 방향

## 1차 목표

현재 stage barrier는 유지하되, 내부적으로 lesson-level dependency scheduler를 추가한다.

즉 오케스트레이터는 아래를 하게 한다.

- 각 lesson job 생성
- job dependency 기록
- ready job 즉시 실행
- 완료 시 downstream unlock
- 모든 `html_card` 완료 후 global stage 시작

## 2차 목표

`stage_order` 중심 manifest 외에 `job_graph` 중심 manifest를 추가한다.

예:

- `job_manifest.json`
- `job_edges.json`

또는 하나의 manifest에:

- `jobs`
- `dependencies`
- `ready`
- `running`
- `completed`

를 포함한다.

## 3차 목표

대시보드도 stage 중심 표시에서 job dependency 중심 표시로 확장한다.

권장 표시 방식:

- 상단: 큰 흐름
  - `lesson pipeline`
  - `capture`
  - `compose`
  - `verify`
- 하단: 차시별 실제 job 흐름
  - `1차시 analysis -> review -> activity -> review -> html`
  - `2차시 ...`

## 오케스트레이터 변경 포인트

현재:

- stage 시작
- stage 전체 병렬 실행
- stage 전체 완료 대기
- 다음 stage 시작

변경 후:

- lesson job queue 생성
- dependency가 풀린 job만 즉시 실행
- 개별 job 완료 시 다음 job enqueue
- 모든 lesson-level `html_card` 완료 시 global queue 시작

즉 orchestrator는 `stage runner`보다 `job scheduler`에 가까워진다.

## 리스크

### 1. 구현 복잡도 증가

현재보다 dependency 관리가 복잡해진다.

### 2. status 집계 로직 재설계 필요

stage 단위 `running/succeeded`만으로는 부족해진다.

### 3. UI도 같이 손봐야 한다

lesson별 진행과 global 진행을 같이 보여줄 수 있어야 한다.

### 4. html_card 계약 확인 필요

현재 `html_card_agent`가 차시별 독립 실행에 완전히 맞는지 확인해야 한다.

## 권장 단계별 전환

### Step 1

`lesson_analysis -> lesson_review -> activity_plan -> activity_review`만 lesson-level pipelining 적용

`html_card`부터는 기존 barrier 유지

### Step 2

`html_card_agent`도 lesson-level로 분리

### Step 3

모든 lesson-level `html_card` 완료 후 `capture -> compose -> verify` 진입

## 결론

현재 구조는 동작은 하지만 최적은 아니다.  
특히 차시 수만큼 병렬 CLI를 이미 쓰고 있는 지금은, stage barrier 때문에 불필요하게 기다리는 시간이 생긴다.

더 좋은 구조는 아래다.

- 차시별 생성/검토/HTML 단계는 lesson-level로 독립 진행
- 전체 합성 단계만 global barrier 유지

즉 다음 리팩터링의 목표는:

`stage barrier pipeline -> lesson-level pipelined DAG`

로 전환하는 것이다.
