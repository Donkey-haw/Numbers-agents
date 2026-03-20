# Progress

## 2026-03-19

### 현재까지 정리한 작업
- 현재 디렉토리 구조, `PROCESS.md`, 기존 예시 Numbers 파일, HTML 카드, AppleScript 자동화 스크립트를 분석했다.
- Numbers 교과서 배치 방식은 `PDF 페이지 추출 -> HTML 카드 생성 -> Playwright 스크린샷 -> AppleScript로 Numbers 시트 삽입` 파이프라인으로 정리했다.
- 원본 [빈 넘버스 파일.numbers](/Users/jonyeock/Desktop/Tool/NumbersAuto/빈%20넘버스%20파일.numbers)는 수정하지 않고 복제본으로 작업하는 흐름을 확정했다.

### 2단원 샘플 생성 1차 시도
- 2단원 `민주화와 산업화로 달라진 생활 문화`를 임의 선택해 시트별 Numbers 파일을 생성했다.
- 자동화 스크립트 [scripts/generate_unit2_cards.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/generate_unit2_cards.py) 를 추가해 PDF 추출, HTML 생성, 카드 PNG 캡처를 자동화했다.
- 자동화 스크립트 [scripts/build_unit2_numbers.scpt](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/build_unit2_numbers.scpt) 를 추가해 Numbers 시트 생성과 카드 삽입을 자동화했다.
- 산출물 [output/6-1-2. 민주화와 산업화로 달라진 생활 문화.numbers](/Users/jonyeock/Desktop/Tool/NumbersAuto/output/6-1-2.%20민주화와%20산업화로%20달라진%20생활%20문화.numbers) 을 생성했다.

### 2단원 차시 재구성
- 사용자 제공 [진도표.png](/Users/jonyeock/Desktop/Tool/NumbersAuto/진도표.png) 를 기준으로 차시 분할 기준을 교정했다.
- 2단원 시트 구성을 `7차시`, `8-9차시`, `10차시`, `11차시`, `12-13차시`로 재설계했다.
- 교과서 내부 인쇄 쪽수 기준으로 매핑을 수정했다.
  - `7차시`: 사회 26~29쪽
  - `8-9차시`: 사회 30~35쪽
  - `10차시`: 사회 36~37쪽
  - `11차시`: 사회 38~41쪽
  - `12-13차시`: 사회 42~47쪽
- 카드 라벨도 PDF 파일 페이지 번호가 아니라 `사회 xx쪽` 기준으로 수정했다.
- Numbers 파일 재생성 후 시트명을 다시 확인했고, 최종 시트 구성이 의도대로 들어간 것을 검증했다.

### 생성 및 검증 결과
- 최종 파일: [output/6-1-2. 민주화와 산업화로 달라진 생활 문화.numbers](/Users/jonyeock/Desktop/Tool/NumbersAuto/output/6-1-2.%20민주화와%20산업화로%20달라진%20생활%20문화.numbers)
- 생성된 시트:
  - `7차시`
  - `8-9차시`
  - `10차시`
  - `11차시`
  - `12-13차시`
- `PROCESS.md`의 cleanup 정책에 맞춰 작업 중 생성한 `assets/pages`, `assets/cards` 임시 이미지들은 정리했다.

### Skill화 진행
- 차시 구성을 코드 상수에서 설정 파일로 분리했다.
- 설정 파일 [configs/unit2.json](/Users/jonyeock/Desktop/Tool/NumbersAuto/configs/unit2.json) 을 추가했다.
- 범용 실행기 [scripts/generate_numbers_lesson.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/generate_numbers_lesson.py) 를 추가했다.
  - 템플릿 복제
  - PDF 페이지 추출
  - HTML 카드 생성
  - Playwright 카드 캡처
  - AppleScript 기반 Numbers 삽입
  - 시트명 검증
  - 임시 에셋 cleanup
- 새 범용 실행기로 `configs/unit2.json`을 사용해 실제 `.numbers` 파일 재생성을 완료했고, 시트명이 기대값과 일치하는 것을 재검증했다.
- Codex Skill 초안 [TextBookInSkill/SKILL.md](/Users/jonyeock/.codex/skills/TextBookInSkill/SKILL.md) 를 생성했다.
- `scripts/` 루트를 정리해 현재 표준 진입점만 남기고, 실험용/단원 전용 스크립트는 [scripts/legacy/README.md](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/legacy/README.md) 기준으로 `scripts/legacy/`로 이동했다.
- [scripts/README.md](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/README.md) 에 현재 표준 실행 경로를 문서화했다.
- 기존 호출 호환성을 위해 [scripts/generate_unit2_cards.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/generate_unit2_cards.py) 는 범용 실행기를 호출하는 deprecated wrapper로 남겨 두었다.
- OCR 보조 스크립트 [scripts/ocr_progress_chart.swift](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/ocr_progress_chart.swift) 와 [scripts/draft_config_from_progress_chart.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/draft_config_from_progress_chart.py) 를 추가했다.
- `진도표.png`에서 2단원 범위만 추출해 [configs/unit2_draft_from_chart.json](/Users/jonyeock/Desktop/Tool/NumbersAuto/configs/unit2_draft_from_chart.json) 초안을 생성했다.
- 이 OCR 초안 config로 [output/6-1-2-ocr-draft.numbers](/Users/jonyeock/Desktop/Tool/NumbersAuto/output/6-1-2-ocr-draft.numbers) 생성까지 검증했고, 시트명이 기대값과 일치하는 것을 확인했다.
- 범용 생성기에서 `pdf_pages` 없는 title-only config를 지원하도록 수정했다.
- [configs/democracy_election_title_only.json](/Users/jonyeock/Desktop/Tool/NumbersAuto/configs/democracy_election_title_only.json) 로 `차시명 기반 페이지 추론` 방식을 검증했고, [output/6-1-2-1. 민주주의와 선거-title-only.numbers](/Users/jonyeock/Desktop/Tool/NumbersAuto/output/6-1-2-1.%20민주주의와%20선거-title-only.numbers) 생성 및 시트 검증을 통과했다.
- 기준을 더 엄격하게 바꿨다:
  - 진도표 쪽수는 전부 무시
  - 스킬 호출 시 교과서 PDF를 먼저 분석
  - 각 시트는 해당 차시명이 등장하는 페이지부터 다음 차시명 직전 페이지까지 포함
  - 마지막 차시는 `end_before_query` 또는 `unit_end_page`로 경계 설정
- [scripts/draft_config_from_progress_chart.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/draft_config_from_progress_chart.py) 도 쪽수 없는 title-only draft를 생성하도록 수정했다.
- `2단원 도입 + 민주주의와 선거` 묶음 생성용 설정 [configs/democracy_election_with_intro.json](/Users/jonyeock/Desktop/Tool/NumbersAuto/configs/democracy_election_with_intro.json) 을 추가했다.
- 이 설정으로 [output/6-1-2. 2단원 도입과 민주주의와 선거.numbers](/Users/jonyeock/Desktop/Tool/NumbersAuto/output/6-1-2.%202단원%20도입과%20민주주의와%20선거.numbers) 를 생성했고, 시트 `1차시, 2차시, 3차시, 4-5차시, 6-7차시` 를 검증했다.
- 활동 확장 구현의 다음 단계로 schema와 v1 템플릿 기준본을 추가했다.
  - [schemas/lesson_analysis.schema.json](/Users/jonyeock/Desktop/Tool/NumbersAuto/schemas/lesson_analysis.schema.json)
  - [schemas/activity_plan.schema.json](/Users/jonyeock/Desktop/Tool/NumbersAuto/schemas/activity_plan.schema.json)
  - [schemas/render_manifest.schema.json](/Users/jonyeock/Desktop/Tool/NumbersAuto/schemas/render_manifest.schema.json)
  - [examples/lesson_analysis.sample.json](/Users/jonyeock/Desktop/Tool/NumbersAuto/examples/lesson_analysis.sample.json)
  - [templates/v1/learning_note.html](/Users/jonyeock/Desktop/Tool/NumbersAuto/templates/v1/learning_note.html)
  - [templates/v1/see_think_wonder.html](/Users/jonyeock/Desktop/Tool/NumbersAuto/templates/v1/see_think_wonder.html)
  - [templates/v1/worksheet.html](/Users/jonyeock/Desktop/Tool/NumbersAuto/templates/v1/worksheet.html)
- `activity_plan.json`을 받아 v1 템플릿 3종으로 HTML을 생성하는 결정론적 renderer [scripts/render_activity_html.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/render_activity_html.py) 를 추가했다.
- renderer 검증용 샘플 [examples/activity_plan.sample.json](/Users/jonyeock/Desktop/Tool/NumbersAuto/examples/activity_plan.sample.json) 도 추가했다.
- 샘플 plan으로 `learning_note`, `see_think_wonder`, `worksheet` HTML 3개가 정상 렌더링되는 것을 임시 디렉토리에서 검증했다.
- `교과서 + 활동지` 통합용 오케스트레이터 [scripts/generate_numbers_with_activities.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/generate_numbers_with_activities.py) 를 추가했다.
- 이 스크립트는 다음을 한 번에 처리한다.
  - 교과서 차시 범위 추론
  - 교과서 카드 렌더/캡처
  - activity_plan 기반 활동 HTML 렌더/캡처
  - render manifest 생성
  - 같은 시트 안에 교과서 카드와 활동 카드를 순서대로 Numbers에 삽입
- `document 1` 참조로 생기던 Numbers 앱 다중 문서 문제를 줄이기 위해, 생성/검증 AppleScript를 `open`이 반환한 문서를 직접 참조하도록 수정했다.
- [configs/democracy_election_with_intro.json](/Users/jonyeock/Desktop/Tool/NumbersAuto/configs/democracy_election_with_intro.json) + [examples/activity_plan.sample.json](/Users/jonyeock/Desktop/Tool/NumbersAuto/examples/activity_plan.sample.json) 조합으로 통합 생성 검증을 완료했다.
- 최종 산출물은 [output/6-1-2. 2단원 도입과 민주주의와 선거.numbers](/Users/jonyeock/Desktop/Tool/NumbersAuto/output/6-1-2.%202단원%20도입과%20민주주의와%20선거.numbers) 이며, 시트 `1차시, 2차시, 3차시, 4-5차시, 6-7차시` 를 다시 검증했다.
- 교과서 본문에서 차시별 핵심 정보를 추출하는 분석기 [scripts/generate_lesson_analysis.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/generate_lesson_analysis.py) 를 추가했다.
  - 차시별 `lesson_analysis.json` 생성
  - 핵심 개념, 오개념, 학습 덩어리, source page refs 초안 생성
- 차시 분석을 바탕으로 활동지 초안을 만드는 [scripts/generate_activity_plan.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/generate_activity_plan.py) 를 추가했다.
  - `learning_note`, `see_think_wonder`, `worksheet` 3종을 결정론적으로 생성
  - 출력 상태는 기본 `draft`
- [scripts/generate_numbers_with_activities.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/generate_numbers_with_activities.py) 는 이제 `--activity-plan` 반복 입력을 지원해 여러 차시의 활동 계획을 한 번에 합성할 수 있다.
- `config -> lesson_analysis -> activity_plan -> Numbers`를 한 번에 수행하는 오케스트레이터 [scripts/generate_numbers_with_auto_activities.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/generate_numbers_with_auto_activities.py) 를 추가했다.
- 자동 생성 활동은 검토 게이트를 유지하기 위해 `draft`로 생성하지만, 새 오케스트레이터는 기본적으로 `draft/reviewed/approved`를 모두 렌더해 시제품 제작까지 바로 가능하게 했다.
- [configs/democracy_election_with_intro.json](/Users/jonyeock/Desktop/Tool/NumbersAuto/configs/democracy_election_with_intro.json) 기준으로 자동 생성 오케스트레이터를 실제 실행해 최종 Numbers 재생성까지 검증했다.
- 자동 분석 품질도 보정했다.
  - 조사 제거를 통한 핵심 개념 정제
  - 질문형 차시명을 설명형 학습목표 문장으로 정규화
  - 예: `선거란 무엇일까요?` -> `선거의 핵심 내용을 설명할 수 있다.`

### 현재 남아 있는 한계
- `진도표.png`의 내용을 OCR 없이 사람이 읽어 `configs/unit2.json`에 반영했다.
- Numbers 삽입 위치와 크기는 현재 고정값이라 다양한 카드 높이에 대해 추가 튜닝 여지가 있다.
- 이전 실험용 HTML 파일이 `html/` 디렉토리에 일부 남아 있어 정리가 필요하다.
