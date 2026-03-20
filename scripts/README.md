# Scripts

## Current Entry Point
- [generate_numbers_lesson.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/generate_numbers_lesson.py)
- [draft_config_from_progress_chart.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/draft_config_from_progress_chart.py)
- [generate_numbers_with_activities.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/generate_numbers_with_activities.py)
- [generate_numbers_with_auto_activities.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/generate_numbers_with_auto_activities.py)
- [run_gemini_cli_pipeline.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/run_gemini_cli_pipeline.py)

이 디렉토리의 표준 실행 경로는 위 스크립트들이다.

예시:

```bash
python3 scripts/generate_numbers_lesson.py --config configs/unit2.json
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
  --config configs/democracy_election_with_intro.json \
  --gemini-bin gemini \
  --dry-run
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
- 새 작업은 가능하면 `configs/*.json`을 추가하고 범용 실행기를 호출하는 방식으로 진행한다.
- 진도표의 쪽수는 사용하지 않는다. 차시명만 추출하고, 실제 페이지 범위는 교과서 PDF 본문 분석으로 결정한다.
- 자동 활동 생성 흐름은 `lesson_analysis -> activity_plan -> HTML render -> Numbers insert` 순서다.
- 자동 생성된 활동은 기본적으로 `draft` 상태이며, `generate_numbers_with_auto_activities.py`는 이 초안도 바로 렌더할 수 있게 설계했다.
- Gemini CLI 연동은 `로컬 preextract -> Gemini JSON -> 로컬 normalize/validate -> 기존 Numbers 합성` 구조다.
- Gemini 프롬프트는 [prompts/gemini/system_analyze.md](/Users/jonyeock/Desktop/Tool/NumbersAuto/prompts/gemini/system_analyze.md), [prompts/gemini/user_analyze.md](/Users/jonyeock/Desktop/Tool/NumbersAuto/prompts/gemini/user_analyze.md), [prompts/gemini/system_plan.md](/Users/jonyeock/Desktop/Tool/NumbersAuto/prompts/gemini/system_plan.md), [prompts/gemini/user_plan.md](/Users/jonyeock/Desktop/Tool/NumbersAuto/prompts/gemini/user_plan.md)에 분리했다.
