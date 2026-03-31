# Agent Test Plan

목표:
- 각 agent를 독립 책임 단위로 검증한다.
- 실패 지점을 `run_manifest` 전체가 아니라 agent 산출물 단위에서 확인한다.

공통 원칙:
- 기본적으로 `--keep-run-artifacts`를 켠다.
- 개별 stage 테스트는 `--stop-after <stage>`를 사용한다.
- 선행 stage 산출물이 필요한 agent는 그 이전 stage까지 먼저 실행한다.

## 1. source_parse_agent

실행:
```bash
python3 scripts/pipeline_orchestrator.py \
  --config configs/<config>.json \
  --stop-after source_parse_agent \
  --keep-run-artifacts
```

통과 조건:
- `source/runtime_config.json` 생성
- `source/config_quality_review.json` 생성
- `source/boundary_review.json` 생성
- `source/supplement_review.json` 생성
- `source/source_ai_review.json` 생성
- `source/source_parse.status.json` 상태가 `succeeded` 또는 `succeeded_with_warning`

## 2. lesson_analysis_agent

실행:
```bash
python3 scripts/pipeline_orchestrator.py \
  --config configs/<config>.json \
  --stop-after review_lesson_agent \
  --keep-run-artifacts
```

통과 조건:
- 각 lesson 디렉토리에 `lesson_analysis.json` 생성
- 각 lesson 디렉토리에 `lesson_review.json` 생성
- 각 lesson 디렉토리에 `lesson_analysis.status.json` 생성
- fallback 여부가 status 파일에서 판독 가능

## 3. activity_plan_agent

실행:
```bash
python3 scripts/pipeline_orchestrator.py \
  --config configs/<config>.json \
  --stop-after review_activity_agent \
  --keep-run-artifacts
```

통과 조건:
- 각 lesson 디렉토리에 `activity_plan.json` 생성
- 각 lesson 디렉토리에 `activity_review.json` 생성
- repair 시 `activity_plan.repair.prompt.md` 또는 `activity_plan_ai_repair.json` 생성
- fallback 여부가 status 파일에서 판독 가능

## 4. html_card_agent

실행:
```bash
python3 scripts/pipeline_orchestrator.py \
  --config configs/<config>.json \
  --stop-after html_card_agent \
  --keep-run-artifacts
```

통과 조건:
- `render/html_manifest.json` 생성
- `render/html_card.status.json` 상태가 `succeeded`
- `render/html/` 아래 활동 HTML 생성

## 5. capture_agent

실행:
```bash
python3 scripts/pipeline_orchestrator.py \
  --config configs/<config>.json \
  --stop-after capture_agent \
  --keep-run-artifacts
```

통과 조건:
- `render/render_manifest.json` 생성
- `render/capture.status.json` 상태가 `succeeded`
- `render/cards/` 아래 캡처 산출물 생성

## 6. numbers_compose_agent

실행:
```bash
python3 scripts/pipeline_orchestrator.py \
  --config configs/<config>.json \
  --stop-after numbers_compose_agent \
  --keep-run-artifacts
```

통과 조건:
- `output/numbers_compose.status.json` 상태가 `succeeded`
- run root 내부에 최종 `.numbers` 생성

## 7. review_manifest_agent

실행:
```bash
python3 scripts/pipeline_orchestrator.py \
  --config configs/<config>.json \
  --stop-after review_manifest_agent \
  --keep-run-artifacts
```

통과 조건:
- `render/manifest_review.json` 생성
- warning과 blocking issue가 구조적으로 기록됨

## 8. verify_agent

실행:
```bash
python3 scripts/pipeline_orchestrator.py \
  --config configs/<config>.json \
  --stop-after verify_agent \
  --keep-run-artifacts
```

통과 조건:
- `output/verify.status.json` 상태가 `succeeded`
- 최종 `.numbers`가 존재

## 권장 테스트 순서

1. `source_parse_agent`
2. `review_lesson_agent`
3. `review_activity_agent`
4. `capture_agent`
5. `verify_agent`

이 순서면 각 단계의 산출물과 downstream 영향이 가장 명확하게 드러난다.
