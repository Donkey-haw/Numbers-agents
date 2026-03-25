# Scripts

## Current Entry Point
- [generate_numbers_lesson.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/generate_numbers_lesson.py)
- [parse_progress_chart_pdf.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/parse_progress_chart_pdf.py)
- [draft_config_from_progress_chart.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/draft_config_from_progress_chart.py)
- [generate_numbers_with_activities.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/generate_numbers_with_activities.py)
- [generate_numbers_with_auto_activities.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/generate_numbers_with_auto_activities.py)
- [run_gemini_cli_pipeline.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/run_gemini_cli_pipeline.py)
- [build_resource_index.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/build_resource_index.py)
- [build_unit_bundle.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/build_unit_bundle.py)
- [build_runtime_config.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/build_runtime_config.py)
- [generate_numbers_from_bundle.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/generate_numbers_from_bundle.py)

이 디렉토리의 표준 실행 경로는 위 스크립트들이다.

예시:

```bash
python3 scripts/generate_numbers_lesson.py --config configs/social_6_1_unit2_state_agencies.json
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

Gemini CLI를 붙여 차시 해석과 활동 추천을 AI 보조로 생성할 때:

```bash
python3 scripts/run_gemini_cli_pipeline.py \
  --config configs/social_6_1_unit2_state_agencies.json \
  --gemini-bin gemini \
  --max-workers 2 \
  --dry-run
```

진도표 PDF를 구조화 JSON으로 정리할 때:

```bash
python3 scripts/parse_progress_chart_pdf.py \
  --pdf "6학년 1학기 사회 진도표.pdf" \
  --output configs/social_6_1_progress_chart.json
```

교재 PDF 전체를 재사용 가능한 resource index로 저장할 때:

```bash
python3 scripts/build_resource_index.py \
  --pdf "[사회]6_1_교과서.pdf" \
  --resource-id social_textbook \
  --label "사회" \
  --kind textbook \
  --subject social \
  --output artifacts/scan/social_6_1/resources/social_textbook.resource_index.json
```

재사용된 resource index와 진도표에서 단원 bundle을 만들 때:

```bash
python3 scripts/build_unit_bundle.py \
  --chart configs/social_6_1_progress_chart.json \
  --unit-number 2 \
  --topic-title "민주주의와 선거" \
  --resource-index artifacts/scan/social_6_1/resources/social_textbook.resource_index.json \
  --primary-resource-id social_textbook \
  --existing-config configs/social_6_1_unit2_democracy_election.json \
  --output artifacts/scan/social_6_1/bundles/unit2_democracy_election.unit_bundle.json
```

unit bundle에서 실행용 config를 만들 때:

```bash
python3 scripts/build_runtime_config.py \
  --bundle artifacts/scan/social_6_1/bundles/unit2_democracy_election.unit_bundle.json \
  --project-root /absolute/path/to/project \
  --template-path "빈 넘버스 파일.numbers" \
  --output-file "output/unit2_democracy_election.generated.numbers" \
  --footer "사회 6-1 · 2단원 · 민주주의와 시민 참여" \
  --review-overrides artifacts/scan/social_6_1/reviews/unit2_democracy_election.overrides.json \
  --review-output artifacts/scan/social_6_1/reviews/unit2_democracy_election.review.json \
  --output artifacts/scan/social_6_1/generated_configs/unit2_democracy_election.generated.json
```

bundle에서 바로 Numbers를 만들 때:

```bash
python3 scripts/generate_numbers_from_bundle.py \
  --bundle artifacts/scan/social_6_1/bundles/unit2_democracy_election.unit_bundle.json \
  --project-root /absolute/path/to/project \
  --template-path "빈 넘버스 파일.numbers" \
  --output-file "output/unit2_democracy_election.generated.numbers" \
  --footer "사회 6-1 · 2단원 · 민주주의와 시민 참여" \
  --review-overrides artifacts/scan/social_6_1/reviews/unit2_democracy_election.overrides.json \
  --review-output artifacts/scan/social_6_1/reviews/unit2_democracy_election.review.json
```

진도표 이미지에서 config 초안을 만들 때:

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
- 단원 전용 또는 실험용 스크립트는 `scripts/legacy/`로 이동했다.
- 기존 실험용 config는 [configs/legacy](/Users/jonyeock/Desktop/Tool/NumbersAuto/configs/legacy) 로 이동했고, 현재 표준 config는 `configs/social_6_1_*.json` 형식을 사용한다.
- 새 작업은 가능하면 진도표 PDF를 먼저 [configs/social_6_1_progress_chart.json](/Users/jonyeock/Desktop/Tool/NumbersAuto/configs/social_6_1_progress_chart.json) 으로 구조화한 뒤, 주제별 config를 추가하고 범용 실행기를 호출하는 방식으로 진행한다.
- 진도표의 쪽수는 사용하지 않는다. 차시명만 추출하고, 실제 페이지 범위는 교과서 PDF 본문 분석으로 결정한다.
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
- `build_runtime_config.py`는 기본적으로 `supplement` 중 `matched`만 실행용 config에 포함한다. `needs_review`와 `not_found`는 review report로 빠지며, 승인하려면 `--review-overrides`를 사용하거나 `--include-needs-review-supplements`/`--include-unmatched-supplements`를 명시한다.
