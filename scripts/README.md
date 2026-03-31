# Scripts

## Core Pipeline
현재 AGENT 기반 Numbers 자동 생성에서 직접 쓰는 핵심 스크립트는 아래다.

- [pipeline_orchestrator.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/pipeline_orchestrator.py)
- [runtime_driven_agents.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/runtime_driven_agents.py)
- [source_boundary_agent.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/source_boundary_agent.py)
- [source_validation_agent.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/source_validation_agent.py)
- [lesson_analysis_agent.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/lesson_analysis_agent.py)
- [activity_plan_agent.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/activity_plan_agent.py)
- [html_card_agent.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/html_card_agent.py)
- [capture_agent.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/capture_agent.py)
- [numbers_compose_agent.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/numbers_compose_agent.py)
- [review_manifest_agent.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/review_manifest_agent.py)
- [verify_agent.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/verify_agent.py)
- [pipeline_contracts.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/pipeline_contracts.py)
- [render_pipeline_support.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/render_pipeline_support.py)
- [agent_runtime.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/agent_runtime.py)

현재 AI stage는 아래 AGENT 문서를 실제 runtime prompt spec으로 사용한다.

- [agents/source_boundary_agent/AGENT.md](/Users/jonyeock/Desktop/Tool/NumbersAuto/agents/source_boundary_agent/AGENT.md)
- [agents/source_validation_agent/AGENT.md](/Users/jonyeock/Desktop/Tool/NumbersAuto/agents/source_validation_agent/AGENT.md)
- [agents/lesson_analysis_agent/AGENT.md](/Users/jonyeock/Desktop/Tool/NumbersAuto/agents/lesson_analysis_agent/AGENT.md)
- [agents/activity_plan_agent/AGENT.md](/Users/jonyeock/Desktop/Tool/NumbersAuto/agents/activity_plan_agent/AGENT.md)
- [agents/review_manifest_agent/AGENT.md](/Users/jonyeock/Desktop/Tool/NumbersAuto/agents/review_manifest_agent/AGENT.md)

이 파이프라인이 내부적으로 재사용하는 기반 스크립트:

- [generate_numbers_lesson.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/generate_numbers_lesson.py)
- [generate_numbers_with_activities.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/generate_numbers_with_activities.py)
- [generate_numbers_with_auto_activities.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/generate_numbers_with_auto_activities.py)
- [generate_activity_plan.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/generate_activity_plan.py)
- [generate_lesson_analysis.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/generate_lesson_analysis.py)
- [render_activity_html.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/render_activity_html.py)
- [run_gemini_cli_pipeline.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/run_gemini_cli_pipeline.py)

## Config Authoring
현재 기준 경로는 manual page selection이며, 핵심은 `config`를 `pdf_pages` 기반 final config로 만드는 것이다.

레거시 진도표/초안 생성 보조 스크립트:

- [parse_progress_chart_pdf.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/parse_progress_chart_pdf.py)
- [draft_config_from_progress_chart.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/draft_config_from_progress_chart.py)
- [ocr_progress_chart.swift](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/ocr_progress_chart.swift)

일회성 정리 스크립트는 [archive/scripts/one_off](/Users/jonyeock/Desktop/Tool/NumbersAuto/archive/scripts/one_off) 로 이동했다.

예시:

```bash
python3 scripts/pipeline_orchestrator.py \
  --config configs/social_6_1_unit2_state_agencies.json
```

기존 교과서 카드 생성기만 단독으로 실행할 때:

```bash
python3 scripts/generate_numbers_lesson.py \
  --config configs/social_6_1_unit2_state_agencies.json
```

교과서 카드와 이미 준비된 활동 계획을 함께 넣을 때:

```bash
python3 scripts/generate_numbers_with_activities.py \
  --config configs/democracy_election_with_intro.json \
  --activity-plan examples/activity_plan.sample.json
```

교과서 분석부터 활동 계획 자동 생성까지 한 번에 실행할 때:

```bash
python3 scripts/generate_numbers_with_auto_activities.py \
  --config configs/democracy_election_with_intro.json
```

`gemini` CLI가 설치되어 있으면 위 명령은 기본적으로 Gemini 파이프라인을 사용한다.
로컬 규칙 생성기로 강제하려면 `--local-only`를 사용한다.

```bash
python3 scripts/generate_numbers_with_auto_activities.py \
  --config configs/democracy_election_with_intro.json \
  --local-only
```

Gemini CLI를 붙여 차시 해석과 활동 추천을 AI 보조로 생성할 때:

```bash
python3 scripts/run_gemini_cli_pipeline.py \
  --config configs/social_6_1_unit2_state_agencies.json \
  --gemini-bin gemini \
  --max-workers 2 \
  --gemini-timeout-sec 120 \
  --dry-run
```

레거시 진도표 PDF를 구조화 JSON으로 정리할 때:

```bash
python3 scripts/parse_progress_chart_pdf.py \
  --pdf "6학년 1학기 사회 진도표.pdf" \
  --output configs/social_6_1_progress_chart.json
```

레거시 진도표 이미지에서 config 초안을 만들 때:

```bash
python3 scripts/draft_config_from_progress_chart.py \
  --image 진도표.png \
  --project-root . \
  --pdf-path "[사회]6_1_교과서.pdf" \
  --output-file "output/draft.numbers" \
  --config-output "configs/draft.json" \
  --footer "사회 6-1 · 1단원 · 민주화와 산업화로 달라진 생활 문화" \
  --start-after "② 민주화와 산업화로 달라진 생활 문화" \
  --stop-before "1단원 정리" \
  --end-before-query "민주주의와 선거"
```

## Notes
- 현재 메인 실행 경로는 `pipeline_orchestrator.py` 기반이다.
- 성공한 full run은 기본적으로 최종 `.numbers` 파일만 config의 `output_file` 경로에 남기고, `artifacts/runs/<run_id>/`는 자동 삭제한다.
- run artifacts를 보존하려면 `--keep-run-artifacts`를 사용한다.
- bundle/index 실험 경로 스크립트는 [archive/scripts/support](/Users/jonyeock/Desktop/Tool/NumbersAuto/archive/scripts/support) 로 이동했다.
- 단원 전용 또는 실험용 구형 스크립트는 [archive/scripts/legacy](/Users/jonyeock/Desktop/Tool/NumbersAuto/archive/scripts/legacy) 로 이동했다.
- 기존 실험용 config는 [archive/configs/legacy](/Users/jonyeock/Desktop/Tool/NumbersAuto/archive/configs/legacy) 로 이동했고, 현재 표준 config는 `configs/social_6_1_*.json` 형식을 사용한다.
- 새 작업은 [MANUAL_PAGE_SELECTION_WORKFLOW.md](/Users/jonyeock/Desktop/Tool/NumbersAuto/MANUAL_PAGE_SELECTION_WORKFLOW.md) 기준으로 `pdf_pages`가 확정된 final config를 먼저 만든 뒤 실행하는 것을 기본으로 한다.
- 진도표는 레거시 보조 입력일 뿐, 필수 입력이 아니다.
- 교과서 카드에는 해당 주제의 `주제 도입` 페이지를 반드시 포함한다.
- `주제 도입`이 별도 차시가 아닌 경우에는 첫 본차시 카드가 `주제 도입 + 본문 시작`을 함께 담도록 config를 잡는다.
- Gemini 기반 `lesson_analysis`와 `activity_plan` 생성의 기본 근거는 주교과서다.
- `supplement` resource는 기본적으로 Numbers 배치용 보조 자료이며, 활동 생성 단계에서는 참조하지 않아도 된다.
- 자동 활동 생성 흐름은 `lesson_analysis -> activity_plan -> HTML render -> Numbers insert` 순서다.
- 자동 생성된 활동은 기본적으로 `draft` 상태이며, `generate_numbers_with_auto_activities.py`는 이 초안도 바로 렌더할 수 있게 설계했다.
- Gemini CLI 연동은 `로컬 preextract -> Gemini JSON -> 로컬 normalize/validate -> 기존 Numbers 합성` 구조다.
- Gemini CLI 연동은 차시별 worker pool로 병렬 실행할 수 있고, `--max-workers`로 동시 차시 수를 조절한다.
- Gemini 프롬프트는 [prompts/gemini/system_analyze.md](/Users/jonyeock/Desktop/Tool/NumbersAuto/prompts/gemini/system_analyze.md), [prompts/gemini/user_analyze.md](/Users/jonyeock/Desktop/Tool/NumbersAuto/prompts/gemini/user_analyze.md), [prompts/gemini/system_plan.md](/Users/jonyeock/Desktop/Tool/NumbersAuto/prompts/gemini/system_plan.md), [prompts/gemini/user_plan.md](/Users/jonyeock/Desktop/Tool/NumbersAuto/prompts/gemini/user_plan.md)에 분리했다.
- `geminiCLI-freeactivity` 기준으로는 활동을 기존 템플릿 enum에 맞춰 추천받는 것이 아니라, Gemini가 [NumbersDesign.md](/Users/jonyeock/Desktop/Tool/NumbersAuto/NumbersDesign.md) 원칙에 따라 `html_content`를 직접 생성한다.
- 렌더러는 `html_content`가 있으면 그 HTML을 그대로 카드로 사용하고, 없으면 기존 템플릿 렌더 fallback을 사용한다.
- `--debug-artifacts`는 프롬프트 파일을 저장만 하고, 실제 Gemini 호출은 인라인 프롬프트를 사용한다.
- `.gitignore`가 `artifacts/`와 대부분의 `output/`을 무시하므로, 성공 실행의 증거는 기본적으로 git에 보존되지 않는다.
- 산출물 보관 규칙은 [RUN_OUTPUT_POLICY.md](/Users/jonyeock/Desktop/Tool/NumbersAuto/RUN_OUTPUT_POLICY.md) 를 따른다.

## Verification
Gemini 기반 자동 활동 생성이 실제로 적용되는지 확인할 때는 아래 순서로 본다.

1. `python3 scripts/generate_numbers_with_auto_activities.py --config ...` 실행
2. `artifacts/gemini/<config stem>/<timestamp>/run_summary.json` 생성 확인
3. `sections/*/activity_plan.json` 안에 `activity_type: "freeform_html"` 와 `html_content` 존재 확인
4. `render_manifest.json` 또는 최종 `.numbers` 파일 생성 확인
