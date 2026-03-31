# Future Workflow Vision

## 목표

NumbersAuto의 최종 목표는 단순히 교과서를 기반으로 활동지를 생성하는 것이 아니다.

지향하는 최종 시스템은 아래를 수행해야 한다.

1. 교과서를 분석한다.
2. 차시별로 분리한다.
3. 차시별 교육 내용을 분석한다.
4. 국가수준 교육과정의 성취기준, 평가, 교수학습 방법과 정렬한다.
5. 사용자 요구에 따라 활동 구성 방향을 바꾼다.
6. 주요 활동을 수준별 활동으로 다시 구성한다.
7. 학생이 자신이 할 수 있는 수준의 활동을 선택할 수 있게 한다.
8. 최종적으로 Numbers 수업 자료로 출력한다.


## 현재 구조를 바탕으로 발전 가능한가

가능하다.

현재 구조는 아래의 기본 축을 이미 갖고 있다.

- 교과서 source를 차시 단위로 자른다.
- 차시별 JSON 산출물을 만든다.
- 차시별 활동을 생성한다.
- 최종적으로 render/capture/compose를 거쳐 Numbers 파일을 만든다.

즉 현재 구조는 "교과서 -> 차시 -> 활동 -> 산출물"의 뼈대가 이미 있다.

이 뼈대를 유지한 채, 중간 단계에 교육과정 정렬과 수준별 재구성 레이어를 추가하면 된다.


## 현재 구조에서 유지 가능한 축

다음 축은 그대로 유지해도 된다.

- `source_boundary_agent`
- `source_validation_agent`
- `lesson_analysis_agent`
- `lesson_review_agent`
- `html_card_agent`
- `capture_agent`
- `numbers_compose_agent`
- `verify_agent`

즉 지금 있는 구조는 버릴 대상이 아니라, 상위 목표를 위해 확장해야 할 기반이다.


## 반드시 추가되어야 할 레이어

### 1. `curriculum_alignment_agent`

역할:

- 차시 내용을 국가수준 교육과정과 연결한다.
- 성취기준, 평가 요소, 교수학습 방법, 적합한 학습 경험을 도출한다.

왜 필요한가:

- 지금 구조는 교과서 내용을 해석하는 수준에 가깝다.
- 최종 목표는 교육과정 정렬형 수업 설계이므로, "교과서 내용"과 "교육과정 체계"를 연결하는 중간 레이어가 반드시 필요하다.

예상 출력:

- `sections/<lesson>/curriculum_alignment.json`


### 2. `activity_strategy_agent`

역할:

- 사용자 요구를 반영해 활동 구성 방향을 정한다.

예:

- 창작 중심
- 기능 중심
- 탐구 중심
- 토의 중심
- 프로젝트 중심

왜 필요한가:

- 같은 차시라도 사용자의 수업 의도에 따라 활동 구조는 달라져야 한다.
- 곧바로 activity를 생성하는 것이 아니라, 먼저 "어떤 방향의 활동을 설계할지" 결정하는 전략 단계가 필요하다.

예상 출력:

- `sections/<lesson>/activity_strategy.json`


### 3. `differentiation_agent`

역할:

- 주요 활동을 수준별 활동군으로 재구성한다.

예:

- 지원형
- 표준형
- 확장형

또는:

- 기본
- 표준
- 심화

왜 필요한가:

- 개별화 학습은 단순히 "쉬운 버전 / 어려운 버전"을 만드는 것으로 충분하지 않다.
- 학생이 선택 가능한 학습 경로를 가져야 한다.
- 따라서 major activity를 수준별 bundle로 재구성하는 별도 단계가 필요하다.

예상 출력:

- `sections/<lesson>/differentiated_activity_bundle.json`


### 4. `differentiation_review_agent`

역할:

- 수준별 활동군이 교육적으로 타당한지 검토한다.
- 각 수준이 단순 난이도 차이인지, 실제로 선택 가능한 경로인지 확인한다.

예상 출력:

- `sections/<lesson>/differentiation_review.json`


## 권장 미래 워크플로우

최종적으로는 아래 순서를 목표로 한다.

1. `source_boundary_agent`
2. `source_validation_agent`
3. `lesson_analysis_agent`
4. `lesson_review_agent`
5. `curriculum_alignment_agent`
6. `activity_strategy_agent`
7. `activity_plan_agent`
8. `activity_review_agent`
9. `differentiation_agent`
10. `differentiation_review_agent`
11. `html_card_agent`
12. `capture_agent`
13. `numbers_compose_agent`
14. `review_manifest_agent`
15. `verify_agent`


## 차시별 산출물 구조 예시

최종적으로는 차시 디렉터리가 아래와 같이 확장되는 것이 자연스럽다.

```text
sections/8차시/
  lesson_analysis.json
  lesson_review.json
  curriculum_alignment.json
  activity_strategy.json
  activity_plan.json
  activity_review.json
  differentiated_activity_bundle.json
  differentiation_review.json
```

이 구조의 장점:

- 차시 단위 독립성 유지
- 단계별 디버깅 가능
- 특정 단계만 재실행 가능
- 수준별 재구성 결과를 render 레이어에 안정적으로 전달 가능


## 핵심 설계 원칙

### 1. `lesson_analysis`와 `curriculum_alignment`를 분리한다

둘은 비슷해 보이지만 다른 작업이다.

- `lesson_analysis`: 교과서가 무엇을 다루는지 분석
- `curriculum_alignment`: 그 내용을 어떤 교육과정 기준으로 해석할지 정렬

분리해야 각 단계의 책임과 품질 평가 기준이 선명해진다.


### 2. 활동 생성 전에 전략 레이어를 둔다

사용자가 "창작 중심", "기능 중심"을 선택할 수 있으려면, 바로 activity를 생성하면 안 된다.

먼저 아래를 정리해야 한다.

- 어떤 학습경험을 강조할지
- 어떤 평가 요소를 반영할지
- 어떤 교수학습 방법이 중심인지
- 학생 산출물의 성격이 무엇인지

즉 activity 생성 전에 strategy 단계가 있어야 한다.


### 3. 수준별 활동은 난이도 조절이 아니라 학습경로 재구성이다

최종 목표는 단순한 leveled worksheet가 아니다.

좋은 differentiation은 아래를 포함해야 한다.

- 지원형: scaffold 제공
- 표준형: 핵심 성취
- 확장형: 응용, 전이, 창작

즉 학생이 "내가 할 수 있는 것"을 선택하고, 그 선택이 학습적으로 의미 있는 경로가 되어야 한다.


### 4. review는 구조 검증을 넘어 교육적 타당성까지 다뤄야 한다

현재 review는 구조적 검증 비중이 크다.

미래에는 아래까지 포함해야 한다.

- 교육과정 정렬 타당성
- 활동 방향과 사용자 의도 일치 여부
- 수준별 선택 구조의 유의미성
- 평가 요소 반영 여부


## 앞으로 필요한 입력 모델 확장

지금 config는 교과서와 lesson 중심이다.

미래에는 수업 설계 의도를 반영하는 입력이 필요하다.

예시:

```json
{
  "activity_preference": "creative",
  "differentiation_model": "support-core-extension",
  "evaluation_focus": [
    "concept_understanding",
    "expression",
    "collaboration"
  ],
  "teaching_style": [
    "inquiry",
    "discussion"
  ],
  "class_constraints": {
    "minutes_per_lesson": 40,
    "group_work_allowed": true,
    "writing_heavy_ok": false
  }
}
```

이런 입력이 있어야 같은 차시라도 사용자가 원하는 수업 방향으로 activity를 설계할 수 있다.


## 현재 구조에서 부족한 점

가능성은 충분하지만, 아직 아래는 비어 있다.

- 교육과정 데이터 소스
- 사용자 의도 입력 모델
- 활동 전략 레이어
- 수준별 활동 재구성 레이어
- 교육적 타당성 중심 review

즉 현재 구조는 "교과서 기반 차시 활동 생성기"에 가깝고, 최종 목표는 "교육과정 정렬형, 사용자 지향형, 수준별 개별화 수업 설계 시스템"이다.


## 현실적인 개발 순서

권장 순서는 아래와 같다.

### 1. `curriculum_alignment_agent` 추가

목적:

- 교과서 분석과 교육과정 정렬을 연결


### 2. `activity_strategy_agent` 추가

목적:

- 사용자 요구와 수업 방향을 activity 생성 전에 확정


### 3. 기존 `activity_plan_agent`를 전략 반영형으로 개편

목적:

- 무조건적인 activity 생성이 아니라, strategy 기반 생성으로 전환


### 4. `differentiation_agent` 추가

목적:

- major activity를 수준별 activity bundle로 재구성


### 5. render 계층 확장

목적:

- 수준별 활동 bundle을 시각적으로 표현 가능하게 만들기


## 한 줄 결론

현재 구조는 충분히 발전 가능하다.

버릴 필요는 없고, 아래 세 축을 추가하면 된다.

- 교육과정 정렬
- 활동 전략 제어
- 수준별 재구성

즉 앞으로 NumbersAuto는 "교과서 기반 활동 생성기"에서 "교육과정 정렬형, 사용자 지향형, 수준별 개별화 수업 설계 시스템"으로 발전해야 한다.
