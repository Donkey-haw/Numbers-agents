# CLI Agent Runtime Plan

## 목표

오케스트레이터는 agent 로직을 직접 수행하지 않고, job 스케줄러 역할만 담당한다.

각 agent는 필요할 때 독립 CLI 환경에서 실행한다.

- `python` runner
- `gemini` runner
- `codex` runner

이 구조의 목적은 다음이다.

- 생성/해석 단계의 실제 병렬 실행
- agent별 실패 격리
- runner 및 모델 교체 용이성 확보
- stage별 모델 품질/비용/속도 최적화

## 핵심 원칙

1. 성능 이득이 큰 agent만 실제 분리한다.
2. deterministic 작업은 로컬 Python runtime으로 유지한다.
3. 모든 agent는 파일 contract로만 입출력한다.
4. agent별 runner와 모델은 명시적으로 설정한다.
5. 병렬화는 lesson/job 단위가 생긴 뒤에만 적용한다.

## 분리 대상

### 1차 분리 대상

- `lesson_analysis_agent`
- `activity_plan_agent`
- `activity_review_agent`

이유:

- 처리 시간이 길다.
- 이미 lesson 단위 job 구조가 있다.
- 병렬 실행 효과가 크다.

### 2차 분리 대상

- `curriculum_alignment_agent`
- `differentiation_agent`
- `review_manifest_agent`

### 로컬 유지 대상

- `validate-page-map`
- `manual source artifact preparation`
- `html_card_agent`
- `capture_agent`
- `numbers_compose_agent`
- `verify_agent`

이유:

- 주로 deterministic 작업이다.
- CLI 분리 오버헤드 대비 이득이 작다.

## 목표 실행 구조

### Orchestrator

역할:

- stage DAG 관리
- job 생성
- 병렬도 제어
- retry / cancel / timeout 정책 적용
- stage 상태와 job 상태 집계

### Agent Runner

공용 실행기 `agent_runner.py`를 둔다.

역할:

- job spec 로드
- runner 종류 선택
- subprocess 실행
- stdout / stderr 저장
- timeout / idle timeout 적용
- output artifact 존재 여부와 schema 검증

### Agent Job

각 agent 실행은 job spec으로 표현한다.

예시:

```json
{
  "job_id": "lesson-analysis-사회_1차시__1차시",
  "stage": "lesson_analysis_agent",
  "runner": "gemini",
  "model": "gemini-2.5-pro",
  "input_path": "artifacts/runs/<run_id>/jobs/lesson-analysis-사회_1차시__1차시.input.json",
  "output_path": "artifacts/runs/<run_id>/jobs/lesson-analysis-사회_1차시__1차시.output.json",
  "status_path": "artifacts/runs/<run_id>/jobs/lesson-analysis-사회_1차시__1차시.status.json",
  "stdout_log": "artifacts/runs/<run_id>/jobs/lesson-analysis-사회_1차시__1차시.stdout.log",
  "stderr_log": "artifacts/runs/<run_id>/jobs/lesson-analysis-사회_1차시__1차시.stderr.log",
  "timeout_sec": 0,
  "idle_timeout_sec": 180
}
```

## Runner 종류

### `python` runner

대상:

- deterministic processing
- validation
- manifest build
- compose/verify

실행 예:

```bash
python3 scripts/activity_review_agent.py --single-lesson ...
```

### `gemini` runner

대상:

- lesson meaning analysis
- activity generation
- curriculum alignment

실행 예:

```bash
gemini --model gemini-2.5-pro
```

또는 wrapper를 통해:

```bash
python3 scripts/agent_runner.py --runner gemini --model gemini-2.5-pro ...
```

### `codex` runner

대상:

- review / repair
- bounded planning
- structured rewrite
- 일부 activity generation 실험

실행 예:

```bash
codex --model gpt-5.4-mini
```

또는 wrapper를 통해:

```bash
python3 scripts/agent_runner.py --runner codex --model gpt-5.4-mini ...
```

## 모델 설정 전략

각 runner는 agent별로 별도 모델을 갖는다.

즉, 전역 모델 하나가 아니라 stage/agent별 모델 지정이 필요하다.

### 권장 모델 매트릭스

#### 생성/해석

- `lesson_analysis_agent`
  - runner: `gemini`
  - primary model: `gemini-2.5-pro`
  - fallback model: `gemini-2.5-flash`

- `activity_plan_agent`
  - runner: `gemini`
  - primary model: `gemini-2.5-pro`
  - fallback model: `gemini-2.5-flash`

#### 검토/리뷰

- `activity_review_agent`
  - runner: `codex`
  - primary model: `gpt-5.4-mini`
  - fallback model: `python`

- `lesson_review_agent`
  - runner: `codex`
  - primary model: `gpt-5.4-mini`
  - fallback model: `python`

#### deterministic

- `html_card_agent`
  - runner: `python`

- `capture_agent`
  - runner: `python`

- `numbers_compose_agent`
  - runner: `python`

- `verify_agent`
  - runner: `python`

## 설정 파일 형태

권장:

`agent_runtime.config.json`

예시:

```json
{
  "defaults": {
    "max_parallel_jobs": 2,
    "timeout_sec": 0,
    "idle_timeout_sec": 180
  },
  "agents": {
    "lesson_analysis_agent": {
      "runner": "gemini",
      "model": "gemini-2.5-pro",
      "fallback_runner": "gemini",
      "fallback_model": "gemini-2.5-flash",
      "max_parallel_jobs": 2,
      "timeout_sec": 0,
      "idle_timeout_sec": 180
    },
    "activity_plan_agent": {
      "runner": "gemini",
      "model": "gemini-2.5-pro",
      "fallback_runner": "gemini",
      "fallback_model": "gemini-2.5-flash",
      "max_parallel_jobs": 2,
      "timeout_sec": 0,
      "idle_timeout_sec": 240
    },
    "lesson_review_agent": {
      "runner": "codex",
      "model": "gpt-5.4-mini",
      "fallback_runner": "python",
      "max_parallel_jobs": 4
    },
    "activity_review_agent": {
      "runner": "codex",
      "model": "gpt-5.4-mini",
      "fallback_runner": "python",
      "max_parallel_jobs": 4
    },
    "capture_agent": {
      "runner": "python"
    },
    "numbers_compose_agent": {
      "runner": "python"
    }
  }
}
```

## 오케스트레이터 변경 계획

### 현재

- 오케스트레이터가 Python 모듈을 직접 호출하거나
- 일부 agent만 ad-hoc subprocess wrapper를 사용한다.

### 목표

- 오케스트레이터는 `agent_runner.py`에 job spec만 넘긴다.
- 실제 실행은 runner가 맡는다.

## 1차 구현 계획

### Step 1. `agent_runner.py` 도입

포함 기능:

- runner 선택
- 모델 선택
- input/output/status/log 경로 관리
- timeout / idle timeout
- 종료코드 처리

### Step 2. 현재 subprocess worker 3개 이관

- `lesson_analysis_agent`
- `activity_plan_agent`
- `activity_review_agent`

목표:

- agent별 ad-hoc wrapper 제거
- 공통 runner로 통일

### Step 3. job manifest 추가

파일:

- `artifacts/runs/<run_id>/job_manifest.json`

포함 정보:

- job id
- stage
- lesson id
- runner
- model
- status
- started_at
- finished_at
- fallback_used

## 2차 구현 계획

### Step 4. runner backend 분리

- `python_runner`
- `gemini_runner`
- `codex_runner`

### Step 5. agent별 runner 지정

예:

- `lesson_analysis_agent` -> `gemini`
- `activity_plan_agent` -> `gemini`
- `activity_review_agent` -> `codex`

### Step 6. fallback / escalation 정책 추가

예:

- Gemini 실패 -> Gemini lower-tier model
- Codex failure -> Python deterministic review

## 3차 구현 계획

### Step 7. 대시보드 job manifest 연동

보여줄 정보:

- stage별 병렬 job 수
- runner 종류
- 모델명
- fallback 여부

### Step 8. 운영 최적화

- subject별 모델 매트릭스 분리
- 국어 / 사회 / 수학 별 정책 분기
- 비용/속도/품질 측정 자동화

## 리스크

1. 모든 agent를 CLI로 분리하면 오버헤드가 커질 수 있다.
2. deterministic 작업까지 runner화하면 오히려 느려질 수 있다.
3. Codex/Gemini 출력 구조 차이를 schema로 강제하지 않으면 운영성이 떨어진다.
4. timeout보다 idle-timeout 기반 정책이 더 적합할 수 있다.

## 권장 결론

1. 생성/해석 계층만 먼저 실제 CLI runner로 분리한다.
2. runner와 모델은 agent별로 개별 설정한다.
3. `numbers_compose`, `capture`, `verify`는 당분간 Python 유지가 맞다.
4. 첫 구현은 `agent_runner.py + agent_runtime.config.json`이다.

이 계획의 핵심은 “모든 것을 agent화”가 아니라,
“실제 성능 이득이 나는 agent를 독립 CLI job으로 분리하고, 각 job의 모델을 개별 설정 가능하게 만드는 것”이다.
