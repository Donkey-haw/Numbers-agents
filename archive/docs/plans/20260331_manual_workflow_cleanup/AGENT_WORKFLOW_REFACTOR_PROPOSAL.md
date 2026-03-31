# Agent Workflow Refactor Proposal

## 목적

현재 NumbersAuto의 agent 기반 파이프라인을 "각 agent가 최소 책임 단위만 맡는다"는 기준으로 다시 정리한다.

이 문서는 아래를 다룬다.

- 현재 구조의 장점
- 현재 구조의 경계 문제
- 권장 agent 분해안
- 권장 workflow
- 상태 모델 정리 방향
- 최소 수정 우선순위


## 현재 구조 평가

현재 파이프라인의 큰 방향은 좋다.

기본 흐름:

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

이 구조의 장점:

- source -> lesson -> activity -> render -> capture -> compose -> verify 흐름이 자연스럽다.
- run-root 아래에 단계별 산출물이 남아 디버깅이 쉽다.
- `stop-after` 방식으로 부분 실행 테스트가 가능하다.
- lesson/activity 단계는 lesson 단위 병렬화가 가능하도록 설계돼 있다.

즉, "실행 파이프라인 분리"는 비교적 잘 되어 있다.


## 현재 구조의 핵심 문제

문제는 "최소 책임 단위 분리" 기준에서는 아직 agent 경계가 크다는 점이다.

### 1. `source_parse_agent`가 너무 많은 책임을 가진다

현재 이 단계는 사실상 아래를 한 번에 수행한다.

- 입력 config 확정
- 페이지 범위 추론
- 멀티리소스 정책 적용
- 구조 검토
- 경계 검토
- 보조자료 검토
- AI sidecar review

즉 하나의 agent가 planner, resolver, validator, reviewer 역할을 동시에 갖는다.

이 구조에서는 source 단계가 실패할 때 원인 분리가 어렵고, 실제로도 전체 run이 첫 단계에서 쉽게 차단된다.

### 2. `review_lesson_agent`, `review_activity_agent`가 실제 독립 agent가 아니다

문서상 stage로 보이지만, 실제 구현에서는 상위 생성 agent 내부의 후처리 산출물이다.

결과적으로:

- 그래프상 stage는 분리되어 보인다.
- 실제 책임은 생성 agent 내부에 묶여 있다.

즉 모니터링 단위와 실행 단위가 어긋난다.

### 3. 생성, 검증, 복구가 한 agent 안에 섞여 있다

특히 `lesson_analysis_agent`, `activity_plan_agent`는 다음을 함께 수행한다.

- prompt 구성
- Gemini 호출
- 정규화
- review 생성
- repair 또는 fallback

실무적으로는 편하지만, 최소 단위 기준으로는 역할이 섞여 있다.

### 4. stage 상태 모델이 실제 실행 단위와 완전히 맞지 않는다

일부 stage는 `running` 전이가 명확하고, 일부는 결과만 반영된다.

이 문제는 보통 "실행 단위가 불명확한 상태"에서 나타난다.


## Agent 설계 원칙

권장 기준은 단순하다.

각 agent는 아래 셋 중 하나만 하게 둔다.

1. 결정한다
2. 생성한다
3. 검증한다

복구가 필요하면 `repair agent`를 별도로 둔다.

이 기준을 따르면:

- 실패 원인 추적이 쉬워진다.
- fallback 사용량을 별도 집계할 수 있다.
- review가 실제 독립 실행 주체가 된다.
- 모니터링 그래프와 실행 단위가 일치한다.


## 권장 Workflow

권장 stage 순서:

1. `config_intake_agent`
2. `source_boundary_agent`
3. `source_validation_agent`
4. `lesson_analysis_agent`
5. `lesson_review_agent`
6. `activity_plan_agent`
7. `activity_review_agent`
8. `activity_repair_agent`
9. `html_card_agent`
10. `render_manifest_agent`
11. `render_review_agent`
12. `capture_agent`
13. `numbers_compose_agent`
14. `numbers_verify_agent`
15. `run_summary_agent`


## Agent별 권장 책임

### 1. `config_intake_agent`

역할:

- 입력 config 정규화
- 교과서/보조자료 경로 확인
- lesson 목록과 기본 메타데이터 확정

입력:

- `configs/<config>.json`

출력:

- `source/input_config.normalized.json`
- `source/config_intake.status.json`

비고:

현재 `source_parse_agent`에 들어 있는 "입력 config 확정" 책임을 떼어내는 단계다.


### 2. `source_boundary_agent`

역할:

- 차시별 교과서/보조자료 페이지 범위 계산
- deterministic rule 기반 경계 확정

입력:

- `source/input_config.normalized.json`

출력:

- `source/runtime_config.json`
- `source/source_boundary.status.json`

하지 말아야 할 일:

- 의미 분석을 하지 않는다.
- AI review를 하지 않는다.
- 품질 판정까지 같이 하지 않는다.


### 3. `source_validation_agent`

역할:

- source boundary 결과 검토
- 구조 문제, 경계 모호성, 보조자료 누락 검출

입력:

- `source/runtime_config.json`

출력:

- `source/config_quality_review.json`
- `source/boundary_review.json`
- `source/supplement_review.json`
- `source/source_validation.status.json`

비고:

현재 `source_parse_agent` 내부 review 로직을 별도 단계로 분리한 형태다.


### 4. `lesson_analysis_agent`

역할:

- lesson별 의미 분석 생성

입력:

- `source/runtime_config.json`

출력:

- `sections/<lesson>/lesson_analysis.json`
- `sections/<lesson>/lesson_analysis.status.json`

하지 말아야 할 일:

- review를 생성하지 않는다.
- source 경계를 다시 바꾸지 않는다.


### 5. `lesson_review_agent`

역할:

- lesson analysis 필수 필드와 구조를 검증

입력:

- `sections/<lesson>/lesson_analysis.json`

출력:

- `sections/<lesson>/lesson_review.json`
- `sections/<lesson>/lesson_review.status.json`

비고:

현재 stage 이름만 존재하는 review를 실제 독립 실행 단위로 승격한다.


### 6. `activity_plan_agent`

역할:

- lesson analysis 기반 활동 계획 생성

입력:

- `sections/<lesson>/lesson_analysis.json`

출력:

- `sections/<lesson>/activity_plan.json`
- `sections/<lesson>/activity_plan.status.json`

하지 말아야 할 일:

- repair를 내부에서 수행하지 않는다.
- review를 내부에서 생성하지 않는다.


### 7. `activity_review_agent`

역할:

- activity plan 구조 검증
- blocked/warning 판정

입력:

- `sections/<lesson>/activity_plan.json`

출력:

- `sections/<lesson>/activity_review.json`
- `sections/<lesson>/activity_review.status.json`


### 8. `activity_repair_agent`

역할:

- review 실패 시에만 실행
- repair prompt 또는 local fallback 수행

입력:

- `sections/<lesson>/activity_plan.json`
- `sections/<lesson>/activity_review.json`

출력:

- `sections/<lesson>/activity_plan.repaired.json`
- `sections/<lesson>/activity_repair.status.json`

비고:

현재 `activity_plan_agent` 내부의 repair/fallback을 밖으로 빼는 것이 핵심이다.


### 9. `html_card_agent`

역할:

- activity plan을 HTML 자산으로 렌더링

입력:

- `sections/<lesson>/activity_plan.json`

출력:

- `render/html/...`
- `render/html_card.status.json`


### 10. `render_manifest_agent`

역할:

- HTML/cards를 sheet 단위 배치 manifest로 조립

입력:

- `render/html/...`

출력:

- `render/render_manifest.json`
- `render/render_manifest.status.json`

비고:

현재 구조에서는 manifest 생성 책임과 manifest review 책임이 이름상 선명하게 드러나지 않는다.


### 11. `render_review_agent`

역할:

- render manifest 규칙 검토
- textbook-first
- before/during/after 흐름
- sheet별 asset 존재 여부 확인

입력:

- `render/render_manifest.json`

출력:

- `render/manifest_review.json`
- `render/manifest_rule_review.json`
- `render/render_review.status.json`


### 12. `capture_agent`

역할:

- HTML/cards 캡처만 수행

입력:

- `render/render_manifest.json`

출력:

- `render/cards/...`
- `render/capture.status.json`


### 13. `numbers_compose_agent`

역할:

- Numbers 파일 조립만 수행

입력:

- `render/render_manifest.json`
- `render/cards/...`

출력:

- `output/<run>.numbers`
- `output/numbers_compose.status.json`


### 14. `numbers_verify_agent`

역할:

- 최종 파일 존재 여부 및 기본 규칙 검증

입력:

- `output/<run>.numbers`

출력:

- `output/verify.status.json`
- `output/verify_rule_review.json`

하지 말아야 할 일:

- compose를 다시 하지 않는다.
- upstream 산출물을 수정하지 않는다.


### 15. `run_summary_agent`

역할:

- 전체 run 상태 요약
- 핵심 warning/blocking issue 정리
- 운영자가 읽는 최종 리포트 생성

입력:

- run manifest
- 각 stage status / review 파일

출력:

- `output/run_summary.json`

비고:

필수는 아니지만 운영과 QA에는 유용하다.


## 권장 상태 모델

각 stage는 공통적으로 아래 상태만 쓰는 편이 낫다.

- `pending`
- `running`
- `succeeded`
- `succeeded_with_warning`
- `blocked`
- `failed`

권장하지 않는 방식:

- `failed_fallback_used`

이 상태는 "실패"와 "복구 사용"을 한 필드에 섞는다.

더 나은 방식:

- 상태는 `succeeded_with_warning` 또는 `failed`
- 별도 메타데이터에 `fallback_used: true`
- 필요 시 `repair_attempted: true`

즉 상태와 실행 메타데이터는 분리하는 편이 낫다.


## 현재 구조에서 가장 먼저 바꿔야 할 것

전체를 한 번에 바꾸기 부담되면 아래 3가지를 우선 적용한다.

### 우선순위 1. `source_parse_agent` 분해

현재:

- config 정규화
- source boundary 계산
- review 생성
- AI sidecar review

권장:

1. `config_intake_agent`
2. `source_boundary_agent`
3. `source_validation_agent`

이 분해가 가장 효과가 크다.


### 우선순위 2. `review_lesson_agent`, `review_activity_agent`를 실제 독립 agent로 승격

현재는 stage 이름만 존재하고 실행 책임은 상위 생성 agent 내부에 있다.

이 둘을 실제 독립 실행으로 분리하면:

- stage와 실행 단위가 일치한다.
- 리뷰 품질을 독립적으로 측정할 수 있다.
- 생성과 검증의 책임 경계가 선명해진다.


### 우선순위 3. `activity_repair_agent` 분리

현재 repair/fallback은 `activity_plan_agent` 내부에 숨어 있다.

이를 분리하면:

- 실패 원인 추적이 쉬워진다.
- repair 성공률을 따로 본다.
- baseline fallback 사용량을 명확히 집계할 수 있다.


## 최소 수정 버전의 권장 stage 순서

기존 구조를 최대한 유지하면서도 경계를 개선하는 최소 수정안:

1. `source_boundary_agent`
2. `source_validation_agent`
3. `lesson_analysis_agent`
4. `lesson_review_agent`
5. `activity_plan_agent`
6. `activity_review_agent`
7. `activity_repair_agent`
8. `html_card_agent`
9. `capture_agent`
10. `numbers_compose_agent`
11. `review_manifest_agent`
12. `verify_agent`

이 버전은 기존 렌더/캡처/조합 구조를 유지하면서 가장 큰 결합만 끊는 방법이다.


## 결론

현재 구조는 "실무형 파이프라인 분리"로는 괜찮다.

하지만 "각 agent에 최소 단위 작업만 맡긴다"는 기준으로 보면 아직 아래 문제가 남아 있다.

- source 단계가 비대하다.
- review stage가 실제 독립 실행 단위가 아니다.
- 생성, 검증, 복구가 한 agent 안에 섞여 있다.

따라서 권장 방향은 다음 한 줄로 요약된다.

"생성 agent와 검증 agent를 분리하고, fallback/repair는 별도 agent로 승격한다."

이 원칙만 지켜도 workflow의 명확성, 디버깅 가능성, 운영 관측성이 모두 좋아진다.


## 실제 적용을 위한 `DEFAULT_STAGE_ORDER` 변경안

현재 `scripts/pipeline_contracts.py`의 `DEFAULT_STAGE_ORDER`는 아래와 같다.

```python
[
  "source_parse_agent",
  "lesson_analysis_agent",
  "review_lesson_agent",
  "activity_plan_agent",
  "review_activity_agent",
  "html_card_agent",
  "capture_agent",
  "numbers_compose_agent",
  "review_manifest_agent",
  "verify_agent",
]
```

이 구조는 기존 실행 흐름을 반영하지만, 실제 책임 분리와는 완전히 일치하지 않는다.

### 권장 최종안

```python
[
  "config_intake_agent",
  "source_boundary_agent",
  "source_validation_agent",
  "lesson_analysis_agent",
  "lesson_review_agent",
  "activity_plan_agent",
  "activity_review_agent",
  "activity_repair_agent",
  "html_card_agent",
  "render_manifest_agent",
  "render_review_agent",
  "capture_agent",
  "numbers_compose_agent",
  "numbers_verify_agent",
  "run_summary_agent",
]
```

### 현실적인 최소 수정안

기존 코드베이스와 run-root 구조를 크게 흔들지 않고 먼저 적용하기 쉬운 순서는 아래다.

```python
[
  "source_boundary_agent",
  "source_validation_agent",
  "lesson_analysis_agent",
  "lesson_review_agent",
  "activity_plan_agent",
  "activity_review_agent",
  "activity_repair_agent",
  "html_card_agent",
  "capture_agent",
  "numbers_compose_agent",
  "review_manifest_agent",
  "verify_agent",
]
```

이 최소 수정안의 장점:

- 기존 `render`, `capture`, `compose`, `verify` 구조를 유지한다.
- 가장 큰 결합 지점인 source와 activity repair만 먼저 분리한다.
- 현재 UI와 run monitor 구조를 완전히 갈아엎지 않고 진화시킬 수 있다.


## 단계별 마이그레이션 전략

한 번에 전부 바꾸기보다 3단계로 나누는 편이 안전하다.

### 1차 리팩터링

목표:

- source 단계 분해
- review stage를 실제 실행 단위로 분리

적용 결과:

```python
[
  "source_boundary_agent",
  "source_validation_agent",
  "lesson_analysis_agent",
  "lesson_review_agent",
  "activity_plan_agent",
  "activity_review_agent",
  "html_card_agent",
  "capture_agent",
  "numbers_compose_agent",
  "review_manifest_agent",
  "verify_agent",
]
```

이 단계에서 얻는 효과:

- source 장애 원인 분리가 쉬워진다.
- `review_lesson_agent`, `review_activity_agent`가 stage 이름뿐 아니라 실제 실행 단위가 된다.
- 모니터링 그래프와 실행 구조가 더 잘 맞기 시작한다.

### 2차 리팩터링

목표:

- activity repair/fallback 분리

적용 결과:

```python
[
  "source_boundary_agent",
  "source_validation_agent",
  "lesson_analysis_agent",
  "lesson_review_agent",
  "activity_plan_agent",
  "activity_review_agent",
  "activity_repair_agent",
  "html_card_agent",
  "capture_agent",
  "numbers_compose_agent",
  "review_manifest_agent",
  "verify_agent",
]
```

이 단계에서 얻는 효과:

- repair 성공률을 별도 stage로 추적 가능
- fallback 사용량을 명확히 측정 가능
- activity 생성 실패와 activity 복구 성공을 구분할 수 있음

### 3차 리팩터링

목표:

- manifest 생성/검토 분리
- verify와 summary 역할 정리

적용 결과:

```python
[
  "config_intake_agent",
  "source_boundary_agent",
  "source_validation_agent",
  "lesson_analysis_agent",
  "lesson_review_agent",
  "activity_plan_agent",
  "activity_review_agent",
  "activity_repair_agent",
  "html_card_agent",
  "render_manifest_agent",
  "render_review_agent",
  "capture_agent",
  "numbers_compose_agent",
  "numbers_verify_agent",
  "run_summary_agent",
]
```

이 단계에서 얻는 효과:

- 생성과 검증의 경계가 전체 파이프라인에서 일관된다.
- 운영자용 최종 요약 리포트를 별도 stage로 관리할 수 있다.


## 파일별 리팩터링 작업 목록

아래 목록은 실제 수정 착수 기준으로 정리한 것이다.

### 1. `scripts/pipeline_contracts.py`

변경 목표:

- `DEFAULT_STAGE_ORDER` 재정의
- 상태 모델 단순화

작업:

- `DEFAULT_STAGE_ORDER`를 새 구조로 변경
- `STAGE_STATUS_VALUES`에서 `failed_fallback_used` 제거 검토
- 필요한 경우 `repair_attempted`, `fallback_used`는 status payload로 이동

영향:

- run manifest 생성
- `--stop-after` 선택지
- UI stage 표시 순서


### 2. `scripts/pipeline_orchestrator.py`

변경 목표:

- stage별 실행 단위를 실제 구조와 일치시키기
- 공통 상태 전이 규칙 적용

작업:

- `source_parse_agent` 호출부를 `source_boundary_agent` + `source_validation_agent`로 분해
- `lesson_analysis_agent` 실행 뒤 별도 `lesson_review_agent` 호출 추가
- `activity_plan_agent` 실행 뒤 별도 `activity_review_agent` 호출 추가
- 필요 시 `activity_repair_agent` 분기 실행 추가
- `review_manifest_agent`, `verify_agent`도 다른 stage와 동일하게 `running` 상태 전이 추가
- stage별 try/except 구조를 helper로 추출할지 검토

영향:

- 전체 파이프라인 제어 흐름
- run event 로그
- 실패 시 종료 지점


### 3. `scripts/source_parse_agent.py`

변경 목표:

- 비대한 source 단계 분해

작업:

- 현재 deterministic boundary 계산 부분을 `source_boundary_agent.py`로 이동
- `config_quality_review`, `boundary_review`, `supplement_review`, `source_ai_review` 생성 로직을 `source_validation_agent.py`로 이동
- source status 파일도 stage별로 분리

권장 신규 파일:

- `scripts/source_boundary_agent.py`
- `scripts/source_validation_agent.py`

영향:

- `source/` 아래 status 및 review 파일 생성 위치
- run manifest의 stage별 warning/blocking 집계 방식


### 4. `scripts/lesson_analysis_agent.py`

변경 목표:

- 생성과 review 분리

작업:

- `build_lesson_review()`와 review JSON 생성 로직 분리
- lesson analysis 생성만 담당하도록 단순화
- review 전용 로직은 `lesson_review_agent.py`로 이동

권장 신규 파일:

- `scripts/lesson_review_agent.py`

영향:

- lesson status 구조
- fallback과 review warning 집계 분리


### 5. `scripts/activity_plan_agent.py`

변경 목표:

- 생성, review, repair 분리

작업:

- `build_activity_review()`를 `activity_review_agent.py`로 이동
- repair prompt 및 fallback 로직을 `activity_repair_agent.py`로 이동
- 현재 agent는 activity plan 초안 생성까지만 담당

권장 신규 파일:

- `scripts/activity_review_agent.py`
- `scripts/activity_repair_agent.py`

영향:

- lesson별 산출물 수 증가
- retry/fallback 운영 지표 정교화


### 6. `scripts/review_manifest_agent.py`

변경 목표:

- manifest 생성과 manifest 검토를 명확히 분리

작업:

- 현재 render manifest를 누가 생성하는지 코드상 책임 재확인
- 필요 시 `render_manifest_agent.py` 신설
- `review_manifest_agent.py`는 검토만 수행하도록 제한

권장 신규 파일:

- `scripts/render_manifest_agent.py`


### 7. `scripts/verify_agent.py`

변경 목표:

- verify 역할을 명확히 유지
- 필요 시 summary 책임 분리

작업:

- verify는 최종 산출물 존재 및 규칙 검토만 하도록 유지
- 전체 run 요약 로직이 있다면 `run_summary_agent.py`로 이동 검토

권장 신규 파일:

- `scripts/run_summary_agent.py`


### 8. `agents/*.md`

변경 목표:

- 문서와 실제 실행 구조 일치

작업:

- 새 agent 문서 추가
- 더 이상 내장 review로 남기지 않을 stage는 독립 agent 문서로 분리
- 입력/출력/하지 말아야 할 일 섹션을 실제 산출물 기준으로 갱신

수정 대상 예시:

- `agents/README.md`
- `agents/source_parse_agent/AGENT.md`
- `agents/lesson_analysis_agent/AGENT.md`
- `agents/activity_plan_agent/AGENT.md`
- 신규 `agents/source_boundary_agent/AGENT.md`
- 신규 `agents/source_validation_agent/AGENT.md`
- 신규 `agents/lesson_review_agent/AGENT.md`
- 신규 `agents/activity_review_agent/AGENT.md`
- 신규 `agents/activity_repair_agent/AGENT.md`


### 9. `app/server` 및 `app/web`

변경 목표:

- 새 stage 구조를 모니터링 UI에 반영

작업:

- stage 명칭 매핑 추가
- 그래프 노드 순서 갱신
- stage 상세 패널에서 새 status/review 파일 표시
- `stop-after` 기반 테스트 UX가 있다면 새 stage 목록 반영

영향 가능 파일:

- `app/server/run_manager.py`
- `app/web/src/types/events.ts`
- `app/web/src/utils/graphLayout.ts`
- `app/web/src/components/RunGraph.tsx`
- `app/web/src/components/NodeDetailPanel.tsx`


## 추천 구현 순서

실제 착수 순서는 아래를 권장한다.

### 순서 1

- `pipeline_contracts.py`
- `pipeline_orchestrator.py`

이 두 파일에서 stage 순서와 상태 전이를 먼저 정리한다.

### 순서 2

- `source_boundary_agent.py`
- `source_validation_agent.py`
- 기존 `source_parse_agent.py` 축소 또는 제거

source 단계 분해가 전체 구조 개선 효과가 가장 크다.

### 순서 3

- `lesson_review_agent.py`
- `activity_review_agent.py`

생성과 검증을 분리해 실행 단위와 모니터링 단위를 맞춘다.

### 순서 4

- `activity_repair_agent.py`

repair/fallback을 stage로 승격한다.

### 순서 5

- `agents/*.md`
- `app/server`
- `app/web`

문서와 UI를 실제 실행 구조에 맞춘다.


## 각 단계 완료 기준

### 1차 완료 기준

- source 단계가 두 개 이상의 독립 stage로 나뉜다.
- `review_lesson_agent`가 실제 코드 실행 단위가 된다.
- `review_activity_agent`가 실제 코드 실행 단위가 된다.

### 2차 완료 기준

- repair/fallback이 별도 stage로 보인다.
- `activity_plan_agent`는 생성만 담당한다.
- `activity_review_agent`는 검증만 담당한다.

### 3차 완료 기준

- 생성 agent와 검증 agent가 전체 파이프라인 전반에 걸쳐 일관되게 분리된다.
- run monitor의 stage 그래프와 실제 실행 코드가 1:1로 대응된다.


## 최종 권고

이 리팩터링은 "기능 추가"보다 "책임 경계 정리"가 목적이다.

따라서 가장 중요한 판단 기준은 아래다.

- 이 stage가 무언가를 생성하는가
- 이 stage가 무언가를 판정하는가
- 이 stage가 실패한 결과를 복구하는가

이 셋이 한 stage 안에 동시에 있으면 다시 쪼개는 편이 맞다.

가장 먼저 손대야 할 것은 `source_parse_agent`와 `activity_plan_agent`다.
이 둘이 현재 구조에서 가장 많은 책임을 동시에 가지고 있기 때문이다.
