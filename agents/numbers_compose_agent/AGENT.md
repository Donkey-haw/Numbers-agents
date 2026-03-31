# numbers_compose_agent

## identity
- status: active
- layer: output
- implementation: `scripts/numbers_compose_agent.py`

## responsibility
- 최종 manifest를 Apple Numbers 템플릿에 삽입한다.
- 시트 생성과 카드 배치를 실제 `.numbers` 파일로 반영한다.

## inputs
- required:
  - `render/render_manifest.json`

## outputs
- `output/<final>.numbers`
- `output/numbers_compose.status.json`

## allowed_tools
- local:
  - manifest reader
  - template copy helpers
- platform:
  - AppleScript / Numbers automation

## allowed_actions
- Numbers 템플릿 복사
- manifest 기반 자산 삽입
- 삽입된 시트 목록 검증

## forbidden_actions
- asset 재렌더링
- source/lesson/activity 내용 재계산

## rules
- Numbers composition은 반드시 이 Agent를 통해서만 수행한다.

## hook_contract
- trigger_if_missing:
  - `output/<final>.numbers`
- unlocks:
  - `verify_agent`

## success_criteria
- 최종 `.numbers` 파일이 생성된다.
- status가 `succeeded`다.
- 삽입된 sheet name 목록이 기록된다.

## failure_modes
- render manifest 누락
- Numbers automation 실패
- output file 생성 실패
