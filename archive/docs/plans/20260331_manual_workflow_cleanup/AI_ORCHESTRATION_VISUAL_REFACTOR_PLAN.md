# AI Orchestration Visual Refactor Plan

## 목적
- 현재의 `파이썬 stage worker 중심` 파이프라인을 `AI agent 중심 orchestrator` 구조로 재편한다.
- 모든 agent의 진행 상태를 실시간으로 시각화한다.
- 사용자는 n8n 같은 노드 그래프 화면에서 현재 어느 agent가 무엇을 하고 있는지 본다.

## 전제
- 이 계획은 **구현 계획 문서**다.
- 지금 즉시 전부 AI agent로 바꾸는 것이 아니라, **일관성을 잃지 않도록 orchestration 규약부터 고정**하는 것이 목적이다.
- `source_parse`까지 완전 자유형 AI에 맡기는 것은 변동성이 크므로, AI agent가 하더라도 **반드시 구조화된 출력 계약과 review gate**를 둔다.

## 목표 상태

### 1. 실행 구조
- 사용자는 하나의 실행 요청만 보낸다.
- 중앙 orchestrator가 agent graph를 실행한다.
- 각 agent는 JSON 입력을 받고 JSON 출력만 남긴다.
- 모든 agent는 상태 이벤트를 stream으로 발행한다.

### 2. 시각화 구조
- 화면에는 노드 그래프가 보인다.
- 각 node는 하나의 agent 또는 tool stage를 뜻한다.
- 간선은 입력/출력 dependency를 뜻한다.
- 상태는 실시간으로 바뀐다.
  - `pending`
  - `queued`
  - `running`
  - `waiting_tool`
  - `needs_review`
  - `succeeded`
  - `fallback_used`
  - `failed`
  - `blocked`

### 3. 사용자 경험
- 현재 실행 중인 agent를 색과 애니메이션으로 본다.
- 클릭하면:
  - 입력 JSON
  - 출력 JSON
  - 경고
  - fallback 이유
  - 사용 모델
  - 실행 시간
  - 로그
  를 본다.
- 하단 패널에는 최신 이벤트 로그가 스트리밍된다.

## 핵심 설계 결정

## 1. “모든 agent를 AI로”의 의미

이 계획에서 `모든 agent를 AI 기반`으로 만든다는 뜻은 아래와 같이 정의한다.

### 허용
- 각 단계의 핵심 판단을 AI가 수행
- agent가 tool 호출 계획을 세움
- agent가 repair/fallback 판단을 제안
- agent가 review 결과를 생성

### 금지
- agent가 파일 구조를 제멋대로 바꿈
- agent가 JSON 계약 없이 자유 텍스트만 남김
- agent가 Numbers 삽입 같은 결정론 실행을 직접 대화형으로 처리

즉,
- **판단은 AI**
- **실행과 상태 기록은 orchestrator/runtime**

으로 나눈다.

## 2. 목표 agent graph

### Core agents
1. `source_parse_agent`
2. `boundary_inference_agent`
3. `resource_match_agent`
4. `lesson_analysis_agent`
5. `lesson_review_agent`
6. `activity_plan_agent`
7. `activity_review_agent`
8. `html_card_agent`
9. `html_review_agent`
10. `capture_agent`
11. `numbers_compose_agent`
12. `manifest_review_agent`
13. `verify_agent`

### Controller agents
1. `run_controller_agent`
2. `fallback_controller_agent`
3. `human_review_gate_agent`

## 3. 권장 graph 구조

```text
run_controller
  -> source_parse
  -> boundary_inference
  -> resource_match
  -> lesson_analysis (parallel per lesson)
  -> lesson_review (parallel per lesson)
  -> activity_plan (parallel per lesson)
  -> activity_review (parallel per lesson)
  -> html_card (parallel per lesson)
  -> html_review (parallel per lesson)
  -> capture (batched or serial)
  -> numbers_compose
  -> manifest_review
  -> verify
```

## 4. 병렬화 규칙

### 병렬 허용
- `lesson_analysis_agent`
- `lesson_review_agent`
- `activity_plan_agent`
- `activity_review_agent`
- `html_card_agent`
- 필요 시 `html_review_agent`

### 직렬 유지
- `source_parse_agent`
- `boundary_inference_agent`
- `resource_match_agent`
- `numbers_compose_agent`
- `verify_agent`

### 반직렬
- `capture_agent`
  - 브라우저/시스템 상태 때문에 소수 batch 병렬만 허용

## 5. 출력 계약

모든 agent는 아래 3층 출력 계약을 갖는다.

### A. result JSON
- 실제 다음 단계가 읽는 산출물

### B. status JSON
- 상태, 시간, model, fallback, tool usage

### C. event stream
- UI가 실시간으로 구독하는 이벤트

## 6. event schema

실시간 UI를 위해 이벤트를 아래처럼 표준화한다.

```json
{
  "run_id": "run-20260326-001",
  "node_id": "activity_plan:7-8차시",
  "agent_type": "activity_plan_agent",
  "status": "running",
  "timestamp": "2026-03-26T12:00:00+09:00",
  "progress": 0.4,
  "message": "Prompt sent to model",
  "input_ref": "sections/7-8차시/lesson_analysis.json",
  "output_ref": null,
  "model": "gemini",
  "fallback_used": false,
  "warnings": []
}
```

## 7. UI 구성

## 7.1 화면 레이아웃

### 좌측/중앙
- 노드 그래프 캔버스
- drag/zoom 가능
- 각 lesson node는 group 또는 subgraph로 묶음

### 우측 패널
- 선택한 node 상세
  - 입력
  - 출력
  - 최근 이벤트
  - fallback 이유
  - elapsed time

### 하단 패널
- 실행 로그 타임라인
- 전체 run 요약
- active agents 수
- pending / succeeded / failed 카운트

## 7.2 노드 상태 표현

- `pending`: 회색
- `queued`: 옅은 파랑
- `running`: 초록 pulse
- `waiting_tool`: 노랑
- `needs_review`: 주황
- `fallback_used`: 보라
- `failed`: 빨강
- `blocked`: 진한 빨강
- `succeeded`: 초록 체크

## 7.3 실행 단위

node granularity는 두 레벨을 지원해야 한다.

### Level 1. stage view
- `lesson_analysis_agent`
- `activity_plan_agent`
- `numbers_compose_agent`

### Level 2. lesson instance view
- `lesson_analysis: 1차시`
- `lesson_analysis: 2-3차시`
- `activity_plan: 1차시`

처음엔 Level 1만 보여 주고, 확대 시 Level 2로 drill-down 하는 구성이 가장 현실적이다.

## 8. 시스템 구성안

## 8.1 런타임 구성

### Backend
- Python orchestrator service
- agent execution runtime
- event broker
- artifact store

### Frontend
- graph UI web app
- websocket or SSE subscriber

### Storage
- run metadata store
- artifact file store
- optional vector or memory store

## 8.2 권장 기술

### Backend
- 기존 Python 유지
- 새 service 계층 추가
  - `orchestrator_server.py`
  - `event_bus.py`
  - `agent_runtime.py`

### Frontend
- React + node-graph library
- 후보:
  - React Flow
  - xyflow 계열

### Realtime transport
- 1차: SSE
- 2차: WebSocket

초기엔 SSE가 더 단순하다.

## 9. 구현 전략

## Phase 1. 시각화만 먼저
- 현재 stage worker 구조 유지
- UI는 기존 status JSON을 polling or SSE로 보여 줌
- 아직 모든 agent를 AI로 바꾸지 않음

### 목표
- 현재 파이프라인도 실시간 그래프에서 보이게 만들기

### 완료 조건
- `source -> lesson -> activity -> render -> capture -> compose -> verify`가 화면에 실시간으로 보임

## Phase 2. event bus 도입
- 각 stage가 status JSON만 쓰는 것이 아니라 event도 발행
- orchestrator가 중앙 상태 저장

### 완료 조건
- UI가 filesystem polling 없이 실시간 반응

## Phase 3. lesson/activity agent 완전 AI orchestration
- 현재 AI planning agent를 true agent runtime으로 승격
- 각 lesson/activity agent가 tool-aware execution을 수행

### 완료 조건
- lesson/activity는 완전 agent execution trace를 가짐

## Phase 4. source/boundary/resource도 AI-assisted agent화
- 다만 결과는 반드시 constrained JSON으로 반환
- deterministic reviewer가 검증

### 완료 조건
- 초기 단계도 AI가 제안하되 재현 가능성을 잃지 않음

## Phase 5. human review gate UI
- 특정 node가 `needs_review`면 UI에서 승인/수정
- 승인 후 downstream 재개

### 완료 조건
- 애매한 boundary/supplement/activity를 화면에서 바로 승인 가능

## Phase 6. full AI orchestration mode
- `run_controller_agent`가 전체 DAG를 실행
- 각 node는 AI agent runtime + tool runner로 동작

### 완료 조건
- 현재 목표인 “full orchestration” 달성

## 10. 가장 중요한 위험

## 10.1 변동성 증가
- 모든 단계를 AI로 바꾸면 결과 흔들림이 늘어난다.

대응:
- constrained JSON
- deterministic post-check
- explicit fallback

## 10.2 시각화와 실제 상태 불일치
- UI만 화려하고 실제 상태는 늦게 반영될 수 있다.

대응:
- event stream을 단일 진실 원천으로 사용
- UI는 JSON artifact를 직접 쓰지 않고 event store를 기준으로 그림

## 10.3 agent 간 계약 붕괴
- 서로 다른 agent가 다른 shape의 JSON을 내면 전체가 무너진다.

대응:
- schema versioning
- node별 contract tests

## 10.4 운영 복잡도 급증
- AI runtime, queue, event bus, web UI를 한 번에 넣으면 과도하다.

대응:
- UI 먼저
- event bus 다음
- AI full orchestration은 마지막

## 11. 권장 구현 순서

1. 현재 파이프라인을 시각화하는 UI부터 만든다.
2. stage status를 event stream으로 바꾼다.
3. lesson/activity만 true AI agent runtime으로 바꾼다.
4. source/boundary/resource는 나중에 AI-assisted로 올린다.
5. human review gate를 붙인다.
6. 마지막에 full AI orchestration 모드를 연다.

## 12. 이번 계획의 결론

지금 당장 가장 현실적인 시작점은 이것이다.

- **Step 1:** 현재 Python orchestrator를 유지
- **Step 2:** 실시간 agent graph UI를 먼저 구현
- **Step 3:** event bus를 붙여서 실행 상태를 실시간 stream
- **Step 4:** lesson/activity agent부터 true AI runtime으로 승격

즉, 먼저 **보이게 만들고**, 그 다음 **AI화 범위를 넓히는** 순서가 맞다.
