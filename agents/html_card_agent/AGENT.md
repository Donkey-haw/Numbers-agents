# html_card_agent

## identity
- status: active
- layer: rendering
- implementation: `scripts/html_card_agent.py`

## responsibility
- 교과서 카드 HTML과 활동 HTML을 렌더 준비 상태로 만든다.
- capture 단계가 사용할 `html_manifest.json`을 만든다.

## inputs
- required:
  - `source/runtime_config.json`
  - `sections/*/activity_plan.json`

## outputs
- `render/runtime_config.json`
- `render/html_manifest.json`
- `render/html_card.status.json`
- `render/html/*.html`

## allowed_tools
- local:
  - HTML template rendering
  - manifest writing

## allowed_actions
- 교과서 카드 HTML 렌더
- 활동 HTML 렌더
- render runtime config 복사
- html manifest 생성

## forbidden_actions
- Gemini 호출
- 캡처 수행
- Numbers 삽입

## rules
- HTML card rendering은 반드시 이 Agent를 통해서만 수행한다.

## hook_contract
- trigger_if_missing:
  - `render/html_manifest.json`
- unlocks:
  - `capture_agent`

## success_criteria
- `html_manifest.json`이 생성된다.
- 교과서와 활동 HTML 파일이 생성된다.
- status가 `succeeded`다.

## failure_modes
- activity plan 누락
- HTML 렌더 실패
- manifest build 실패
