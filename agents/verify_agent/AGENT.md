# verify_agent

## identity
- status: active
- layer: verification
- implementation: `scripts/verify_agent.py`

## responsibility
- 최종 `.numbers` 출력이 존재하고 기본 검증을 통과하는지 확인한다.

## inputs
- required:
  - `output/<final>.numbers`

## outputs
- `output/verify.status.json`
- `output/verify_rule_review.json`
- `output/verify_review.json`

## allowed_tools
- local:
  - file existence check
  - verification rule checks
- model:
  - Gemini sidecar review

## allowed_actions
- 최종 output 존재 여부 검증
- verification status 기록
- 최종 run 상태 요약

## forbidden_actions
- Numbers 파일 재조합
- upstream 산출물 수정
- AI review로 최종 파일 생성/수정

## rules
- final output verification은 반드시 이 Agent를 통해서만 수행한다.

## hook_contract
- trigger_if_missing:
  - `output/verify.status.json`
- unlocks:
  - run finalization

## success_criteria
- `verify.status.json` 상태가 `succeeded`다.
- 최종 `.numbers` 파일이 존재한다.

## failure_modes
- output file 누락
- verification rule 실패
- AI sidecar review 실패
