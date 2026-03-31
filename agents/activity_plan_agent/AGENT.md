# activity_plan_agent

## identity
- status: active
- layer: generation
- implementation: `scripts/activity_plan_agent.py`

## responsibility
- lesson analysis를 바탕으로 차시별 activity plan을 생성한다.
- 생성 결과를 정규화해 최종 `activity_plan.json`으로 확정한다.

## inputs
- required:
  - `sections/<lesson>/lesson_analysis.json`

## outputs
- `sections/<lesson>/activity_plan.prompt.md`
- `sections/<lesson>/activity_plan_ai.json`
- `sections/<lesson>/activity_plan.repair.prompt.md`
- `sections/<lesson>/activity_plan_ai_repair.json`
- `sections/<lesson>/activity_plan.json`
- `sections/<lesson>/activity_plan.status.json`

## allowed_tools
- local:
  - prompt assembly
  - local fallback builder
  - JSON normalization
- model:
  - Gemini CLI

## allowed_actions
- activity plan 생성
- repair prompt 재시도
- local fallback 사용
- lesson 단위 병렬 실행

## forbidden_actions
- source 경계 수정
- lesson analysis 수정
- HTML 렌더링 및 캡처
- Numbers 배치 제어

## rules
- activity plan generation은 반드시 이 Agent를 통해서만 수행한다.

## hook_contract
- trigger_if_missing:
  - `sections/<lesson>/activity_plan.json`
- unlocks:
  - `activity_review_agent`
  - `html_card_agent`

## success_criteria
- 각 lesson에 `activity_plan.json`이 생성된다.
- status에서 attempt, repair, fallback 여부가 기록된다.

## failure_modes
- Gemini timeout
- AI JSON 생성 실패
- repair 실패
- local fallback 사용
