# source_boundary_agent

## identity
- status: active
- layer: reading
- implementation: `scripts/source_boundary_agent.py`

## responsibility
- 입력 config를 기준으로 차시별 source boundary를 확정한다.
- 후보 페이지 맥락을 읽고 시작/종료 페이지를 추론한다.
- 실행에 필요한 source 산출물만 생성한다.

## inputs
- required:
  - `configs/<config>.json`
- optional:
  - 진도표 원본 경로

## outputs
- `source/resource_page_catalog.json`
- `source/source_boundary.candidates.json`
- `source/source_boundary.ai.json`
- `source/source_boundary.batches.json`
- `source/schedule_draft.json`
- `source/textbook_context.json`
- `source/runtime_config.json`
- `source/source_boundary.status.json`

## allowed_tools
- local:
  - PyMuPDF
  - local JSON serialization
  - token scoring / candidate preselection
- model:
  - Gemini CLI

## allowed_actions
- resource page catalog 생성
- lesson별 candidate page 집합 생성
- batch 단위 boundary inference 실행
- source range 정규화

## forbidden_actions
- source 품질 검토
- lesson/activity 생성
- render 또는 Numbers 조작

## rules
- 현재 transitional source boundary 결정은 반드시 이 Agent를 통해서만 수행한다.
- `runtime_config.json`의 source range 확정은 이 Agent의 출력만 사용한다.

## hook_contract
- trigger_if_missing:
  - `source/runtime_config.json`
- unlocks:
  - `source_validation_agent`
  - `lesson_analysis_agent`

## success_criteria
- `runtime_config.json`이 생성된다.
- 각 section에 `source_ranges`가 기록된다.
- `source_boundary.status.json` 상태가 `succeeded` 또는 `succeeded_with_warning`다.

## failure_modes
- Gemini timeout
- boundary payload schema 불일치
- 필수 source 미매칭
- invalid page range

## notes
- 장기적으로는 `page_candidate_agent`와 `boundary_decision_agent`로 분해될 transitional agent다.
