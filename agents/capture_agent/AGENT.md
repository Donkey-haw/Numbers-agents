# capture_agent

## identity
- status: active
- layer: rendering
- implementation: `scripts/capture_agent.py`

## responsibility
- HTML과 교과서 카드 자산을 실제 이미지 자산으로 캡처한다.
- Numbers 합성에 직접 쓰는 `render_manifest.json`을 만든다.

## inputs
- required:
  - `render/html_manifest.json`
  - `sections/*/activity_plan.json`

## outputs
- `render/render_manifest.json`
- `render/capture.status.json`
- `render/cards/*`

## allowed_tools
- local:
  - card capture helpers
  - asset manifest generation
- platform:
  - Playwright or browser capture stack

## allowed_actions
- 교과서 카드 캡처
- activity HTML 캡처
- 최종 asset manifest 작성

## forbidden_actions
- activity 의미 수정
- Numbers 배치 수행

## rules
- card capture는 반드시 이 Agent를 통해서만 수행한다.

## hook_contract
- trigger_if_missing:
  - `render/render_manifest.json`
- unlocks:
  - `numbers_compose_agent`
  - `review_manifest_agent`

## success_criteria
- `render_manifest.json`이 생성된다.
- 캡처된 asset 수가 0보다 크다.
- status가 `succeeded`다.

## failure_modes
- html manifest 누락
- capture 실패
- asset manifest build 실패
