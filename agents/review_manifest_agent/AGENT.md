# review_manifest_agent

## identity
- status: active
- layer: verification
- implementation: `scripts/review_manifest_agent.py`

## responsibility
- render manifest의 배치 논리를 사후 검토한다.
- 교과서 카드 우선 배치와 before/during/after 흐름을 확인한다.

## inputs
- required:
  - `render/render_manifest.json`

## outputs
- `render/manifest_review.json`
- `render/manifest_rule_review.json`

## allowed_tools
- local:
  - manifest rule checks
- model:
  - Gemini sidecar review

## allowed_actions
- sheet별 asset 존재 여부 확인
- textbook-first 규칙 확인
- activity flow 순서 확인
- sidecar review 생성

## forbidden_actions
- Numbers 파일 수정
- 자산 재생성
- AI review로 manifest 직접 수정

## rules
- render manifest review는 반드시 이 Agent를 통해서만 수행한다.

## hook_contract
- trigger_if_missing:
  - `render/manifest_review.json`
- unlocks:
  - `verify_agent`

## success_criteria
- `manifest_review.json`이 생성된다.
- decision이 `pass` 또는 `pass_with_warning`다.

## failure_modes
- asset 없음
- manifest rule 위반
- AI sidecar review 실패
