# activity_review_agent

## identity
- status: active
- layer: verification
- implementation: `scripts/activity_review_agent.py`

## responsibility
- activity plan 산출물을 검증한다.
- blocked/warning 판정을 기록한다.

## inputs
- required:
  - `sections/<lesson>/activity_plan.json`
  - `sections/<lesson>/lesson_analysis.json`

## outputs
- `sections/<lesson>/activity_review.json`
- `sections/<lesson>/activity_review.status.json`

## allowed_tools
- local:
  - deterministic review rules
  - structural checks

## allowed_actions
- activity structure 검증
- warning / blocked 판정
- review status 생성

## forbidden_actions
- activity 재생성
- HTML 렌더링
- Numbers 배치 제어

## rules
- activity plan structural review는 반드시 이 Agent를 통해서만 수행한다.

## hook_contract
- trigger_if_missing:
  - `sections/<lesson>/activity_review.json`
- unlocks:
  - `html_card_agent`

## success_criteria
- activity review JSON과 status가 생성된다.
- blocked 상태가 아니면 render 단계가 가능하다.

## failure_modes
- activity plan 누락
- review rule 실패
- 검증 중 예외
