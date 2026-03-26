# Agent-Based Numbers Refactor Plan

## 목적
- 현재의 `스크립트 중심 Numbers 자동 생성` 구조를 `에이전트 중심, JSON 계약 중심` 워크플로우로 개편하기 위한 실행 계획을 정의한다.
- 목표는 기능 추가가 아니라, 아래 4가지를 동시에 만족하는 구조로 재편하는 것이다.
  - 일관성
  - 재현 가능성
  - 단계별 디버깅 가능성
  - Gemini와 결정론 실행의 책임 분리

## 배경
- 현재 구조는 이미 `lesson_analysis.json`, `activity_plan.json`, `render_manifest.json` 같은 중간 JSON 아티팩트를 갖고 있다.
- 하지만 실제 실행 진입점은 여전히 스크립트 단위로 흩어져 있고, 다음 문제가 남아 있다.
  - 실패 위치가 사용자 입장에서 불명확함
  - Gemini 생성 실패와 render 실패와 Numbers 삽입 실패가 같은 “전체 실패”처럼 보임
  - review 단계가 오케스트레이터 바깥에 있음
  - freeform HTML과 fallback template이 같은 단계 안에서 섞여 있음

## 최종 목표 구조

### 목표 아키텍처
- 하나의 `pipeline_orchestrator`
- 6개 핵심 에이전트
  - `source_parse_agent`
  - `lesson_analysis_agent`
  - `activity_plan_agent`
  - `html_card_agent`
  - `numbers_compose_agent`
  - `verify_agent`
- 3개 review 에이전트
  - `review_lesson_agent`
  - `review_activity_agent`
  - `review_manifest_agent`
- 모든 단계는 JSON artifact만 주고받는다.

### 목표 실행 순서
1. `source_parse_agent`
2. `lesson_analysis_agent`
3. `review_lesson_agent`
4. `activity_plan_agent`
5. `review_activity_agent`
6. `html_card_agent`
7. `capture_agent`
8. `numbers_compose_agent`
9. `review_manifest_agent`
10. `verify_agent`

## 현재 코드와 목표 구조의 매핑

### 현재 스크립트
- [generate_numbers_lesson.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/generate_numbers_lesson.py)
- [generate_lesson_analysis.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/generate_lesson_analysis.py)
- [generate_activity_plan.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/generate_activity_plan.py)
- [render_activity_html.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/render_activity_html.py)
- [generate_numbers_with_activities.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/generate_numbers_with_activities.py)
- [run_gemini_cli_pipeline.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/run_gemini_cli_pipeline.py)
- [build_resource_index.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/build_resource_index.py)
- [build_unit_bundle.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/build_unit_bundle.py)
- [build_runtime_config.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/build_runtime_config.py)

### 목표 에이전트별 재배치

#### `source_parse_agent`
- 현재 재사용 대상:
  - `build_resource_index.py`
  - `build_unit_bundle.py`
  - `build_runtime_config.py`
  - `draft_config_from_progress_chart.py`
  - `parse_progress_chart_pdf.py`
  - `generate_numbers_lesson.py` 내부의 page inference 관련 로직
- 책임:
  - source scan
  - 진도표 구조화
  - 차시 경계 baseline
  - runtime config 생성

#### `lesson_analysis_agent`
- 현재 재사용 대상:
  - `generate_lesson_analysis.py`
  - `run_gemini_cli_pipeline.py` 의 lesson 단계
- 책임:
  - 차시 개념 해석
  - 오개념 추출
  - 목표 후보 생성

#### `activity_plan_agent`
- 현재 재사용 대상:
  - `generate_activity_plan.py`
  - `run_gemini_cli_pipeline.py` 의 activity 단계
- 책임:
  - 활동 의미 설계
  - object role / lesson flow / writing zone 메타데이터 생성

#### `html_card_agent`
- 현재 재사용 대상:
  - `render_activity_html.py`
  - `run_gemini_cli_pipeline.py` 의 freeform HTML path
- 책임:
  - 결정론 template render 또는 freeform HTML render normalize

#### `numbers_compose_agent`
- 현재 재사용 대상:
  - `generate_numbers_with_activities.py`
  - `generate_numbers_lesson.py`
- 책임:
  - 교과서/활동 asset 배치
  - manifest 구성
  - AppleScript Numbers 삽입

#### `verify_agent`
- 현재 재사용 대상:
  - `generate_numbers_lesson.py` 의 output verify
  - `generate_numbers_with_activities.py` 의 manifest/output verify

## 개편 원칙

### 1. “스크립트 호출”에서 “agent contract 실행”으로 바꾼다
- 각 스크립트는 더 이상 최종 사용자가 직접 기억해야 하는 진입점이 아니라,
  - 오케스트레이터 내부 stage worker
  로 취급한다.

### 2. 각 단계는 항상 3개 파일을 남긴다
- `*_ai.json` 또는 raw output
- `final *.json`
- `*.status.json`

### 3. review는 별도 stage로 끌어올린다
- 지금은 review가 문서/사람 판단에 가까운데, 이를 명시적 stage로 승격한다.
- 단, review agent는 승인자가 아니다.

### 4. freeform HTML은 activity planning과 논리적으로 분리한다
- 지금은 `activity_plan_agent`가 `html_content`까지 같이 생성하는 경우가 있다.
- 장기 목표는 아래처럼 쪼개는 것이다.
  - `activity_plan.json`: 의미 구조
  - `html_assets.json`: 시각 구조

## 반드시 먼저 고정해야 하는 계약

### A. run-level contract
- `run_manifest.json`
- 필수 필드:
  - `run_id`
  - `workflow_mode`
  - `config_path`
  - `selected_unit`
  - `selected_lessons`
  - `stage_order`
  - `final_status`

### B. lesson contract
- `lesson_analysis.json`
- 이 파일은 다음 단계를 위한 유일한 lesson 해석 입력이어야 한다.

### C. activity contract
- `activity_plan.json`
- 이 파일은 다음 단계를 위한 유일한 activity 설계 입력이어야 한다.

### D. render contract
- `html_assets.json`
- `capture_assets.json`
- `render_manifest.json`

## 개편 단계

## Phase 0. 계약 정리
- 목적:
  - 지금 있는 JSON을 agent contract로 재정의
- 해야 할 일:
  - 각 stage의 입력/출력 파일명 확정
  - status JSON shape 확정
  - review JSON shape 확정
- 완료 기준:
  - 어떤 stage가 어떤 파일만 읽고 어떤 파일만 쓰는지 문서로 고정

## Phase 1. 오케스트레이터 도입
- 목적:
  - 실행 순서를 하나의 진입점으로 통일
- 해야 할 일:
  - `pipeline_orchestrator` 설계
  - run id 기반 artifact root 생성
  - 단계별 status 집계
- 완료 기준:
  - 사용자 입장 진입점이 하나로 줄어듦

## Phase 2. source parse 분리
- 목적:
  - PDF/진도표/보조교재 파싱을 독립 stage로 고정
- 해야 할 일:
  - `resource_index -> unit_bundle -> runtime_config` 흐름을 기본 경로로 승격
  - title-only direct config는 fallback 모드로 재정의
- 완료 기준:
  - 차시 파싱 문제와 activity 생성 문제가 분리됨

## Phase 3. lesson analysis stage 고정
- 목적:
  - Gemini lesson analysis를 명확한 agent로 분리
- 해야 할 일:
  - `lesson_analysis_ai.json`
  - `lesson_analysis.json`
  - `lesson_analysis.status.json`
  - `lesson_review.json`
  를 표준화
- 완료 기준:
  - lesson stage만 독립 재실행 가능

## Phase 4. activity planning stage 고정
- 목적:
  - activity planning을 review/fallback 포함한 독립 agent로 정리
- 해야 할 일:
  - repair pass와 fallback을 status에 기록
  - `activity_review.json` 도입
- 완료 기준:
  - “Gemini가 틀렸다”가 아니라 “activity planning stage failed/fallback”으로 보이게 됨

## Phase 5. html stage 분리
- 목적:
  - activity 의미와 HTML 표현을 분리
- 해야 할 일:
  - `html_assets.json` 표준화
  - template mode / freeform mode 구분
  - normalize 결과를 별도 status에 남김
- 완료 기준:
  - HTML 위반과 activity 의미 위반이 분리됨

## Phase 6. compose/verify stage 분리
- 목적:
  - render와 Numbers 삽입과 최종 검증을 독립 stage로 고정
- 해야 할 일:
  - `numbers_insert.status.json`
  - `manifest_review.json`
  - `verify.status.json`
  표준화
- 완료 기준:
  - AppleScript 실패가 planning 실패와 섞이지 않음

## 운영 모드 개편

### Mode 1. Stable
- 기본 모드
- 특징:
  - template renderer 우선
  - Gemini는 lesson/activity planning만 담당
  - review required
- 용도:
  - 실제 수업용 제작

### Mode 2. Freeform Experimental
- 특징:
  - freeform HTML 허용
  - validation 강화
  - fallback 허용
- 용도:
  - 디자인 탐색

### Mode 3. Recovery
- 특징:
  - lesson/activity 실패 시 빠른 fallback
  - Numbers 결과 생성 자체를 우선
- 용도:
  - 긴급 산출물 확보

## review 단계 개편

### 왜 필요한가
- 현재 구조에서는 review가 사람 판단과 stage validation 사이에 끼어 있다.
- 개편 후에는 review도 stage로 승격해야 전체 상태가 일관된다.

### review 단계 역할
- `review_lesson_agent`
  - 교과서 근거 검토
- `review_activity_agent`
  - ACTIVITY_RULE / NumbersDesign 검토
- `review_manifest_agent`
  - before/during/after 흐름과 배치 검토

### 중요한 제약
- review agent는 승인자가 아니다.
- review agent는 다음만 할 수 있다.
  - `pass`
  - `pass_with_warning`
  - `needs_revision`
  - `blocked`

## 권장 디렉토리 개편

```text
artifacts/
  runs/
    <run_id>/
      run_manifest.json
      source/
      sections/
        <lesson_id>/
      render/
      output/
```

### 이유
- 현재 `artifacts/gemini/...`, `output/analysis/...`, `output/plans/...` 처럼 경로가 분산돼 있다.
- agent 구조에서는 run root 기준으로 정리해야 디버깅과 재실행이 쉬워진다.

## 성능 관점에서의 개편 판단

### 좋아지는 점
- 차시별 재실행이 쉬워진다.
- validation 실패를 국소화할 수 있다.
- artifact cache 재사용이 쉬워진다.
- review와 compose 실패를 분리할 수 있다.

### 느려질 수 있는 점
- review agent 추가
- html stage 분리
- status/review artifact 저장 증가

### 따라서 필요한 운영 원칙
- AI agent는 꼭 필요한 단계에만 둔다.
- capture / compose / verify는 결정론 실행기로 유지한다.
- freeform HTML은 기본 모드가 아니라 실험 모드로 둔다.

## 현재 코드베이스 기준 우선순위

### 1순위
- 오케스트레이터와 artifact root 구조 통합

### 2순위
- lesson / activity / render / compose / verify status JSON 표준화

### 3순위
- review agent 도입

### 4순위
- html stage 논리 분리

### 5순위
- freeform mode와 stable mode 완전 분리

## 비권장 개편 방향

### 1. 모든 단계를 AI agent화
- 비권장 이유:
  - 느림
  - 불안정
  - 책임 불명확

### 2. 기존 스크립트를 한 번에 전부 갈아엎기
- 비권장 이유:
  - 회귀 위험
  - 현재 동작 경로까지 같이 깨질 수 있음

### 3. review와 approval 혼합
- 비권장 이유:
  - 자동 승인 오류가 발생하면 회복이 어려움

## 성공 기준

### 구조 기준
- 모든 stage가 고정된 JSON 계약으로 통신한다.
- stage별 status JSON이 항상 남는다.
- review JSON이 별도 stage로 존재한다.

### 운영 기준
- 한 차시 실패가 전체 run 실패와 구분된다.
- 특정 stage부터 재실행 가능하다.
- 사용자에게 실패 위치를 설명할 수 있다.

### 품질 기준
- `lesson_analysis` 문제
- `activity_plan` 문제
- `html` 문제
- `compose` 문제
- `verify` 문제
를 서로 다른 failure type으로 구분 가능해야 한다.

## 최종 권장안
- 이 개편은 “새 시스템을 다시 만드는 작업”으로 가면 안 된다.
- 가장 현실적인 방향은 현재 구조를 아래 순서로 감싸는 것이다.
  1. JSON 계약 고정
  2. status/review stage 추가
  3. orchestrator 통합
  4. html stage 분리
  5. mode 분리

## 한 줄 요약
- 이 개편안의 핵심은 `Gemini를 더 많이 쓰는 것`이 아니라, **현재 Numbers 자동 생성 파이프라인을 agent-stage JSON workflow로 재구성해, 실패와 검토와 fallback을 구조적으로 통제 가능하게 만드는 것**이다.
