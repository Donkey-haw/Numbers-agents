# Agent JSON Workflow Validation

## 목적
- 사용자가 제안한 `에이전트 단위 워크플로우 + JSON 기반 단계 간 통신` 방식이 현재 코드베이스에 적합한지 검증한다.
- 이 문서는 설계 검증 결과만 다루며, 코드 변경 제안은 포함하되 실제 수정은 하지 않는다.

## 결론
- 결론부터 말하면, 이 방식은 **적합하다**.
- 다만 “완전히 새로운 구조”라기보다, 현재 이미 존재하는 `stage + JSON artifact` 구조를 더 엄격한 **에이전트 계약 모델**로 재정리하는 것이 맞다.
- 즉, 지금 파이프라인을 버리고 다시 만드는 것보다 다음 방향이 현실적이다.
  - 단계별 책임을 더 강하게 분리
  - 각 단계의 입력/출력을 JSON schema로 고정
  - 실패를 단계 단위로 국소화
  - Gemini는 의미 해석과 활동 초안 제안 역할에 집중
  - 렌더/삽입/검증은 계속 결정론 코드가 맡음

## 현재 코드베이스와의 적합성

### 이미 맞아 있는 부분
- 현재 파이프라인은 이미 `JSON 중간 산출물` 중심 구조를 갖고 있다.
  - `lesson_analysis.json`
  - `activity_plan.json`
  - `render_manifest.json`
- 실제 오케스트레이션도 단계형이다.
  - 교과서 분석
  - 활동 계획
  - HTML 렌더/캡처
  - Numbers 삽입
- 관련 근거:
  - [GEMINI_CLI_LINK_PLAN.md](/Users/jonyeock/Desktop/Tool/NumbersAuto/GEMINI_CLI_LINK_PLAN.md)
  - [ACTIVITY_EXPANSION_PLAN.md](/Users/jonyeock/Desktop/Tool/NumbersAuto/ACTIVITY_EXPANSION_PLAN.md)
  - [scripts/run_gemini_cli_pipeline.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/run_gemini_cli_pipeline.py)
  - [scripts/generate_numbers_with_activities.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/generate_numbers_with_activities.py)

### 즉시 얻는 장점
1. 오류 격리
- 지금은 사용자가 체감하기에 “Gemini CLI가 실패했다”, “자동 생성이 깨졌다”처럼 뭉뚱그려 보인다.
- 에이전트 계약을 분리하면 실패 위치를 더 선명하게 볼 수 있다.
  - `schedule_parse_agent` 실패
  - `lesson_analysis_agent` 실패
  - `activity_html_agent` 실패
  - `numbers_insert_agent` 실패

2. 재시도 전략이 선명해진다
- 현재도 lesson/activity 단계에서 fallback이 있지만, 더 명확한 단계 계약이 있으면 단계별 재시도가 쉬워진다.
- 예:
  - `lesson_analysis_agent`: 한 번 더 좁은 문맥으로 재호출
  - `activity_agent`: validation error를 붙여 repair 재호출
  - `numbers_insert_agent`: AppleScript만 재시도

3. 병렬화가 자연스러워진다
- 현재도 차시별 Gemini 병렬화는 이미 들어가 있다.
- 에이전트 단위로 쪼개면 “차시별 task queue”나 “재실행 가능한 부분 파이프라인”으로 확장하기 쉽다.
- 근거:
  - [OPTIMIZATION_ANALYSIS.md](/Users/jonyeock/Desktop/Tool/NumbersAuto/OPTIMIZATION_ANALYSIS.md)
  - [scripts/run_gemini_cli_pipeline.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/run_gemini_cli_pipeline.py)

4. 디버깅과 회귀 검증이 쉬워진다
- JSON artifact가 명확하면 특정 단계부터 재생성 가능하다.
- 예:
  - 차시 파싱까지는 정상
  - activity JSON만 다시 생성
  - render_manifest부터만 재실행

## 에이전트 분리안 검증

### A. 차시 파싱 에이전트
- 역할:
  - 교과서 + 진도표를 읽고 차시 경계를 정리
  - 차시별 config 또는 `schedule_draft.json`, `textbook_context.json` 생성
- 적합성:
  - 매우 높음
- 이유:
  - 현재도 이 역할이 로컬 Python에 잘 맞는다.
  - 페이지 경계는 생성형보다 결정론 로직이 유리하다.
- 권장 출력:
  - `schedule_draft.json`
  - `textbook_context.json`
  - 또는 장기적으로 `unit_bundle.json`
- 근거:
  - [GEMINI_CLI_LINK_PLAN.md](/Users/jonyeock/Desktop/Tool/NumbersAuto/GEMINI_CLI_LINK_PLAN.md)
  - [REUSABLE_SCAN_ARCHITECTURE.md](/Users/jonyeock/Desktop/Tool/NumbersAuto/REUSABLE_SCAN_ARCHITECTURE.md)

### B. lesson_analysis 에이전트
- 역할:
  - 차시 텍스트를 읽고 핵심 질문, 개념, 오개념, 목표 후보 생성
- 적합성:
  - 높음
- 이유:
  - 현재 Gemini가 상대적으로 잘하는 부분이다.
  - 다만 페이지 범위 결정 권한은 주면 안 된다.
- 권장 출력:
  - `lesson_analysis_ai.json`
  - 검증 후 `lesson_analysis.json`

### C. activity 구성 에이전트
- 역할:
  - `lesson_analysis.json`을 받아 활동 JSON 생성
- 적합성:
  - 높음
- 이유:
  - 현재 가장 생성형이 필요한 단계다.
  - 단, 자유 HTML까지 한 에이전트가 다 책임질지 여부는 분리 검토가 필요하다.
- 현재 리스크:
  - 이 단계가 너무 많은 책임을 가진다.
    - 활동 목표 설계
    - 객체 역할 판단
    - lesson flow 판단
    - student_writing_zones 메타데이터 작성
    - freeform HTML 작성
- 판단:
  - `활동 기획 JSON`과 `HTML 제작`을 분리하는 것이 더 안정적일 수 있다.

### D. HTML 제작 에이전트
- 역할:
  - `activity_plan.json`을 받아 최종 HTML 카드 생성
- 적합성:
  - 조건부 적합
- 장점:
  - 프롬프트 책임이 분리된다.
  - 활동의 의미와 카드 레이아웃 문제를 분리할 수 있다.
- 단점:
  - 에이전트 수가 늘고 호출량이 늘어난다.
  - 차시당 활동 수가 많으면 Gemini 호출 수와 비용이 증가한다.
- 현재 코드 기준 판단:
  - 지금은 `activity agent`가 `html_content`까지 생성한다.
  - 이 구조는 빠르지만, validation 실패가 activity 의미 문제와 HTML 문제를 섞는다.
- 현실적 결론:
  - 장기적으로는 분리 가치가 있다.
  - 단기적으로는 `activity_plan_agent -> html_agent` 완전 분리보다
    - `activity_plan JSON`
    - `html_render JSON`
    의 2단 계약을 설계해 시범 적용하는 편이 맞다.

### E. Numbers 삽입 에이전트
- 역할:
  - `render_manifest.json`을 받아 Numbers에 실제 삽입
- 적합성:
  - 높음
- 이유:
  - 현재도 이 단계는 사실상 독립 실행 가능하다.
  - Gemini와 분리해야 하는 전형적인 결정론 단계다.
- 현재 리스크:
  - AppleScript 호출 안정성
- 즉:
  - 이 단계는 AI보다 “재시도 가능하고 idempotent한 실행기”로 보는 편이 더 맞다.

## 핵심 판단: 가장 좋은 분리선

### 추천 분리선
1. `source_parse_agent`
- 입력:
  - 교과서 PDF
  - 진도표
  - config
- 출력:
  - `schedule_draft.json`
  - `textbook_context.json`

2. `lesson_analysis_agent`
- 입력:
  - `textbook_context.json`
  - 차시별 source chunk
- 출력:
  - `lesson_analysis_ai.json`
  - 검증 후 `lesson_analysis.json`

3. `activity_plan_agent`
- 입력:
  - `lesson_analysis.json`
- 출력:
  - `activity_plan_ai.json`
  - 검증 후 `activity_plan.json`

4. `html_card_agent`
- 입력:
  - `activity_plan.json`
- 출력:
  - `render_cards.json` 또는 활동별 `html_assets.json`

5. `numbers_insert_agent`
- 입력:
  - `render_manifest.json`
- 출력:
  - 삽입 결과 JSON
  - 시트 검증 결과 JSON

### 왜 이 분리선이 좋은가
- AI가 필요한 단계와 아닌 단계를 분리한다.
- JSON schema로 경계를 고정할 수 있다.
- 실패 시 전체가 아니라 특정 단계만 재실행할 수 있다.
- 현재 코드베이스의 구조와도 가장 잘 맞는다.

## 이 방식의 가장 큰 장점

### 1. “프롬프트 문제”와 “실행 문제”를 분리할 수 있다
- 지금은 한 번 실패하면 사용자가 보기에는 모두 “Gemini CLI 오류”처럼 보인다.
- 하지만 실제로는 아래가 섞여 있다.
  - Gemini 응답 지연
  - JSON shape 위반
  - HTML 규칙 위반
  - Playwright 캡처 문제
  - AppleScript 삽입 문제
- 에이전트 단위 JSON 계약을 두면 어느 층의 문제인지 즉시 구분 가능하다.

### 2. fallback 설계를 더 정교하게 할 수 있다
- 예:
  - 차시 파싱 실패 -> title-only deterministic fallback
  - activity 설계 실패 -> 로컬 템플릿 fallback
  - html 생성 실패 -> 결정론 템플릿 renderer fallback
  - Numbers 삽입 실패 -> manifest까지만 완료하고 수동 삽입 대기

### 3. artifact 중심 운영이 가능하다
- 지금도 artifact를 저장하지만, 에이전트 기반으로 더 명확한 계약을 두면
  - 재현
  - 회귀 테스트
  - 사람이 중간 검토
  - 부분 승인
  가 쉬워진다.

## 이 방식의 한계와 주의점

### 1. 에이전트 수를 늘리면 오히려 느려질 수 있다
- Gemini 호출이 늘어나면 현재 병목이 더 심해질 수 있다.
- 따라서 모든 단계를 AI 에이전트로 만들면 안 된다.
- 특히 다음은 AI 에이전트보다 결정론 실행기로 유지하는 편이 맞다.
  - PDF 페이지 범위 확정
  - Playwright 캡처
  - Numbers 삽입
  - 결과 검증

### 2. 자유 HTML 생성은 단계 분리를 잘못하면 비용이 커진다
- `activity planning`과 `HTML design`을 모두 분리하면 안정성은 올라갈 수 있지만 속도는 떨어진다.
- 현재 병목이 Gemini 응답 대기라는 점을 감안하면, 완전 분리는 신중해야 한다.

### 3. JSON만으로 모든 디자인 의도를 담기 어렵다
- activity 의미는 JSON으로 잘 전달된다.
- 하지만 자유 HTML 디자인 의도는 메타데이터만으로 손실될 수 있다.
- 따라서 `html_card_agent`를 둘 경우 JSON contract는 너무 얇으면 안 된다.
  - `object_role`
  - `lesson_flow_stage`
  - `writing_space_profile`
  - `student_writing_zones`
  - `reference_slots`
  - `ai_followup_slots`
  같은 구조가 필요하다.

## 현재 코드 기준 최종 판단

### 타당성
- 제안 방식은 타당하다.
- 특히 현재처럼
  - 로컬 Python 정규화
  - Gemini 의미 해석
  - Numbers/렌더 결정론 실행
  이 이미 혼합된 구조에서는 더 잘 맞는다.

### 다만 바로 권장하지 않는 형태
- “모든 단계를 별도 AI 에이전트화”하는 것은 비권장
- 이유:
  - 속도 저하
  - 호출 비용 증가
  - 책임 과분산
  - 디버깅 포인트 증가

### 가장 권장하는 형태
- `AI planning sidecar + 결정론 실행기 + JSON artifact 계약`
- 즉:
  - AI는 해석/추천
  - Python은 정규화/검증/렌더/삽입
  - 단계 간 교환은 JSON schema로 고정

## 실무 적용 권장안

### 단기
- 현재 구조를 유지하되 단계 이름을 명확히 문서화
- 각 단계 산출물 schema를 더 엄격히 정의
- 실패 로그를 단계별 status JSON으로 남김

### 중기
- `activity_plan_agent`와 `html_card_agent`를 논리적으로 분리
- 실제 호출은 필요 시 통합 실행하더라도, 내부 계약은 분리

### 장기
- `unit_bundle -> lesson_analysis -> activity_plan -> render_manifest -> insertion_result`
  전체를 하나의 실행 DAG처럼 운영
- 각 노드는 재실행 가능하고, artifact cache를 재사용

## 최종 한 줄 판단
- 제안한 방식은 **좋다**.
- 단, “에이전트를 많이 늘리는 것”이 핵심이 아니라, **현재 stage 파이프라인을 JSON 계약 중심의 에이전트 워크플로우로 재정의하는 것**이 핵심이다.
