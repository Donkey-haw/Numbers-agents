# Agent Refactor Implementation Sequence

## 목적
- [AGENT_REFACTOR_TASK_BREAKDOWN.md](/Users/jonyeock/Desktop/Tool/NumbersAuto/AGENT_REFACTOR_TASK_BREAKDOWN.md) 의 작업 목록을 실제 구현 순서로 재정렬한다.
- 목표는 “무엇부터 손대야 가장 안전하게 진전되는가”를 명확히 하는 것이다.

## 구현 원칙
1. 먼저 계약을 고정하고 나중에 코드를 옮긴다.
2. 기존 동작 경로를 깨지 않는 얇은 래퍼부터 추가한다.
3. 한 번에 전체 리팩터링하지 않는다.
4. 항상 `textbook-only`와 기존 Gemini 경로를 생존시킨 상태로 진행한다.
5. review는 approval보다 먼저 구조화하되, 자동 승인 기능은 끝까지 넣지 않는다.

## 전체 우선순위

### 최우선
- run artifact root 통일
- stage/status/review 계약 고정
- orchestrator 골격 추가

### 중간 우선순위
- source parse stage 분리
- lesson/activity status 분리
- review stage 연결

### 후순위
- html stage 논리 분리
- freeform/stable/recovery mode 분리 강화
- compose/verify 세분화

## 권장 구현 순서

## Step 1. Run-Level 계약 먼저 고정

### 포함 작업
- `T0-1`
- `T0-2`
- `T0-3`
- `T1-1`
- `T1-2`

### 이유
- 이 단계가 없으면 이후 어떤 stage를 분리해도 저장 위치와 상태 표기가 제각각이 된다.
- 오케스트레이터를 추가하려면 먼저 run root와 status vocabulary가 필요하다.

### 구현 내용
- `artifacts/runs/<run_id>/...` 구조 확정
- `run_manifest.json` 필드 확정
- 공통 status enum / review decision enum 확정

### 병렬 가능 여부
- 가능
- 문서 작업과 schema 초안 작성은 병렬 가능

### 종료 신호
- run-level 문서가 완료됨
- `run_manifest.json` 초안 schema가 존재함
- status enum이 다른 문서와 충돌하지 않음

### 다음 단계로 넘어가는 조건
- 새 stage를 추가할 때 어디에 무엇을 저장하는지 더 이상 논쟁이 없어야 함

## Step 2. Source Parse 계약 고정

### 포함 작업
- `T2-1`
- `T2-2`
- `T2-3`
- `T2-4`
- `T2-5`

### 이유
- source parse는 가장 상류 단계라 여기부터 고정해야 이후 stage가 원본 PDF 대신 JSON contract를 읽게 만들 수 있다.
- lesson/activity 쪽 문제와 차시 파싱 문제를 분리하려면 가장 먼저 필요하다.

### 구현 내용
- `schedule_draft.json`
- `textbook_context.json`
- `runtime_config.json`
- `source_parse.status.json`
계약 확정

### 병렬 가능 여부
- 부분 가능
- `schedule_draft`와 `textbook_context` 문서는 병렬로 정리 가능
- `runtime_config`는 두 계약이 정리된 뒤 맞추는 편이 안전

### 종료 신호
- lesson stage가 `textbook_context.json`만 읽어도 되는 구조가 문서상 확정됨
- compose stage가 `runtime_config.json`만 읽는 구조가 문서상 확정됨

### 다음 단계로 넘어가는 조건
- lesson/activity stage 문서에서 원본 PDF 직접 읽기 의존이 제거돼야 함

## Step 3. Lesson Analysis Stage 분리

### 포함 작업
- `T3-1`
- `T3-2`
- `T3-3`
- `T3-4`

### 이유
- 현재 Gemini 경로의 첫 생성형 단계이며, downstream 영향이 크다.
- 여기서 raw/final/status/review를 분리하면 이후 activity stage도 같은 패턴으로 정리할 수 있다.

### 구현 내용
- `lesson_analysis_ai.json`
- `lesson_analysis.json`
- `lesson_analysis.status.json`
- `lesson_review.json`
계약 확정

### 병렬 가능 여부
- 낮음
- lesson final contract가 activity 입력이므로 순차 진행 권장

### 종료 신호
- activity stage 입력이 `lesson_analysis.json` 하나로 고정됨
- fallback/repair 여부가 status에서 보임
- review 결과가 구조화됨

### 다음 단계로 넘어가는 조건
- “lesson 분석 실패”와 “activity 실패”를 상태 파일만 보고 구분할 수 있어야 함

## Step 4. Activity Planning Stage 분리

### 포함 작업
- `T4-1`
- `T4-2`
- `T4-3`
- `T4-4`

### 이유
- 현재 가장 불안정한 단계다.
- freeform HTML 문제도 실은 이 단계와 HTML 단계 책임이 섞여 있어서 생긴다.

### 구현 내용
- `activity_plan_ai.json`
- `activity_plan.json`
- `activity_plan.status.json`
- `activity_review.json`
계약 확정

### 병렬 가능 여부
- 낮음
- lesson stage 이후 순차 진행 권장

### 종료 신호
- HTML stage가 `activity_plan.json`만 보고 렌더 가능
- `student_writing_zones`, `object_role`, `lesson_flow_stage`가 최종 계약에 고정
- repair/fallback 흐름이 status에 표현됨

### 다음 단계로 넘어가는 조건
- “Gemini가 틀렸다” 대신 “activity planning stage가 repair/fallback으로 종료됐다”라고 말할 수 있어야 함

## Step 5. Review Gating 규칙 확정

### 포함 작업
- `T7-1`
- `T7-2`

### 이유
- review 파일을 만들기만 하고 gating 규칙이 없으면 stage가 추가된 의미가 없다.
- approval과 review를 분리하지 않으면 나중에 자동 승인 사고가 날 수 있다.

### 구현 내용
- review와 approval 분리
- decision별 다음 행동 규칙 표

### 병렬 가능 여부
- 가능
- lesson/activity/manifest review의 common decision model은 병렬로 정리 가능

### 종료 신호
- `pass`, `pass_with_warning`, `needs_revision`, `blocked` 각각의 다음 행동이 문서상 확정됨

### 다음 단계로 넘어가는 조건
- 오케스트레이터가 review 결과만 보고 다음 분기를 정할 수 있어야 함

## Step 6. Orchestrator 골격 추가

### 포함 작업
- `T9-1`
- `T9-2`

### 이유
- 이제 계약이 정리됐으므로 기존 스크립트를 감싸는 얇은 orchestrator를 붙일 수 있다.
- 이 단계에서는 기존 worker 코드 로직을 뜯기보다 호출 순서와 artifact 저장만 통일하는 것이 핵심이다.

### 구현 내용
- `pipeline_orchestrator` 책임 경계 고정
- 모든 stage invocation 공통 인자 정의

### 병렬 가능 여부
- 낮음
- 앞선 계약 고정이 끝난 뒤 진행해야 충돌이 적음

### 종료 신호
- 오케스트레이터가 각 stage를 공통 인터페이스로 호출할 수 있는 수준의 계약이 확정됨

### 다음 단계로 넘어가는 조건
- run id, input refs, output dir, workflow mode가 모든 stage에서 공통으로 설명 가능해야 함

## Step 7. Render / Capture 계약 분리

### 포함 작업
- `T5-1`
- `T5-2`
- `T5-3`
- `T5-4`

### 이유
- 현재 HTML 문제와 compose 문제가 가까이 붙어 있어 실패 위치가 흐린다.
- 이 단계를 분리해야 freeform과 template fallback을 같은 언어로 다룰 수 있다.

### 구현 내용
- `html_assets.json`
- `html_render.status.json`
- `capture_assets.json`
- `capture.status.json`
계약 확정

### 병렬 가능 여부
- 부분 가능
- HTML asset 계약과 capture asset 계약은 병렬 정리 가능

### 종료 신호
- compose stage가 raw html 폴더를 스캔하지 않고 `capture_assets.json`만 읽는 구조가 문서상 확정됨

### 다음 단계로 넘어가는 조건
- HTML 위반과 capture 실패를 분리해서 기록할 수 있어야 함

## Step 8. Compose / Verify 계약 분리

### 포함 작업
- `T6-1`
- `T6-2`
- `T6-3`
- `T6-4`

### 이유
- 현재 사용자 체감상 마지막 실패는 대부분 “Numbers가 깨졌다”로 보인다.
- manifest review와 verify를 분리해야 compose 실패와 결과 검증 실패를 अलगाना 수 있다.

### 구현 내용
- `render_manifest.json`
- `numbers_insert.status.json`
- `manifest_review.json`
- `verify.status.json`
계약 확정

### 병렬 가능 여부
- 부분 가능
- manifest review와 verify 정의는 병렬로 초안 가능
- numbers_insert.status는 compose 계약 이후 맞추는 편이 안전

### 종료 신호
- AppleScript 실패, 배치 오류, 최종 시트 검증 실패가 서로 다른 파일로 남는다

### 다음 단계로 넘어가는 조건
- run summary만 봐도 실패 종류를 구분할 수 있어야 함

## Step 9. 운영 모드 분리

### 포함 작업
- `T8-1`
- `T8-2`
- `T8-3`

### 이유
- mode가 섞여 있으면 stable 작업에도 freeform 실험 규칙이 섞인다.
- 특히 지금은 stable과 freeform이 한 경로 안에 섞여 있는 편이라 운영상 혼란이 크다.

### 구현 내용
- Stable mode
- Freeform Experimental mode
- Recovery mode
각각의 허용 기능과 fallback 규칙 확정

### 병렬 가능 여부
- 가능
- 문서 정의 자체는 병렬 가능

### 종료 신호
- 어떤 실행이 어떤 mode인지 run manifest만 보면 알 수 있음
- mode별 검증 규칙 차이가 문서상 확정됨

### 다음 단계로 넘어가는 조건
- “왜 이번엔 freeform이고 왜 이번엔 template fallback인지”를 mode로 설명할 수 있어야 함

## 실제 구현 착수 추천 순서

### 1차 구현 묶음
- Step 1
- Step 2
- Step 3

### 이유
- 가장 적은 리스크로 큰 구조 이득을 얻는다.
- 아직 render/compose를 건드리지 않아도 lesson-level 실패를 분리할 수 있다.

### 2차 구현 묶음
- Step 4
- Step 5
- Step 6

### 이유
- activity/review/orchestrator가 연결되면서 실제 agent workflow 골격이 생긴다.

### 3차 구현 묶음
- Step 7
- Step 8
- Step 9

### 이유
- render/compose/mode 분리는 파급이 커서 뒤로 미는 편이 안전하다.

## 절대 하지 말아야 할 구현 순서

### 비권장 순서 1
- freeform HTML 분리부터 먼저 시작

### 이유
- 상위 계약이 없으면 다시 임시 경로와 임시 상태가 생긴다.

### 비권장 순서 2
- orchestrator를 먼저 크게 만들고 stage 계약을 나중에 맞춤

### 이유
- 오케스트레이터가 예외 처리 덩어리가 된다.

### 비권장 순서 3
- review agent를 마지막에 넣음

### 이유
- 그러면 다시 생성과 승인 흐름이 섞인다.

## 가장 현실적인 바로 다음 액션

### 바로 시작 가능한 구현 범위
1. run-level contract와 artifact root schema 초안
2. `source_parse.status.json`, `lesson_analysis.status.json`, `activity_plan.status.json` 초안
3. `lesson_review.json`, `activity_review.json`, `manifest_review.json` 초안
4. orchestrator 입력/출력 공통 인터페이스 정의

### 아직 바로 시작하지 않는 것이 좋은 범위
1. freeform HTML 전용 agent 분리 구현
2. compose 단계 전면 재작성
3. approval 자동화

## 최종 판단
- 구현 순서는 `계약 -> 상태 -> review -> orchestrator -> render/compose -> mode` 순서가 맞다.
- 이 순서를 지키면 현재 돌아가는 경로를 유지하면서도 점진적으로 agent workflow로 옮길 수 있다.
