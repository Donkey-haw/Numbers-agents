# Agent Refactor Task Breakdown

## 목적
- [AGENT_BASED_NUMBERS_REFACTOR_PLAN.md](/Users/jonyeock/Desktop/Tool/NumbersAuto/AGENT_BASED_NUMBERS_REFACTOR_PLAN.md) 을 실제 구현 가능한 최소 작업 단위로 분해한다.
- 각 작업은 다음을 반드시 가진다.
  - 작업 목적
  - 선행 조건
  - 산출물
  - 상세 완료 조건
  - 실패 판정 기준

## 작업 분해 원칙
1. 한 작업은 하나의 책임만 가진다.
2. 한 작업은 되도록 하나의 산출물 계약만 확정한다.
3. 완료 조건은 코드 변경 자체가 아니라 `확인 가능한 결과`로 적는다.
4. “동작함” 대신 파일, 상태값, 실행 결과로 판정한다.

## Phase 0. 계약 고정

### T0-1. Run Artifact Root 표준 확정
- 목적:
  - 모든 실행이 동일한 run root 구조를 사용하게 한다.
- 선행 조건:
  - 없음
- 산출물:
  - `run_manifest.json` 구조 문서
  - 표준 디렉토리 구조 문서
- 상세 완료 조건:
  - run root가 `artifacts/runs/<run_id>/` 형태로 문서에 고정된다.
  - 아래 하위 경로가 명시된다.
    - `source/`
    - `sections/<lesson_id>/`
    - `render/`
    - `output/`
  - 기존 분산 경로(`artifacts/gemini`, `output/analysis`, `output/plans`)를 장기적으로 수렴시킬 대상 경로가 정의된다.
- 실패 판정 기준:
  - lesson 산출물과 render 산출물의 표준 저장 위치가 문서에 명시되지 않음

### T0-2. Stage 목록과 고정 순서 확정
- 목적:
  - 어떤 상황에서도 실행 순서가 바뀌지 않게 한다.
- 선행 조건:
  - T0-1
- 산출물:
  - stage order 문서
- 상세 완료 조건:
  - 아래 순서가 표준으로 명시된다.
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
  - stage 생략 가능 여부가 단계별로 명시된다.
  - `review` 없이 다음 단계로 넘어갈 수 없는 지점이 정의된다.
- 실패 판정 기준:
  - freeform mode, stable mode, recovery mode에서 순서가 다르게 설명됨

### T0-3. 공통 Status Enum 확정
- 목적:
  - 모든 stage의 상태를 같은 vocabulary로 기록한다.
- 선행 조건:
  - T0-2
- 산출물:
  - 공통 status enum 정의
  - review decision enum 정의
- 상세 완료 조건:
  - 공통 status 값이 문서에 고정된다.
    - `pending`
    - `running`
    - `succeeded`
    - `succeeded_with_warning`
    - `failed`
    - `failed_fallback_used`
    - `blocked`
  - review decision 값이 문서에 고정된다.
    - `pass`
    - `pass_with_warning`
    - `needs_revision`
    - `blocked`
- 실패 판정 기준:
  - stage마다 다른 상태 이름을 쓰는 예외가 남아 있음

## Phase 1. Run-Level 계약

### T1-1. `run_manifest.json` 필드 확정
- 목적:
  - 하나의 실행 전체를 설명하는 최상위 메타데이터를 만든다.
- 선행 조건:
  - T0-1
  - T0-3
- 산출물:
  - `run_manifest.json` 계약
- 상세 완료 조건:
  - 아래 필드가 필수 필드로 문서화된다.
    - `run_id`
    - `workflow_mode`
    - `config_path`
    - `selected_unit`
    - `selected_lessons`
    - `stage_order`
    - `started_at`
    - `finished_at`
    - `final_status`
    - `final_output_file`
  - `final_status`의 허용값이 정해진다.
    - `success`
    - `partial-with-warning`
    - `textbook-only`
    - `failed`
- 실패 판정 기준:
  - 실행이 끝났을 때 run 수준에서 성공/부분성공/실패를 구분할 수 없음

### T1-2. Stage Summary 집계 규칙 확정
- 목적:
  - run manifest에서 각 stage 결과를 한 번에 볼 수 있게 한다.
- 선행 조건:
  - T1-1
- 산출물:
  - `status_summary` 정의
- 상세 완료 조건:
  - 각 stage별 summary entry 형식이 문서에 정의된다.
  - 최소 포함 필드:
    - `stage`
    - `status`
    - `fallback_used`
    - `warning_count`
    - `error_count`
- 실패 판정 기준:
  - run 수준에서 어느 stage가 실패했는지 즉시 알 수 없음

## Phase 2. Source Parse Stage

### T2-1. `source_parse_agent` 입력 계약 확정
- 목적:
  - source parse stage가 무엇을 읽는지 고정한다.
- 선행 조건:
  - T0-2
- 산출물:
  - 입력 계약 문서
- 상세 완료 조건:
  - 허용 입력이 명시된다.
    - 원본 PDF
    - 진도표 PDF/이미지
    - 기존 config
    - `resource_catalog.json`
    - `resource_index.json`
    - `unit_bundle.json`
  - direct config와 scan artifact 기반 실행의 우선순위가 정의된다.
- 실패 판정 기준:
  - 같은 단원을 상황에 따라 전혀 다른 입력 방식으로 설명해야 함

### T2-2. `schedule_draft.json` 계약 확정
- 목적:
  - 차시명 초안과 진도표 파싱 결과를 고정 구조로 저장한다.
- 선행 조건:
  - T2-1
- 산출물:
  - `schedule_draft.json` 계약
- 상세 완료 조건:
  - 필수 필드가 정의된다.
    - `schema_version`
    - `generated_at`
    - `unit_title`
    - `sections[]`
  - 각 section의 최소 필드가 정의된다.
    - `sheet_name`
    - `lesson_title`
    - `title_query`
    - `chart_source`
- 실패 판정 기준:
  - 차시명 초안이 stage 간 공유 가능한 구조로 정리되지 않음

### T2-3. `textbook_context.json` 계약 확정
- 목적:
  - lesson analysis stage가 읽을 차시별 텍스트 문맥을 고정한다.
- 선행 조건:
  - T2-2
- 산출물:
  - `textbook_context.json` 계약
- 상세 완료 조건:
  - 각 차시에 대해 다음 정보가 존재해야 한다.
    - `sheet_name`
    - `lesson_title`
    - `title_query`
    - `pdf_pages`
    - `extracted_text`
    - `baseline_analysis_path` 또는 baseline summary
  - 인접 차시 정보 포함 여부가 정의된다.
- 실패 판정 기준:
  - lesson analysis 단계가 여전히 원본 PDF를 직접 읽어야 함

### T2-4. `runtime_config.json` 계약 확정
- 목적:
  - compose 단계가 사용할 실행용 config를 표준화한다.
- 선행 조건:
  - T2-3
- 산출물:
  - `runtime_config.json` 계약
- 상세 완료 조건:
  - `.numbers` 생성에 필요한 최소 필드가 정의된다.
    - `template_path`
    - `output_file`
    - `sections`
    - `resources`
    - `footer`
- 실패 판정 기준:
  - compose 단계가 여전히 임의 config 형식에 의존함

### T2-5. `source_parse.status.json` 계약 확정
- 목적:
  - source parse 단계의 성공/경고/실패를 기록한다.
- 선행 조건:
  - T2-4
- 산출물:
  - `source_parse.status.json` 계약
- 상세 완료 조건:
  - 필수 필드가 모두 정의된다.
    - `stage`
    - `status`
    - `run_id`
    - `started_at`
    - `finished_at`
    - `input_refs`
    - `output_refs`
    - `warnings`
    - `errors`
  - `title-only fallback used` 같은 대표 warning 사례가 명시된다.
- 실패 판정 기준:
  - source parse fallback이 조용히 일어나고 기록되지 않음

## Phase 3. Lesson Analysis Stage

### T3-1. `lesson_analysis_ai.json` 계약 확정
- 목적:
  - Gemini raw proposal을 저장하는 구조를 분리한다.
- 선행 조건:
  - T2-3
- 산출물:
  - `lesson_analysis_ai.json` 계약
- 상세 완료 조건:
  - raw proposal과 normalized final output의 차이를 문서에 구분한다.
  - AI proposal이 final input으로 직접 쓰이지 않는다고 명시한다.
- 실패 판정 기준:
  - `lesson_analysis_ai.json`과 `lesson_analysis.json` 역할이 섞여 있음

### T3-2. `lesson_analysis.json` 최종 계약 확정
- 목적:
  - downstream가 읽는 유일한 lesson 분석 파일을 고정한다.
- 선행 조건:
  - T3-1
- 산출물:
  - `lesson_analysis.json` 계약
- 상세 완료 조건:
  - 필수 필드가 정의된다.
    - `lesson_id`
    - `sheet_name`
    - `lesson_title`
    - `pdf_pages`
    - `essential_question`
    - `learning_goals`
    - `key_concepts`
    - `vocabulary`
    - `misconceptions`
    - `content_chunks`
    - `source_page_refs`
    - `analysis_confidence`
  - activity 단계는 이 파일만 읽는다고 명시된다.
- 실패 판정 기준:
  - activity 단계가 여전히 prompt context나 baseline JSON을 직접 참조함

### T3-3. `lesson_analysis.status.json` 계약 확정
- 목적:
  - lesson analysis stage의 재시도와 fallback을 기록한다.
- 선행 조건:
  - T3-2
- 산출물:
  - `lesson_analysis.status.json` 계약
- 상세 완료 조건:
  - 필수 필드:
    - `stage`
    - `lesson_id`
    - `status`
    - `model`
    - `attempt_count`
    - `fallback_used`
    - `validation_errors`
  - `fallback_used`가 false/true만이 아니라 원인 문자열을 가질지 여부가 정의된다.
- 실패 판정 기준:
  - lesson fallback이 발생했는지 run 결과만으로 알 수 없음

### T3-4. `lesson_review.json` 계약 확정
- 목적:
  - lesson review를 별도 stage 산출물로 고정한다.
- 선행 조건:
  - T3-3
- 산출물:
  - `lesson_review.json` 계약
- 상세 완료 조건:
  - 필수 필드:
    - `stage`
    - `lesson_id`
    - `status`
    - `decision`
    - `findings`
    - `blocking_issues`
    - `warnings`
  - `findings` 배열의 최소 항목 형식이 정의된다.
    - `severity`
    - `message`
    - `evidence_refs`
- 실패 판정 기준:
  - review 결과가 자연어 메모 수준에 머무르고 구조화되지 않음

## Phase 4. Activity Planning Stage

### T4-1. `activity_plan_ai.json` 계약 확정
- 목적:
  - Gemini activity raw proposal을 final plan과 분리한다.
- 선행 조건:
  - T3-2
- 산출물:
  - `activity_plan_ai.json` 계약
- 상세 완료 조건:
  - AI raw proposal이 review/repair 대상이라는 점이 명시된다.
- 실패 판정 기준:
  - raw proposal을 바로 render input으로 사용할 수 있게 열어둠

### T4-2. `activity_plan.json` 최종 계약 확정
- 목적:
  - HTML stage가 읽는 유일한 activity planning 입력을 고정한다.
- 선행 조건:
  - T4-1
- 산출물:
  - `activity_plan.json` 계약
- 상세 완료 조건:
  - activity별 필수 필드가 정의된다.
    - `activity_id`
    - `lesson_id`
    - `object_role`
    - `lesson_flow_stage`
    - `activity_type`
    - `level`
    - `learning_goal`
    - `prompt_text`
    - `source_refs`
    - `student_writing_zones`
    - `estimated_minutes`
    - `review_status`
  - `student_writing_zones`의 필수 하위 필드가 정의된다.
    - `zone_id`
    - `label`
    - `input_area_type`
    - `min_height`
- 실패 판정 기준:
  - HTML 단계가 활동 의미를 보충 추론해야만 렌더 가능함

### T4-3. `activity_plan.status.json` 계약 확정
- 목적:
  - repair pass, validation fail, fallback 사용 여부를 기록한다.
- 선행 조건:
  - T4-2
- 산출물:
  - `activity_plan.status.json` 계약
- 상세 완료 조건:
  - 필수 필드:
    - `stage`
    - `lesson_id`
    - `status`
    - `attempt_count`
    - `repair_attempted`
    - `fallback_used`
    - `validation_errors`
  - `validation_errors` 예시가 문서에 들어간다.
    - missing writing zone fields
    - invalid activity type
    - insufficient source refs
- 실패 판정 기준:
  - “Gemini가 이상했다” 수준의 모호한 상태만 남음

### T4-4. `activity_review.json` 계약 확정
- 목적:
  - activity review를 별도 구조화 산출물로 남긴다.
- 선행 조건:
  - T4-3
- 산출물:
  - `activity_review.json` 계약
- 상세 완료 조건:
  - 검토 기준이 문서에 고정된다.
    - 교과서 반복 여부
    - `ACTIVITY_RULE.md` 적합성
    - `NumbersDesign.md` 적합성
    - before / during / after 역할 적절성
  - `decision`에 따라 다음 stage 진행 규칙이 정의된다.
- 실패 판정 기준:
  - review 결과가 다음 stage gating에 연결되지 않음

## Phase 5. HTML / Render Stage

### T5-1. `html_assets.json` 계약 확정
- 목적:
  - HTML stage 결과를 manifest 이전 독립 계약으로 만든다.
- 선행 조건:
  - T4-2
- 산출물:
  - `html_assets.json` 계약
- 상세 완료 조건:
  - activity별 HTML 자산 정보가 정의된다.
    - `asset_id`
    - `lesson_id`
    - `source_activity_id`
    - `render_mode`
    - `html_path`
    - `html_origin`
  - `render_mode` 허용값이 정의된다.
    - `template`
    - `freeform`
    - `fallback_template`
- 실패 판정 기준:
  - freeform과 template 결과가 같은 타입으로 섞여 후속 단계가 분기 처리 불가

### T5-2. `html_render.status.json` 계약 확정
- 목적:
  - HTML normalize, render fallback, render mode를 기록한다.
- 선행 조건:
  - T5-1
- 산출물:
  - `html_render.status.json` 계약
- 상세 완료 조건:
  - 필수 필드:
    - `stage`
    - `lesson_id`
    - `status`
    - `render_mode`
    - `html_count`
    - `warnings`
  - freeform normalize warning 사례가 정의된다.
- 실패 판정 기준:
  - html stage가 fallback template로 내려갔는지 알 수 없음

### T5-3. `capture_assets.json` 계약 확정
- 목적:
  - 캡처 결과를 compose 전에 독립 계약으로 둔다.
- 선행 조건:
  - T5-1
- 산출물:
  - `capture_assets.json` 계약
- 상세 완료 조건:
  - asset별 필수 필드가 정의된다.
    - `asset_id`
    - `asset_type`
    - `sheet_name`
    - `image_path`
    - `capture_size`
    - `dimensions`
  - 교과서 asset과 활동 asset이 같은 배열 contract로 표현된다고 정의한다.
- 실패 판정 기준:
  - compose 단계가 여전히 html이나 raw image folder를 직접 스캔해야 함

### T5-4. `capture.status.json` 계약 확정
- 목적:
  - Playwright 캡처 단계의 성공/실패를 기록한다.
- 선행 조건:
  - T5-3
- 산출물:
  - `capture.status.json` 계약
- 상세 완료 조건:
  - 필수 필드:
    - `stage`
    - `status`
    - `captured_count`
    - `failed_assets`
    - `warnings`
- 실패 판정 기준:
  - 캡처 실패가 manifest 실패와 섞여 보임

## Phase 6. Compose / Verify Stage

### T6-1. `render_manifest.json` 계약 최종 확정
- 목적:
  - Numbers 삽입 직전의 최종 배치 계약을 고정한다.
- 선행 조건:
  - T5-3
- 산출물:
  - `render_manifest.json` 계약
- 상세 완료 조건:
  - 필수 필드:
    - `asset_id`
    - `asset_type`
    - `sheet_name`
    - `insert_order`
    - `image_path`
    - `dimensions`
  - before / during / after 배치 정보가 필요한지 여부가 확정된다.
- 실패 판정 기준:
  - compose stage가 추가 추론으로 asset 순서를 계산해야 함

### T6-2. `numbers_insert.status.json` 계약 확정
- 목적:
  - AppleScript compose 결과를 기록한다.
- 선행 조건:
  - T6-1
- 산출물:
  - `numbers_insert.status.json` 계약
- 상세 완료 조건:
  - 필수 필드:
    - `stage`
    - `status`
    - `manifest_path`
    - `output_file`
    - `applescript_attempts`
    - `errors`
  - first try fail / retry success 같은 사례를 표현할 수 있어야 한다.
- 실패 판정 기준:
  - compose 재시도 이력이 남지 않음

### T6-3. `manifest_review.json` 계약 확정
- 목적:
  - Numbers 삽입 전후의 배치 검토를 구조화한다.
- 선행 조건:
  - T6-2
- 산출물:
  - `manifest_review.json` 계약
- 상세 완료 조건:
  - 검토 항목이 문서에 고정된다.
    - before / during / after 흐름
    - asset 누락
    - insert_order 이상
    - 객체 수 불일치
- 실패 판정 기준:
  - review manifest가 단순 로그에 머무름

### T6-4. `verify.status.json` 계약 확정
- 목적:
  - 최종 결과 검증을 표준화한다.
- 선행 조건:
  - T6-3
- 산출물:
  - `verify.status.json` 계약
- 상세 완료 조건:
  - 필수 필드:
    - `stage`
    - `status`
    - `sheet_names_expected`
    - `sheet_names_actual`
    - `asset_count_expected`
    - `asset_count_actual`
    - `warnings`
  - `partial-with-warning` 판정 조건이 정의된다.
- 실패 판정 기준:
  - 최종 산출물의 부분 성공/완전 성공 기준이 불명확함

## Phase 7. Review / Approval 운영 규칙

### T7-1. Review와 Approval 분리 규칙 확정
- 목적:
  - review agent가 승인자가 되지 않도록 막는다.
- 선행 조건:
  - T3-4
  - T4-4
  - T6-3
- 산출물:
  - 운영 규칙 문서
- 상세 완료 조건:
  - review agent는 `approved`를 직접 부여하지 않는다고 명시된다.
  - 승인 경로는 아래 둘 중 하나만 허용된다고 명시된다.
    - 사람 승인
    - 명시된 정책 엔진
- 실패 판정 기준:
  - review 결과만으로 auto-approve가 가능하게 열려 있음

### T7-2. Stage Gating 규칙 확정
- 목적:
  - review 결과에 따라 다음 단계 진행 여부를 고정한다.
- 선행 조건:
  - T7-1
- 산출물:
  - gating 규칙 표
- 상세 완료 조건:
  - `pass`, `pass_with_warning`, `needs_revision`, `blocked` 각각의 다음 행동이 정해진다.
  - lesson, activity, manifest review 각각에 대한 행동 차이가 정의된다.
- 실패 판정 기준:
  - review decision이 있어도 오케스트레이터 행동이 정해지지 않음

## Phase 8. 운영 모드 분리

### T8-1. Stable Mode 계약 확정
- 목적:
  - 실제 수업용 기본 모드를 고정한다.
- 선행 조건:
  - T5-1
  - T7-2
- 산출물:
  - stable mode 정의
- 상세 완료 조건:
  - template renderer 우선
  - review required
  - activity planning까지만 Gemini 사용
  가 명시된다.
- 실패 판정 기준:
  - stable mode에서 freeform HTML이 기본 활성화됨

### T8-2. Freeform Experimental Mode 계약 확정
- 목적:
  - 자유 HTML 실험 모드의 범위를 고정한다.
- 선행 조건:
  - T8-1
- 산출물:
  - freeform mode 정의
- 상세 완료 조건:
  - freeform 허용 범위
  - validation 강화 조건
  - fallback policy
  가 문서에 명시된다.
- 실패 판정 기준:
  - freeform mode와 stable mode가 같은 검증 규칙을 공유해 구분이 사라짐

### T8-3. Recovery Mode 계약 확정
- 목적:
  - 산출물 확보 우선 모드의 fallback 체계를 고정한다.
- 선행 조건:
  - T8-2
- 산출물:
  - recovery mode 정의
- 상세 완료 조건:
  - lesson/activity 실패 시 어느 단계까지 fallback 허용되는지 정의된다.
  - `textbook-only`, `partial-with-warning` 전환 조건이 문서화된다.
- 실패 판정 기준:
  - recovery mode에서도 전체 실패와 부분 실패가 구분되지 않음

## Phase 9. 오케스트레이터 도입

### T9-1. Orchestrator 책임 경계 확정
- 목적:
  - 오케스트레이터가 stage worker를 대체하지 않도록 한다.
- 선행 조건:
  - T1-2
  - T7-2
- 산출물:
  - orchestrator responsibility 문서
- 상세 완료 조건:
  - 오케스트레이터가 해야 하는 일과 하면 안 되는 일이 고정된다.
  - 특히 아래 금지 항목이 명시된다.
    - lesson 내용 직접 수정
    - activity HTML 직접 작성
    - page range 직접 재추론
- 실패 판정 기준:
  - orchestrator가 stage 로직을 다시 품기 시작함

### T9-2. Stage Invocation 계약 확정
- 목적:
  - 각 agent 호출 입출력 형식을 통일한다.
- 선행 조건:
  - T9-1
- 산출물:
  - stage invocation spec
- 상세 완료 조건:
  - 모든 stage가 최소 공통 입력을 가진다.
    - `run_id`
    - `input_refs`
    - `output_dir`
    - `workflow_mode`
  - 모든 stage가 최소 공통 출력을 가진다.
    - `final json`
    - `status json`
- 실패 판정 기준:
  - stage마다 실행 인터페이스가 제각각이라 오케스트레이터가 특수처리를 많이 해야 함

## 최종 완료 기준

### 문서 완료 기준
- 각 stage별 입력/출력/상태/검토 계약이 모두 정의되어 있다.
- 각 작업의 완료 조건이 파일과 상태값 기준으로 판정 가능하다.
- fallback과 review가 문서 수준에서 stage로 고정되어 있다.

### 구조 완료 기준
- 사용자가 “어디서 실패했는가”를 stage 이름으로 말할 수 있다.
- 한 차시만 재실행 가능한 단위가 정의돼 있다.
- review와 approval이 분리돼 있다.
- stable / freeform / recovery 세 모드의 차이가 명확하다.

## 가장 중요한 판정 기준
- 이 문서의 목표는 “할 일을 많이 적는 것”이 아니다.
- 진짜 완료 판정 기준은 다음 한 줄이다.
  - **모든 단계가 자기 입력과 출력과 실패 상태를 독립적으로 설명할 수 있어야 한다.**
