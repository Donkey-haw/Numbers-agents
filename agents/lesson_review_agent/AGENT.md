# lesson_review_agent

## identity
- status: active
- layer: verification
- implementation: `scripts/lesson_review_agent.py`

## responsibility
- lesson analysis 산출물을 검증한다.
- 필수 필드와 구조적 경고를 기록한다.

## inputs
- required:
  - `sections/<lesson>/lesson_analysis.json`

## outputs
- `sections/<lesson>/lesson_review.json`
- `sections/<lesson>/lesson_review.status.json`

## allowed_tools
- local:
  - deterministic review rules
  - JSON schema-like checks

## allowed_actions
- 필수 필드 검증
- 구조 경고 기록
- lesson review 상태 산출

## forbidden_actions
- lesson analysis 재생성
- source 경계 수정
- activity 생성

## rules
- lesson analysis structural review는 반드시 이 Agent를 통해서만 수행한다.

## hook_contract
- trigger_if_missing:
  - `sections/<lesson>/lesson_review.json`
- unlocks:
  - `activity_plan_agent`

## success_criteria
- lesson review JSON과 status가 생성된다.
- blocked 상태가 아니면 downstream이 진행 가능하다.

## failure_modes
- lesson analysis 누락
- 필수 필드 누락
- 검증 중 예외
