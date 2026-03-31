# Gemini CLI Link Plan

## 목적
- 기존 `교과서 분석 -> 차시 분류 -> 활동 계획 -> HTML 렌더 -> Numbers 삽입` 구조에 `Gemini CLI`를 붙인다.
- API SDK 대신 로컬 커맨드라인 도구를 사용해, 교과서 PDF와 진도표 이미지를 바탕으로 AI 보조 분석을 수행한다.
- 핵심 목표는 `차시 해석 정확도 보강`과 `차시별 활동 추천 품질 향상`이지, 기존 결정론 파이프라인을 대체하는 것이 아니다.

## 현재 기준선
- 기존 파이프라인은 제목 기반 차시 경계 추론, `lesson_analysis/activity_plan/render_manifest` JSON, HTML 캡처, Numbers 삽입 구조를 가진다.
- 현재도 자동 분석과 활동 초안 생성은 가능하지만, 규칙 기반 휴리스틱이 중심이라 교육적 품질과 표현 다양성에 한계가 있다.
- `TextBookInSkill`의 핵심 규칙은 유지한다.
  - 진도표 쪽수는 무시
  - 교과서 PDF를 먼저 분석
  - 차시는 `해당 제목이 처음 등장하는 페이지 ~ 다음 차시 제목 직전`으로 확정

## 병렬 브레인스토밍 요약

### 수업전문가 관점
- Gemini는 `핵심 질문`, `학습목표 후보`, `오개념`, `수준별 활동 초안` 제안까지 맡는 것이 적절하다.
- 차시명과 교과서 실제 내용 연결, 활동의 목표 적합성, 수준별 분화 타당성은 사람이 반드시 검토해야 한다.
- 교과서 근거 없는 활동 문장, 배경지식 과다 요구, 가치판단 과도 유도는 강한 실패 사례다.

### 개발자 관점
- Gemini CLI는 `AI planning sidecar`로 붙여야 한다.
- 페이지 경계, 텍스트 추출, Numbers 삽입 같은 정답성이 높은 단계는 기존 Python이 유지한다.
- Gemini 출력은 자유 텍스트가 아니라 엄격한 JSON으로 받고, schema 검증과 fallback을 강제해야 한다.

### 디자이너 관점
- Gemini는 디자인을 만들지 않는다. 디자인은 계속 [NumbersDesign.md](/Users/jonyeock/Desktop/Tool/NumbersAuto/NumbersDesign.md) 기반 템플릿 렌더러가 담당한다.
- AI는 활동 내용과 쓰기 영역 메타데이터만 제안하고, 화면 구조는 템플릿이 결정한다.
- 따라서 CLI 연동 이후에도 결과물의 시각 품질은 안정적으로 유지할 수 있다.

### 총괄 PM 관점
- v1 범위는 `Gemini로 차시 해석 보조 + 활동 추천 보조`까지다.
- `완전 무검토 자동화`와 `전 과목 범용화`는 v1 범위를 넘는다.
- 성공 기준은 `기존 textbook-only 흐름 무회귀`, `활동 초안 품질 향상`, `실패 시 안전한 fallback`이다.

## 최종 결정 사항

### 1. 아키텍처 원칙
- Gemini CLI는 기존 파이프라인을 대체하지 않고 `판단 보조 계층`으로 붙인다.
- 책임 분리는 명확해야 한다.
  - 기존 Python: PDF 추출, 제목 검색, 차시 경계 확정, schema 검증, HTML 렌더, Numbers 삽입
  - Gemini CLI: 의미 해석, 핵심 개념 정리, 오개념 후보, 활동 초안, 차시명 의미 보정
- 즉, `결정론적 단계`와 `생성형 단계`를 분리한다.
  - 결정론적 단계: `extract`, `match`, `validate`, `render`, `insert`, `verify`
  - 생성형 단계: `interpret`, `summarize`, `recommend`, `normalize candidate fields`

### 2. 차시 분류 원칙
- 차시 경계는 계속 기존 제목 기반 로직이 baseline을 만든다.
- Gemini는 다음 역할만 수행한다.
  - 진도표 차시명과 교과서 본문 제목 사이의 의미적 alias 제안
  - 애매한 제목에 대한 `boundary_notes` 제안
  - 차시 목표 요약
- Gemini가 페이지 범위를 직접 최종 결정하지는 않는다.

### 3. 활동 계획 원칙
- Gemini는 차시별로 `draft` 활동 초안을 생성한다.
- 활동 추천은 교과서 근거와 연결되어야 한다.
  - 각 활동은 `source_refs` 또는 `source_chunks`를 반드시 가진다.
  - 교과서 근거가 없는 활동은 폐기 대상이다.
- 출력은 계속 템플릿 enum 안으로만 들어온다.
  - `learning_note`
  - `see_think_wonder`
  - `worksheet`

### 4. 승인 게이트
- Gemini 산출물은 기본 상태가 `draft`다.
- 최소 검토 지점은 두 개다.
  - `lesson_analysis_ai -> lesson_analysis`
  - `activity_plan_ai -> activity_plan`
- 사람이 승인하지 않으면 기본적으로 Numbers 렌더에는 들어가지 않게 설계하는 것이 원칙이다.
- 단, 실험용 시제품 모드에서는 `draft` 렌더 허용 옵션을 둘 수 있다.

## 권장 데이터 흐름

### 입력
- `textbook.pdf`
- `progress_chart.png` 또는 `lesson schedule image`
- 기존 project config

### 중간 산출물
- `schedule_draft.json`
  - OCR 또는 기존 차시명 추출 결과
- `textbook_context.json`
  - 차시 후보별 추출 텍스트, 제목 검색 결과, 경계 후보
- `lesson_analysis_ai.json`
  - Gemini가 제안한 차시 해석 결과
- `lesson_analysis.json`
  - schema 검증과 사람 검토를 거친 확정본
- `activity_plan_ai.json`
  - Gemini가 제안한 활동 초안
- `activity_plan.json`
  - 검토/승인 후 렌더 가능한 확정본

### 최종 산출물
- `render_manifest.json`
- 최종 `.numbers`

## 권장 입출력 계약

### 1. preextract_local
- 목적:
  - Gemini에 넘길 문맥을 먼저 로컬에서 안정적으로 추출한다.
- 입력:
  - `config.json`
  - `textbook.pdf`
  - `progress_chart.png` 또는 기존 차시명 목록
- 출력:
  - `schedule_draft.json`
  - `textbook_context.json`
  - `pdf_text_chunks/<lesson>.txt`
- 원칙:
  - 바이너리 PDF 파싱 책임을 Gemini CLI에 넘기지 않는다.
  - 파일 존재 확인, OCR 보조, 텍스트 추출, 제목 검색 후보 계산까지는 로컬 Python이 담당한다.

### 2. Gemini 1차 출력: lesson_breakdown / lesson_analysis_ai
- 최소 필드:
  - `unit_title`
  - `sections[]`
  - `sheet_name`
  - `lesson_title`
  - `title_query`
  - `essential_question`
  - `learning_goals`
  - `key_concepts`
  - `misconceptions`
  - `confidence`
  - `notes`
  - `end_before_query_candidate`
- 주의:
  - 페이지 번호는 Gemini가 확정하지 않는다.
  - `title_query`는 로컬 검증 대상이다.

### 3. Gemini 2차 출력: activity_plan_ai
- 기존 [activity_plan.schema.json](/Users/jonyeock/Desktop/Tool/NumbersAuto/schemas/activity_plan.schema.json) shape를 최대한 재사용한다.
- 추가 권장 필드:
  - `layout_hint`
  - `writing_space_profile`
  - `expected_output`
  - `constraints`
- 목적:
  - 템플릿 선택과 쓰기 공간 배치를 렌더러가 바로 결정할 수 있게 한다.

## 권장 CLI 구조

### 단일 진입점
- 새 래퍼 명령을 둔다.

```bash
python3 scripts/run_gemini_cli_pipeline.py \
  --config configs/<unit>.json \
  --pdf "[사회]6_1_교과서.pdf" \
  --chart "진도표.png" \
  --gemini-model <model> \
  --gemini-bin gemini \
  --keep-artifacts
```

### 내부 단계
1. `extract_textbook_context`
2. `draft_schedule_from_chart`
3. `call_gemini_for_lesson_analysis`
4. `normalize_and_validate_lesson_analysis`
5. `call_gemini_for_activity_plan`
6. `normalize_and_validate_activity_plan`
7. `render_html_and_capture`
8. `insert_into_numbers`
9. `verify_output`

### 실행 모드
- `--dry-run`
  - Gemini 호출과 JSON 정규화까지만 수행
- `--textbook-only-fallback`
  - Gemini 실패 시 기존 textbook-only 결과를 강제로 생성
- `--include-status draft reviewed approved`
  - 시제품 모드에서 `draft` 활동까지 렌더
- `--keep-artifacts`
  - prompt, raw response, normalized json, validation report 보존

## 프롬프트 전략

### 원칙
- PDF 전체를 통째로 넣지 않는다.
- 기존 Python이 먼저 텍스트를 추출하고, Gemini에는 구조화된 문맥만 넘긴다.
- 차시별 독립 호출을 기본으로 한다. 한 차시 실패가 전체 단원을 막지 않게 해야 한다.

### Gemini에 넘길 문맥
- 차시명
- 교과서에서 찾은 시작/종료 페이지 후보
- 해당 범위에서 추출한 텍스트
- 핵심 이미지/표/활동 설명의 OCR 텍스트
- 진도표에서 읽은 차시명 목록

### 출력 형식
- 자유 서술 금지
- JSON only
- 기존 schema와 호환되도록 field 제한

### 프롬프트 파일 구조
- `prompts/gemini/system_analyze.md`
- `prompts/gemini/user_analyze.md`
- `prompts/gemini/system_plan.md`
- `prompts/gemini/user_plan.md`
- `prompts/gemini/json_schema_lesson_analysis.json`
- `prompts/gemini/json_schema_activity_plan.json`

### 고정 규칙 문구
- 진도표 쪽수는 전부 무시
- 교과서 PDF를 먼저 분석
- 차시는 제목 기준으로만 분리
- schema 외 필드 금지
- 모르면 `null` 또는 `notes`에 남김
- 출력은 반드시 `JSON only`

## 검증과 재시도

### 로컬 검증 항목
- JSON schema validation
- `title_query`가 실제 PDF 본문 텍스트에 매칭되는지 확인
- `lesson_id`와 실제 시트명이 대응되는지 확인
- `activity_type`이 허용 enum 안에 있는지 확인
- `source_refs` 또는 `source_chunks`가 존재하는지 확인

### 재시도 원칙
- 같은 프롬프트 무한 반복은 금지
- 로컬 검증 실패 이유를 붙여 한 번 더 수정 요청
- 예:
  - `title_query not found in PDF text`
  - `activity_type is outside allowed enum`
  - `lesson_id does not match any section`

### fallback 정책
- 1차 실패:
  - 동일 단계 재호출
- 2차 실패:
  - 더 좁은 문맥으로 재호출
- 3차 실패:
  - 기존 규칙 기반 분석으로 fallback
- 최종 실패:
  - `partial-with-warning` 또는 `textbook-only`

## 실패 처리 정책
- Gemini CLI 호출 실패 시:
  - 1차: 재시도
  - 2차: 더 좁은 문맥으로 재호출
  - 3차: 기존 규칙 기반 분석으로 fallback
- malformed JSON이면:
  - schema repair pass
  - 실패 시 해당 차시만 `draft_failed`로 남기고 다음 차시 계속 진행
- 차시 해석이 애매하면:
  - `ambiguous` 상태로 보류
  - 자동 확정하지 않음

## 로그와 산출물 보존
- 디버깅을 위해 다음을 같이 저장한다.
  - prompt input
  - raw Gemini response
  - normalized JSON
  - validation result
- 권장 위치:

```text
artifacts/gemini/<unit>/<timestamp>/
```

## 보안 및 운영 주의
- 교과서 텍스트와 진도표 이미지가 외부 모델로 전달될 수 있다는 점을 문서에 명시해야 한다.
- 학교 자료 반출 허용 범위를 먼저 정리해야 한다.
- CLI 환경 전제도 문서화해야 한다.
  - `gemini` 실행 가능 여부
  - 로그인 또는 인증 상태
  - 지원 모델명

### 사전 점검 항목
- `gemini` 바이너리 설치 여부
- 인증 상태
- Numbers 앱 설치 여부
- Playwright 실행 가능 여부
- Vision OCR 사용 가능 여부
- 작업 디렉토리 쓰기 권한

### 권장 보조 스크립트
- `scripts/check_local_requirements.py`
  - Gemini CLI, Numbers, Playwright, OCR, Python 의존성 사전 점검
- `scripts/run_gemini_cli_pipeline.py`
  - 전체 래퍼
- `scripts/normalize_gemini_json.py`
  - malformed JSON 복구/정규화

## v1 범위
- 지원 입력:
  - 텍스트 제목이 비교적 명확한 교과서 PDF
  - 차시명 위주 진도표 이미지
- 지원 출력:
  - 차시 해석 보조
  - 차시별 활동 1~3개 초안
  - 기존 3개 템플릿으로 렌더 가능한 JSON
- 비포함:
  - 완전 자동 승인
  - 과목 무제한 범용화
  - 자유 레이아웃 생성
  - 교사용 편집 UI
  - 실시간 대화형 수정
  - 대규모 병렬 배치 운영

## 단계별 구현 로드맵

### M1. CLI 래퍼 도입
- Gemini CLI 실행 래퍼 추가
- prompt/result 저장 구조 추가
- dry-run 모드 추가

### M2. Lesson Analysis 보강
- 기존 차시 경계 추론 결과를 Gemini에 입력
- `lesson_analysis_ai.json` 생성
- schema 검증 + 사람이 수정 가능한 normalized output 생성

### M3. Activity Plan 보강
- 차시별 활동 추천을 Gemini로 생성
- 기존 enum/template 안으로 정규화
- `draft` 상태 기본화

### M4. 통합 및 검증
- 기존 `generate_numbers_with_auto_activities.py`와 연결
- `--use-gemini-cli` 또는 별도 진입점으로 통합
- fallback과 검증 로그 정비

### M5. 운영 안정화
- 샘플 교과서 세트로 golden regression 구축
- prompt/model 버전 기록
- 실패 케이스 축적
- 사람이 수정한 결과를 다음 프롬프트 개선 입력으로 재활용

## 성공 기준
- Gemini를 꺼도 기존 파이프라인은 그대로 동작한다.
- Gemini를 켰을 때 차시 해석의 수정량과 활동 초안 수작업 수정량이 줄어든다.
- 실패 시에도 최소 `textbook-only` 결과는 안전하게 생성된다.
- 렌더 결과는 계속 [NumbersDesign.md](/Users/jonyeock/Desktop/Tool/NumbersAuto/NumbersDesign.md) 템플릿 규칙 안에서만 나온다.
- 모델 버전, 프롬프트 버전, raw response, normalized output이 모두 아티팩트로 남는다.

## MVP 정의
- 가장 먼저 구현할 MVP는 `Gemini CLI 기반 analyze-textbook + recommend-activities`다.
- 범위:
  - 교과서 PDF 1권
  - 차시표 이미지 1장
  - 차시 해석 보조 JSON
  - 활동 추천 JSON
  - 기존 3개 템플릿으로 Numbers 합성
- 완료 정의:
  - 사람 검토 10분 이내
  - 1개 단원 dry-run 성공
  - 1개 단원 full pipeline 성공

## 남은 오픈 질문
- Gemini CLI가 로컬 파일 직접 참조를 어느 수준까지 안정적으로 지원하는지
- 차시표 OCR 초안과 Gemini 해석 결과가 충돌할 때 우선순위를 어디에 둘지
- `lesson_analysis_ai`와 기존 `lesson_analysis`를 분리 저장할지, patch 형태로 저장할지
- 실험 단계에서 `draft` 활동을 기본 렌더할지, 명시적 옵션으로만 허용할지

## 다음 액션
- 1. `Gemini CLI 호출 방식`과 `입출력 포맷`을 실제 명령 기준으로 고정
- 2. `lesson_analysis_ai`와 `activity_plan_ai`용 별도 schema 초안 작성
- 3. `run_gemini_cli_pipeline.py` 최소 골격 구현
- 4. 한 단원으로 dry-run 검증
