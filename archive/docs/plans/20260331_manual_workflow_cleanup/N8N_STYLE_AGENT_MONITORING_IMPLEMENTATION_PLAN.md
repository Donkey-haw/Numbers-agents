# N8N-Style Agent Monitoring Implementation Plan

## 목표

현재 NumbersAuto 파이프라인을 n8n 스타일의 실시간 실행 화면과 연결한다.

사용자가 보고 싶은 것:
- 어떤 agent가 지금 실행 중인지
- 어떤 agent가 성공, 경고, fallback, 실패 상태인지
- 각 agent가 어떤 입력과 출력을 주고받는지
- lesson 단위 병렬 실행이 어떻게 진행되는지
- 최종 `.numbers`가 언제 생성되었는지

핵심 원칙:
- 현재 파이프라인을 바로 폐기하지 않는다.
- 먼저 `pipeline_orchestrator.py`를 event-producing runtime으로 확장한다.
- UI는 실행 엔진을 대체하지 않고, orchestrator의 상태를 시각화한다.
- 현재 hybrid 구조를 유지한다.
  - deterministic execution: source/render/capture/compose
  - AI execution: lesson/activity/review sidecars

## 목표 화면

화면 구조는 n8n과 비슷하게 4영역으로 나눈다.

1. 상단 실행 헤더
- 현재 run id
- config 이름
- 진행률
- 실행/중단/재시도 버튼
- 현재 workflow mode

2. 중앙 graph canvas
- agent node graph
- 노드 색상으로 상태 표시
  - pending
  - running
  - succeeded
  - succeeded_with_warning
  - failed_fallback_used
  - blocked
- lesson/activity는 차시별 sub-node 또는 stacked badge로 표시

3. 우측 detail panel
- 선택한 node의 상세 정보
- 입력 refs
- 출력 refs
- warnings
- errors
- fallback 여부
- 사용된 `AGENT.md`
- Gemini model / timeout / attempts

4. 하단 execution log panel
- 시간순 event stream
- start / finish / retry / fallback / warning
- stderr 또는 핵심 오류 요약

## 현재 파이프라인과 연결 지점

현재 진입점:
- `scripts/pipeline_orchestrator.py`

현재 실시간 표시 가능한 정보:
- `run_manifest.json`
- stage별 `*.status.json`
- review JSON
- prompt 파일
- output files

즉, 새 사이트는 처음부터 별도 state engine을 만들 필요가 없다.
우선은 orchestrator가 이미 알고 있는 상태를 event로 내보내면 된다.

## 제안 아키텍처

### 1. Backend Runtime Layer

새 컴포넌트:
- `orchestrator_event_bus.py`
- `run_event_store.py`
- `orchestrator_api.py`

역할:
- orchestrator 내부 stage 전환 시 event 발행
- event를 run memory + disk log에 기록
- frontend에 SSE 또는 WebSocket으로 전달

권장 초기 방식:
- `SSE`

이유:
- 서버 -> 클라이언트 단방향 push면 충분하다
- 구현이 WebSocket보다 단순하다
- 현재 use case는 chat이 아니라 execution stream이다

### 2. Event Schema

최소 event 타입:
- `run_created`
- `run_started`
- `stage_started`
- `stage_updated`
- `stage_finished`
- `lesson_started`
- `lesson_finished`
- `artifact_created`
- `warning_emitted`
- `fallback_used`
- `error_emitted`
- `run_finished`

권장 event shape:

```json
{
  "event_id": "evt_001",
  "run_id": "korean_6_1_unit1_related_to_life_reading-20260326-220856",
  "timestamp": "2026-03-26T13:08:56.222970+00:00",
  "event_type": "stage_started",
  "stage": "activity_plan_agent",
  "lesson_id": "4-6차시",
  "status": "running",
  "payload": {
    "agent_spec_path": "agents/activity_plan_agent/AGENT.md",
    "attempt_count": 1
  }
}
```

### 3. Disk Persistence

run별 event log:
- `artifacts/runs/<run_id>/events/run_events.jsonl`

장점:
- 새로고침해도 복구 가능
- 과거 실행 재생 가능
- UI replay 가능

### 4. API Layer

초기 필요한 API:
- `POST /api/runs`
  - 새 run 시작
- `GET /api/runs`
  - 최근 run 목록
- `GET /api/runs/:runId`
  - run summary
- `GET /api/runs/:runId/events`
  - 전체 event 목록
- `GET /api/runs/:runId/stream`
  - SSE stream
- `POST /api/runs/:runId/cancel`
  - 실행 중단

### 5. Frontend

권장 스택:
- React
- TypeScript
- Vite
- React Flow
- Zustand 또는 TanStack Query

React Flow를 쓰는 이유:
- n8n 스타일 node graph를 빠르게 구현 가능
- node 상태 색상, edge 표시, group 표현이 쉬움

### 6. Node 모델

고정 stage node:
- source_parse_agent
- lesson_analysis_agent
- review_lesson_agent
- activity_plan_agent
- review_activity_agent
- html_card_agent
- capture_agent
- numbers_compose_agent
- review_manifest_agent
- verify_agent

동적 child node:
- lesson analysis child nodes
- activity plan child nodes

예:
- `lesson_analysis_agent`
  - `1차시`
  - `2-3차시`
  - `4-6차시`

표시 전략:
- 초기 MVP: 상위 node 하나 + badge count
- 2단계: 펼치면 lesson child nodes 표시

## 실시간 상태 계산 방식

단일 truth source:
- event log + latest stage status

frontend는 다음을 계산한다.
- 각 node의 latest status
- 시작 시간 / 종료 시간
- 진행률
- warning 수
- fallback 수

## UI 세부 동작

### Node 상태 색상

- `pending`: gray
- `running`: blue pulsing
- `succeeded`: green
- `succeeded_with_warning`: amber
- `failed_fallback_used`: orange
- `blocked`: red

### Edge 스타일

- 미실행: dotted gray
- 진행 경로: solid blue
- 완료 경로: solid green
- 실패 경로: red

### Detail Panel 표시 항목

- agent name
- current status
- started / finished timestamp
- warnings / errors
- fallback_used
- agent spec path
- input refs
- output refs
- prompt path
- review JSON path

## 현재 코드에 필요한 구체 변경

### M1. Event Bus 도입

`pipeline_orchestrator.py`에 다음 호출 삽입:
- run 생성 시 `emit(run_created)`
- stage 시작 시 `emit(stage_started)`
- stage 종료 시 `emit(stage_finished)`
- fallback 기록 시 `emit(fallback_used)`
- warning 발생 시 `emit(warning_emitted)`

### M2. Status Writer 통합

현재는 stage마다 status JSON을 직접 쓴다.
이를 `status_and_event.py` 같은 공용 유틸로 통합한다.

목표:
- status 파일 갱신
- event 발행
- run_manifest summary 갱신

이 세 작업을 한 API에서 처리

### M3. Sub-stage Event

lesson/activity는 병렬 단위가 중요하므로 추가 event 필요:
- `lesson_started`
- `lesson_finished`

payload 예:
- lesson id
- fallback 여부
- review decision

### M4. API 서버 추가

새 디렉토리 제안:
- `app/server`
- `app/web`

server 역할:
- orchestrator subprocess 관리
- event stream 제공
- run replay API 제공

권장 초기 구현:
- FastAPI

이유:
- Python orchestrator와 가깝다
- SSE 구현이 쉽다
- subprocess 관리와 파일 접근이 단순하다

### M5. Web UI

권장 구조:
- `app/web/src/pages/RunsPage.tsx`
- `app/web/src/pages/RunDetailPage.tsx`
- `app/web/src/components/RunGraph.tsx`
- `app/web/src/components/NodeDetailPanel.tsx`
- `app/web/src/components/EventLogPanel.tsx`

## 단계별 구현 순서

### Phase 1. Observable Orchestrator

목표:
- UI 없이도 event JSONL이 쌓이게 만들기

완료 조건:
- full run 시 `events/run_events.jsonl` 생성
- stage 시작/종료/fallback/warning이 기록됨

### Phase 2. Run API

목표:
- CLI 대신 API로 run을 시작하고 추적

완료 조건:
- `POST /api/runs`로 새 run 시작 가능
- `GET /api/runs/:id/stream`으로 SSE 수신 가능

### Phase 3. Minimal Graph UI

목표:
- 현재 실행 상태를 graph로 표시

완료 조건:
- 중앙 node graph에서 stage 상태 변화가 실시간 반영됨
- detail panel에서 status JSON 정보 확인 가능

### Phase 4. Lesson-Level Subnodes

목표:
- lesson/activity 병렬 실행 현황 표시

완료 조건:
- `lesson_analysis_agent`, `activity_plan_agent`에 lesson subnode 표시
- fallback lesson이 눈에 띄게 표시됨

### Phase 5. Interactive Controls

목표:
- 실행 중단/재시도/아티팩트 열기

완료 조건:
- cancel 동작
- 실패 stage부터 resume
- output 열기

## 가장 먼저 구현해야 하는 것

우선순위:
1. event schema 고정
2. orchestrator event emitter
3. JSONL event persistence
4. SSE API
5. React Flow 기반 graph MVP

이 순서가 맞는 이유:
- UI보다 먼저 event contract가 고정돼야 한다
- event가 안정돼야 replay와 실시간 표시가 둘 다 가능하다

## 리스크

### 1. 이벤트 중복 기록

원인:
- status 파일과 event를 따로 관리

대응:
- 단일 writer 유틸로 통합

### 2. 병렬 lesson 상태 race

원인:
- lesson/activity 병렬 worker가 동시에 상태 갱신

대응:
- lesson 이벤트는 append-only jsonl
- run summary는 메인 스레드만 갱신

### 3. UI가 실행 엔진을 침범

원인:
- frontend 요구 때문에 orchestrator가 UI 친화적으로만 바뀌는 문제

대응:
- orchestrator는 event producer까지만
- UI는 consumer로 제한

## 성공 기준

- 사용자가 실행 중 어느 agent가 돌고 있는지 즉시 알 수 있다
- fallback이 발생하면 어느 lesson에서 왜 났는지 바로 보인다
- `.numbers` 생성 직전/직후 상태를 추적할 수 있다
- 새로고침해도 run 상태가 복원된다
- 과거 run도 replay 가능하다

## 현재 판단

지금은 `full AI orchestration`보다 `observable orchestration`이 먼저다.

즉 다음 실제 구현은:
- agent를 더 AI화하기 전에
- 현재 orchestrator를 event-driven runtime으로 확장하고
- n8n 스타일 시각화 UI를 붙이는 것이 맞다.
