# Agent Workflow Setup

## 목적
- 교과서 PDF, 진도표, 활동 생성, HTML 렌더, Numbers 삽입까지의 전체 작업 흐름을 **항상 같은 방식**으로 실행하기 위한 에이전트 셋업 표준을 정의한다.
- 핵심은 “에이전트를 많이 쓰는 것”이 아니라, **모든 상황에서 같은 단계, 같은 JSON 계약, 같은 실패 처리 규칙**을 유지하는 것이다.

## 핵심 원칙
1. 워크플로우는 항상 같은 단계 순서를 따른다.
2. 각 단계는 하나의 명확한 책임만 가진다.
3. 단계 간 통신은 항상 JSON artifact로만 한다.
4. 생성형 판단과 결정론 실행을 섞지 않는다.
5. 실패는 전체 실패가 아니라 `단계 실패`로 기록한다.
6. fallback은 조용히 일어나면 안 되고, 반드시 status JSON에 남긴다.
7. 사람이 중간 검토할 수 있도록 모든 핵심 산출물은 저장한다.

## 가장 권장하는 에이전트 구성

### 1. `source_parse_agent`
- 역할:
  - 교과서 PDF, 진도표, 보조교재를 읽고 차시 실행 입력을 만든다.
- 성격:
  - 결정론 실행기
- 입력:
  - `resource_catalog.json` 또는 원본 PDF/진도표/config
- 출력:
  - `schedule_draft.json`
  - `textbook_context.json`
  - 필요 시 `unit_bundle.json`
  - `runtime_config.json`
- 금지:
  - 활동 추천
  - HTML 생성
  - 페이지 범위를 생성형으로 확정

### 2. `lesson_analysis_agent`
- 역할:
  - 차시 텍스트를 읽고 학습 목표, 핵심 개념, 오개념, 핵심 질문을 제안한다.
- 성격:
  - AI planning agent
- 입력:
  - `textbook_context.json`
  - 차시별 source chunk
- 출력:
  - `lesson_analysis_ai.json`
  - `lesson_analysis.json`
  - `lesson_analysis.status.json`
- 금지:
  - 페이지 범위 수정
  - Numbers 배치 판단

### 3. `activity_plan_agent`
- 역할:
  - `lesson_analysis.json`을 바탕으로 활동의 의미 구조를 설계한다.
- 성격:
  - AI planning agent
- 입력:
  - `lesson_analysis.json`
  - `ACTIVITY_RULE.md`
  - `NumbersDesign.md`
- 출력:
  - `activity_plan_ai.json`
  - `activity_plan.json`
  - `activity_plan.status.json`
- 반드시 포함해야 할 메타데이터:
  - `object_role`
  - `lesson_flow_stage`
  - `student_writing_zones`
  - `source_refs`

### 4. `html_card_agent`
- 역할:
  - 활동 계획을 실제 렌더 가능한 카드 표현으로 바꾼다.
- 성격:
  - 우선순위는 2안 중 하나
- 권장 1안:
  - 결정론 renderer
- 권장 2안:
  - 필요 시 AI-assisted HTML agent
- 입력:
  - `activity_plan.json`
- 출력:
  - `html_assets.json`
  - 활동별 `.html`
  - `html_render.status.json`

### 5. `capture_agent`
- 역할:
  - HTML과 교과서 카드를 PNG asset으로 캡처한다.
- 성격:
  - 결정론 실행기
- 입력:
  - `html_assets.json`
  - 교과서 카드 HTML/이미지 정보
- 출력:
  - `capture_assets.json`
  - PNG files
  - `capture.status.json`

### 6. `numbers_compose_agent`
- 역할:
  - `render_manifest.json`을 만들고 Numbers에 삽입한다.
- 성격:
  - 결정론 실행기
- 입력:
  - `capture_assets.json`
  - `runtime_config.json`
- 출력:
  - `render_manifest.json`
  - `numbers_insert.status.json`
  - 최종 `.numbers`

### 7. `verify_agent`
- 역할:
  - 최종 `.numbers` 결과와 manifest를 검증한다.
- 성격:
  - 결정론 실행기
- 입력:
  - `.numbers`
  - `render_manifest.json`
  - expected sheet list
- 출력:
  - `verify.status.json`
  - 필요 시 `partial-with-warning`

### 8. `review_agent` 계층
- 역할:
  - 각 핵심 산출물을 자동 검토하고, 수정이 필요한 지점을 구조화된 JSON으로 남긴다.
- 성격:
  - AI review agent 또는 규칙 기반 review agent
- 원칙:
  - `review agent`는 검토자이지 승인자가 아니다.
  - 최종 승인 상태를 직접 `approved`로 바꾸면 안 된다.
  - 반드시 `review result`만 남기고, 승인 여부는 별도 정책이나 사람이 결정한다.

### 8-1. `review_lesson_agent`
- 입력:
  - `lesson_analysis.json`
- 출력:
  - `lesson_review.json`
- 점검 항목:
  - 차시명 정합성
  - 목표/개념의 교과서 근거
  - 오개념 누락 여부
  - source page refs 적절성

### 8-2. `review_activity_agent`
- 입력:
  - `activity_plan.json`
  - 필요 시 `lesson_analysis.json`
- 출력:
  - `activity_review.json`
- 점검 항목:
  - 활동이 교과서 반복인지 여부
  - `ACTIVITY_RULE.md` 적합성
  - `NumbersDesign.md` 적합성
  - `student_writing_zones` 충실성
  - before / during / after 역할 적절성

### 8-3. `review_manifest_agent`
- 입력:
  - `render_manifest.json`
- 출력:
  - `manifest_review.json`
- 점검 항목:
  - before / during / after 흐름
  - 객체 수
  - 배치 순서
  - 누락 asset 여부

## 어떤 상황에서도 일관되게 유지되는 표준 실행 순서

### 고정 순서
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

### 절대 바꾸지 않는 규칙
- `lesson_analysis`보다 먼저 `activity_plan`을 만들지 않는다.
- `review_lesson_agent` 없이 `activity_plan_agent`로 바로 넘어가지 않는다.
- `activity_plan` 없이 HTML을 만들지 않는다.
- `review_activity_agent` 없이 HTML 생성으로 바로 넘어가지 않는다.
- `render_manifest` 없이 Numbers 삽입을 하지 않는다.
- `review_manifest_agent` 없이 최종 완료 처리하지 않는다.
- `verify` 없이 완료 상태를 주지 않는다.

## 추천 오케스트레이터 구조

### 메인 오케스트레이터는 1개만 둔다
- 이름 예시:
  - `pipeline_orchestrator`
- 역할:
  - 각 에이전트를 호출
  - artifact 경로 관리
  - 상태 집계
  - fallback 결정

### 오케스트레이터가 해야 하는 일
- run id 발급
- 각 단계 입력 경로 고정
- 각 단계 출력 경로 고정
- 단계 성공/실패 집계
- 실패 시 다음 fallback 단계 결정

### 오케스트레이터가 하면 안 되는 일
- lesson analysis 내용을 직접 수정
- activity HTML을 직접 만들기
- 페이지 범위를 임의 재해석

## 표준 디렉토리 구조

```text
artifacts/
  runs/
    <run_id>/
      run_manifest.json
      source/
        schedule_draft.json
        textbook_context.json
        runtime_config.json
        source_parse.status.json
      sections/
        <lesson_id>/
          lesson_analysis_ai.json
          lesson_analysis.json
          lesson_analysis.status.json
          lesson_review.json
          activity_plan_ai.json
          activity_plan.json
          activity_plan.status.json
          activity_review.json
          html_assets.json
          html_render.status.json
      render/
        capture_assets.json
        capture.status.json
        render_manifest.json
        numbers_insert.status.json
        manifest_review.json
        verify.status.json
      output/
        result.numbers
```

## 단계별 JSON 계약

### A. `source_parse.status.json`
- 목적:
  - 차시 파싱 단계 성공/실패 기록
- 필수 필드:
  - `stage`
  - `status`
  - `run_id`
  - `started_at`
  - `finished_at`
  - `input_refs`
  - `output_refs`
  - `warnings`
  - `errors`

### B. `lesson_analysis.status.json`
- 필수 필드:
  - `stage`
  - `lesson_id`
  - `status`
  - `model`
  - `attempt_count`
  - `fallback_used`
  - `validation_errors`

### C. `activity_plan.status.json`
- 필수 필드:
  - `stage`
  - `lesson_id`
  - `status`
  - `attempt_count`
  - `repair_attempted`
  - `fallback_used`
  - `validation_errors`

### D. `html_render.status.json`
- 필수 필드:
  - `stage`
  - `lesson_id`
  - `status`
  - `render_mode`
  - `html_count`
  - `warnings`

### E. `lesson_review.json`
- 필수 필드:
  - `stage`
  - `lesson_id`
  - `status`
  - `decision`
  - `findings`
  - `blocking_issues`
  - `warnings`

### F. `activity_review.json`
- 필수 필드:
  - `stage`
  - `lesson_id`
  - `status`
  - `decision`
  - `findings`
  - `blocking_issues`
  - `warnings`

### G. `manifest_review.json`
- 필수 필드:
  - `stage`
  - `status`
  - `decision`
  - `findings`
  - `blocking_issues`
  - `warnings`

### H. `numbers_insert.status.json`
- 필수 필드:
  - `stage`
  - `status`
  - `manifest_path`
  - `output_file`
  - `applescript_attempts`
  - `errors`

### I. `verify.status.json`
- 필수 필드:
  - `stage`
  - `status`
  - `sheet_names_expected`
  - `sheet_names_actual`
  - `asset_count_expected`
  - `asset_count_actual`
  - `warnings`

## 상태 머신

### 공통 status enum
- `pending`
- `running`
- `succeeded`
- `succeeded_with_warning`
- `failed`
- `failed_fallback_used`
- `blocked`

### review decision enum
- `pass`
- `pass_with_warning`
- `needs_revision`
- `blocked`

### run 전체 상태
- `success`
- `partial-with-warning`
- `textbook-only`
- `failed`

## 가장 중요한 일관성 장치

### 1. stage별 입력은 immutable로 취급
- 한 단계가 이전 단계 산출물을 덮어쓰지 않는다.
- 항상:
  - `*_ai.json`
  - `normalized/final *.json`
  - `status.json`
  를 분리해 둔다.

### 2. schema validation을 단계 경계에 둔다
- 다음 단계는 반드시 이전 단계의 검증 통과본만 읽는다.
- 예:
  - `activity_plan_agent`는 `lesson_analysis.json`만 읽고 `lesson_analysis_ai.json`은 읽지 않음
  - `numbers_compose_agent`는 `render_manifest.json`만 읽음

### 3. fallback도 같은 계약 안에서만 허용
- 예:
  - Gemini 실패 -> 로컬 fallback
- 이때도 출력 파일명과 shape는 바뀌면 안 된다.
- 즉:
  - 항상 `activity_plan.json`은 존재해야 함
  - 다만 `activity_plan.status.json`에서 `fallback_used: true`로 기록

### 4. 단계별 재실행 기준을 고정
- `source_parse_agent` 실패:
  - 전체 run 재실행 또는 cached source artifact 사용
- `lesson_analysis_agent` 실패:
  - 한 차시만 재시도
- `activity_plan_agent` 실패:
  - 한 차시 repair 1회 후 fallback
- `html_card_agent` 실패:
  - 해당 차시만 deterministic renderer fallback
- `numbers_compose_agent` 실패:
  - compose 단계만 재시도

## 추천 fallback 정책

### source_parse 단계
- 1차:
  - cached artifact 재사용
- 2차:
  - title-only parsing
- 최종:
  - run 중단

### lesson_analysis 단계
- 1차:
  - Gemini 재호출
- 2차:
  - 더 좁은 chunk로 재호출
- 최종:
  - baseline deterministic analysis 사용

### lesson_review 단계
- `pass`:
  - 다음 단계 진행
- `pass_with_warning`:
  - 경고 기록 후 다음 단계 진행
- `needs_revision`:
  - lesson_analysis 재생성 또는 사람 검토 대기
- `blocked`:
  - 해당 차시 중단

### activity_plan 단계
- 1차:
  - Gemini 초안
- 2차:
  - validation error를 붙인 repair pass
- 최종:
  - 로컬 deterministic activity plan 사용

### activity_review 단계
- `pass`:
  - 다음 단계 진행
- `pass_with_warning`:
  - 경고 기록 후 다음 단계 진행
- `needs_revision`:
  - activity_plan 재생성 또는 사람 검토 대기
- `blocked`:
  - HTML 단계로 진행하지 않음

### html 단계
- 1차:
  - 자유 HTML 또는 설계형 출력
- 2차:
  - HTML normalize
- 최종:
  - 템플릿 renderer fallback

### Numbers 단계
- 1차:
  - AppleScript 삽입
- 2차:
  - 동일 manifest 재시도
- 최종:
  - manifest까지만 남기고 `partial-with-warning`

### manifest_review 단계
- `pass`:
  - verify 진행
- `pass_with_warning`:
  - 경고 기록 후 verify 진행
- `needs_revision`:
  - manifest 재구성 또는 사람 검토 대기
- `blocked`:
  - Numbers 완료로 간주하지 않음

## agent별 권장 모델/실행 성격

### 생성형이 필요한 단계
- `lesson_analysis_agent`
- `activity_plan_agent`
- 조건부 `html_card_agent`

### 생성형이 필요 없는 단계
- `source_parse_agent`
- `capture_agent`
- `numbers_compose_agent`
- `verify_agent`

### 권장 이유
- 현재 병목은 Gemini 대기와 Numbers/캡처 쪽이다.
- 따라서 AI 에이전트는 필요한 곳에만 제한적으로 두는 것이 안정적이다.

## activity 설계와 html 설계의 분리 기준

### 기본 권장
- 논리적으로는 분리
- 실행상으로는 상황에 따라 통합 가능

### 왜 이렇게 가야 하나
- 의미 설계 실패와 HTML 설계 실패를 분리해 볼 수 있다.
- 단, 호출 수가 너무 늘면 속도가 떨어진다.

### 운영 기준
- 안정성이 우선인 모드:
  - `activity_plan_agent`와 `html_card_agent` 분리
- 속도가 우선인 모드:
  - `activity_plan_agent`가 `html_content`까지 생성
  - 단, status와 validation은 여전히 분리 기록

## 권장 운영 모드

### Mode A. Stable
- 목적:
  - 실사용용, 회귀 최소화
- 특징:
  - 템플릿 renderer 우선
  - Gemini는 lesson/activity planning만 담당
  - 사람 검토 게이트 유지

### Mode B. Freeform Experimental
- 목적:
  - 자유 HTML 탐색
- 특징:
  - `html_card_agent` 또는 freeform `activity_plan_agent` 사용
  - 더 강한 validation
  - 실패 시 템플릿 fallback 허용

### Mode C. Recovery
- 목적:
  - 빨리 결과 확보
- 특징:
  - textbook-only 또는 local activity fallback 허용
  - Numbers 파일 생성 자체를 우선

## run manifest 예시 항목
- `run_id`
- `workflow_mode`
- `input_catalog`
- `selected_unit`
- `selected_lessons`
- `stage_order`
- `section_count`
- `status_summary`
- `final_status`
- `final_output_file`

## 사람이 확인해야 하는 최소 게이트

### 필수 검토 1
- `lesson_analysis.json`
- `lesson_review.json`
- 확인 내용:
  - 차시명 정합성
  - 목표/개념의 교과서 근거

### 필수 검토 2
- `activity_plan.json`
- `activity_review.json`
- 확인 내용:
  - 활동이 교과서 반복이 아닌지
  - `ACTIVITY_RULE.md`와 `NumbersDesign.md`에 맞는지

### 선택 검토 3
- `render_manifest.json`
- `manifest_review.json`
- 확인 내용:
  - before / during / after 흐름
  - 객체 수와 배치 순서

### 검토와 승인의 분리 원칙
- `review agent`는 문제를 찾고 구조화하는 역할만 한다.
- `review agent`는 `approved`를 직접 부여하지 않는다.
- 최종 승인 상태 변경은 아래 둘 중 하나만 허용한다.
  - 사람 승인
  - 명시적으로 허용된 정책 엔진

## 가장 일관된 운영을 위한 최종 권장 셋업

### 필수 구성
- 오케스트레이터 1개
- 결정론 에이전트 4개
  - `source_parse_agent`
  - `capture_agent`
  - `numbers_compose_agent`
  - `verify_agent`
- 생성형 에이전트 2개
  - `lesson_analysis_agent`
  - `activity_plan_agent`
- review 에이전트 3개
  - `review_lesson_agent`
  - `review_activity_agent`
  - `review_manifest_agent`
- 선택형 1개
  - `html_card_agent`

### 권장 기본값
- 기본 모드: `Stable`
- HTML 생성 기본값: 결정론 renderer
- Gemini 적용 범위 기본값:
  - `lesson_analysis`
  - `activity_plan`
- freeform HTML은 실험 모드에서만 활성화

## 최종 판단
- 전체 작업 워크플로우를 어떤 상황에서도 일관되게 유지하려면, “모델이 똑똑해야 한다”보다 “단계 계약이 고정되어야 한다”가 더 중요하다.
- 가장 좋은 설정은 다음 한 줄로 요약된다.
  - **고정된 stage 순서 + JSON artifact 계약 + 단계별 status 기록 + fallback 표준화**
