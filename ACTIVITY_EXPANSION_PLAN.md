# Activity Expansion Plan

## 목적
- 현재의 `교과서 페이지 -> HTML 카드 -> 스크린샷 -> Numbers 삽입` 파이프라인을 확장해, 교과서 내용에 맞는 활동지까지 자동 생성한다.
- 결과물은 단순 교과서 시트가 아니라 `교과서 이해 + 수준별 활동 + 학생 필기 공간 + 교사 확인 포인트`를 포함한 수업용 Numbers 파일이어야 한다.
- 활동 HTML은 반드시 [NumbersDesign.md](/Users/jonyeock/Desktop/Tool/NumbersAuto/NumbersDesign.md)의 디자인 원칙을 따른다.

## 브레인스토밍 참가 역할
- 수업전문가: 활동의 교육적 구조, 수준별 분화, 교사 체크포인트 정의
- 개발자: 아키텍처, 데이터 계약, 검증, 단계 분리
- 디자이너: 템플릿 계열, 입력 영역, iPad/Pencil 주석 UX
- 총괄 PM: 범위, 단계, 성공 기준, 보류 항목

## 공통 합의
- 교과서 분석은 항상 최상위 단계다.
- 활동 생성은 교과서 분석 위에 올라가는 오버레이이며, 교과서 분량과 구조가 기준이다.
- 생성형 판단은 활동 제안/내용 초안에만 쓰고, PDF 분석/페이지 매핑/HTML 렌더/스크린샷/Numbers 삽입은 결정론적으로 유지한다.
- 자유 HTML 생성은 금지하고, `NumbersDesign.md`에 맞춘 템플릿 기반 렌더링만 허용한다.
- v1에서는 좁은 범위의 활동 유형만 지원하고, 사람 검토 단계를 반드시 둔다.

## 최종 결정 사항

### 1. 파이프라인 구조
- 새 표준 파이프라인은 아래 6단계다.
  - `analyze_textbook`
  - `plan_activities`
  - `render_activity_html`
  - `capture_activity_images`
  - `insert_into_numbers`
  - `verify_output`
- 교과서 카드와 활동 카드는 같은 파이프라인 안의 동등한 산출물이다.
- AppleScript는 얇게 유지하고, 시트 생성/이미지 삽입/기본 검증만 담당한다.

### 2. 데이터 계약
- 중간 산출물은 JSON으로 분리한다.
- 최소 4개 아티팩트를 둔다.
  - `lesson_analysis.json`
  - `activity_plan.json`
  - `render_manifest.json`
  - 최종 프로젝트 config
- 모든 JSON에는 `schema_version`, `generated_at`를 넣는다.
- 각 활동은 반드시 지원되는 activity type enum만 사용할 수 있다.

### 3. 활동 설계 원칙
- 한 차시의 흐름은 `입력 -> 사고 -> 연습 -> 성찰 -> 교사 확인` 구조를 기본값으로 둔다.
- 수준 분화는 `core`, `on-level`, `extension` 3단계로 제한한다.
- 수준 차이는 장식이 아니라 다음 3가지로만 낸다.
  - 프롬프트 수
  - 문장틀/예시 제공량
  - 작성 영역의 개방성
- 활동 개수는 차시 목적을 덮지 않도록 제한한다.

### 4. 디자인 시스템 결정
- 모든 활동은 `배지 + 컨테이너 + 지시문/라벨 + 학생 입력 영역` 공통 골격을 갖는다.
- 학생 입력 영역은 항상 `2px solid #333` 이상의 진한 테두리를 사용한다.
- 배지 색은 활동 유형 기준으로 고정하고, 차시별로 임의 확장하지 않는다.
- iPad/Pencil 주석을 전제로 다음 원칙을 강제한다.
  - 큰 입력 영역
  - 충분한 패딩
  - 작은 라벨 금지
  - 색상만으로 정보 전달 금지

### 5. v1 범위
- v1에서 우선 구현할 활동 템플릿은 3개로 제한한다.
  - `Learning Note`
  - `See-Think-Wonder`
  - `Worksheet`
- 이후 확장 후보:
  - `Frayer Model`
  - `Spectrum / Sorting`
  - `Reference + Response`

### 6. 사람 검토 정책
- 자동 생성 결과를 바로 HTML로 넘기지 않는다.
- 최소 승인 게이트는 2개다.
  - `lesson_analysis` 검토
  - `activity_plan` 검토
- 검토 포인트:
  - 교과서 정합성
  - 난이도 적절성
  - 잘못된 사실/허술한 활동 여부
  - 활동이 실제 수업에서 쓸 만한지

### 7. 실패 처리 정책
- 활동 생성이 깨져도 전체 산출물을 망가뜨리지 않는다.
- 기본 fallback은 `textbook-only` 또는 `partial-with-warning`이다.
- 조용히 잘못된 결과를 내는 것은 금지한다.

## 권장 아키텍처

### 오케스트레이터
- 기존 [scripts/generate_numbers_lesson.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/generate_numbers_lesson.py)를 장기적으로 stage 기반 오케스트레이터로 리팩터링한다.

### 모듈 분리
- `analysis/`
  - 교과서 제목 탐지
  - 차시 경계 확정
  - 핵심 개념/어휘/오개념 추출
- `planning/`
  - 활동 초안 생성
  - 수준별 분기
  - 교사 체크포인트 생성
- `templates/`
  - NumbersDesign 기반 템플릿 컴포넌트
  - 활동 유형별 렌더러
- `render/`
  - HTML 생성
  - Playwright 캡처
- `compose/`
  - Numbers 삽입
  - 시트 순서/위치/수량 검증

## 권장 메타데이터

### lesson_analysis
- `lesson_id`
- `sheet_name`
- `lesson_title`
- `pdf_pages`
- `essential_question`
- `learning_goals`
- `key_concepts`
- `vocabulary`
- `misconceptions`
- `content_chunks`
- `source_page_refs`
- `analysis_confidence`

### activity_plan
- `activity_id`
- `lesson_id`
- `activity_type`
- `level`
- `learning_goal`
- `prompt_text`
- `source_refs`
- `layout_template`
- `student_writing_zones`
- `teacher_notes`
- `estimated_minutes`
- `review_status`

### render_manifest
- `asset_type`
- `asset_id`
- `source_json`
- `html_path`
- `image_path`
- `sheet_name`
- `insert_order`
- `dimensions`

## 템플릿 계열
- `Learning Note`
  - 줄노트, 요약, 질문, 핵심 어휘
- `See-Think-Wonder`
  - 3분할 관찰/해석/질문
- `Worksheet`
  - 번호형 문항, 단답형 줄, 서술형 박스
- `Reference + Response`
  - 자료 제시 후 반응 작성
- `Frayer / Concept Builder`
  - 개념 정의와 예시/비예시
- `Spectrum / Sorting`
  - 의견 배치, 분류, 토론 준비

## 우선 구현 로드맵

### M1. 구조 리팩터링
- 기존 스크립트를 stage 기반으로 분리
- JSON schema 추가
- textbook-only 기능 회귀 없음 보장

### M2. 교과서 분석 아티팩트
- 차시 경계 확정
- `lesson_analysis.json` 출력
- 경계 검증 리포트 생성

### M3. 활동 템플릿 3종
- `Learning Note`
- `See-Think-Wonder`
- `Worksheet`
- NumbersDesign 토큰/레이아웃 반영

### M4. 활동 계획과 승인 게이트
- `activity_plan.json` 생성
- 검토/승인용 상태 필드 추가
- approved 데이터만 렌더

### M5. Numbers 합성 통합
- 한 manifest에서 교과서 카드와 활동 카드를 같이 삽입
- 시트 단위 정렬 규칙 확정

### M6. 검증과 회귀 체계
- 템플릿 golden image
- manifest 검증
- Numbers 시트/이미지 수 검증
- 샘플 단원 회귀 테스트

## v1 성공 기준
- 파일 생성 성공률: 필수 시트 100%
- 차시 경계 정확도: 시범 단원에서 검토 후 100%
- 지원 템플릿 3종의 스크린샷 안정성 확보
- 기존 textbook-only 워크플로우에 회귀 없음
- 교사 검토 후 “실사용 가능” 판단을 받는 활동지 비율이 충분히 높을 것

## 보류 항목
- 교사용 편집 UI
- 자동 교육학 품질 점수
- 비-넘버스 출력 포맷
- 과목 전면 확장
- 템플릿 무제한 확장
- 완전 무검토 자동화

## 남은 결정 포인트
- 활동을 같은 시트에 쌓을지, 차시별 활동 전용 시트로 분리할지
- 수준별 활동을 한 시트에 같이 둘지, 별도 시트로 둘지
- 교사 확인 노트를 학생 시트에 노출할지 메타데이터로만 둘지
- 자동 생성된 활동의 승인 방식과 저장 위치를 어떻게 표준화할지

## 권장 다음 액션
- 1. `lesson_analysis.json` 스키마를 먼저 확정
- 2. `Learning Note`, `See-Think-Wonder`, `Worksheet` 3종의 HTML 템플릿 초안 제작
- 3. 한 개 차시에 대해 `교과서 + 활동 1종`만 붙는 최소 end-to-end 샘플 구현
- 4. 그 결과를 바탕으로 same-sheet vs separate-sheet 결정을 확정
