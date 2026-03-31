# source_parse_agent

## identity
- status: deprecated
- layer: reading
- implementation: `scripts/source_parse_agent.py`

## responsibility
- 입력 config를 실행 가능한 run config로 확정한다.
- 차시별 교과서/보조자료 페이지 범위를 결정한다.
- source 수준의 구조 검토 결과를 남긴다.

## inputs
- required:
  - `configs/<config>.json`
- optional:
  - 진도표 원본 경로
  - 교과서 PDF 및 보조자료 PDF

## outputs
- `source/schedule_draft.json`
- `source/textbook_context.json`
- `source/runtime_config.json`
- `source/config_quality_review.json`
- `source/boundary_review.json`
- `source/supplement_review.json`
- `source/source_ai_review.json`
- `source/source_parse.status.json`

## allowed_tools
- local:
  - `generate_numbers_lesson.py`
  - deterministic boundary rules
- model:
  - Gemini sidecar review

## allowed_actions
- source range 확정
- source review 생성
- 멀티리소스 기본 정책 적용

## forbidden_actions
- lesson 의미 분석
- activity 생성
- render/output 수정

## rules
- deprecated transitional agent다.
- 신규 구조에서는 `source_boundary_agent`와 `source_validation_agent`로 대체한다.

## hook_contract
- trigger_if_missing:
  - legacy compatibility only
- unlocks:
  - none

## success_criteria
- `runtime_config.json`이 생성된다.
- review JSON이 생성된다.

## failure_modes
- sections 비어 있음
- 필수 source 미매칭
- source range 계산 실패
