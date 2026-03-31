# Manual Page Selection Workflow

## Goal

교과서 차시 경계 판정은 AI 자동 추론 대신 교사가 직접 확정한다.

시스템의 역할은 다음으로 제한한다.

1. 교과서 PDF를 보여 준다.
2. 교사가 차시를 만들고 페이지 범위를 지정하게 한다.
3. 지정된 범위를 기반으로 final config를 생성한다.
4. 이후 차시 분석, 활동 생성, Numbers 파일 생성을 자동으로 수행한다.

진도표는 필수 입력이 아니다.

## Core Decision

기존 source parsing 레이어의 핵심 목적은 차시를 나누고 페이지 범위를 잡는 것이었다.

이 결정을 교사가 직접 수행하면 아래 단계는 canonical path에서 제거할 수 있다.

- `schedule_parse_agent`
- `lesson_query_agent`
- `page_candidate_agent`
- `boundary_decision_agent`
- `boundary_validation_agent`
- `source_boundary_agent`

즉 새 기준의 canonical flow는 `teacher-confirmed pdf_pages config` 중심이다.
자동 차시 분류 레이어는 legacy/optional path로 남길 수 있다.

## New Workflow

1. 교과서 PDF 업로드 또는 선택
2. PDF 페이지 미리보기 그리드 표시
3. 교사가 차시를 직접 추가
4. 각 차시에 대해 이름을 입력
5. 각 차시에 대해 시작/끝 페이지를 직접 선택
6. 시스템이 `pdf_pages` 기반 final config를 저장
7. `lesson_analysis_agent`부터 downstream 파이프라인 실행

## User Experience

### Step 1. Textbook Select

- 교과서 PDF 선택
- 과목명, 학기, 단원명 입력 또는 선택

### Step 2. Lesson Builder

교사가 직접 차시 목록을 만든다.

필드:

- `sheet_name`
- `title`
- `badge`

예시:

- `2-3차시`
- `지구본의 특징 살펴보기`

### Step 3. Page Grid

교과서 PDF의 페이지 썸네일 그리드를 보여 준다.

현재 1차 구현은 썸네일 그리드 대신 차시별 `start_page` / `end_page` 직접 입력 방식으로 먼저 연결한다.
페이지 그리드는 다음 단계에서 추가한다.

필수 기능:

- 페이지 썸네일 목록
- 현재 선택 중인 차시 표시
- 시작 페이지 선택
- 끝 페이지 선택
- 선택 범위 하이라이트
- 현재 차시의 지정 범위 표시

권장 기능:

- 확대 미리보기
- 연속 페이지 드래그 선택
- 선택 해제
- overlap 경고

### Step 4. Review

차시별 매핑 결과를 표로 보여 준다.

예:

- `2-3차시: 110-118`
- `4차시: 119-119`
- `5차시: 120-123`

검토 항목:

- 빈 차시 없음
- 역방향 범위 없음
- 차시끼리 겹침 없음
- 필요 시 단원 도입 페이지 포함 여부 확인

### Step 5. Generate Config

검토가 끝나면 final config를 생성한다.

## Final Config Contract

새 기준 config는 `title_query`가 아니라 `pdf_pages`를 기준으로 한다.

```json
{
  "project_root": "/absolute/path/to/project",
  "pdf_path": "textbook/사회/[사회]6_1_교과서.pdf",
  "template_path": "빈 넘버스 파일.numbers",
  "output_file": "output/social_unit3_globe_world.numbers",
  "footer": "사회 6-1 · 3단원 · 지구본과 지도로 보는 세계",
  "sections": [
    {
      "sheet_name": "2-3차시",
      "card_file": "social_unit3_globe_world_2_3",
      "title": "지구본의 특징 살펴보기",
      "pdf_pages": [110, 111, 112, 113, 114, 115, 116, 117, 118],
      "badge": "2-3차시",
      "accent": ["#6366f1", "#818cf8"]
    },
    {
      "sheet_name": "4차시",
      "card_file": "social_unit3_globe_world_4",
      "title": "디지털 공간 영상 정보의 의미 알아보기",
      "pdf_pages": [119],
      "badge": "4차시",
      "accent": ["#4f46e5", "#7c3aed"]
    }
  ]
}
```

`pdf_range`를 UI 입력 형식으로 써도 되지만, 저장 시에는 `pdf_pages`로 정규화하는 편이 downstream에 더 단순하다.

## Backend Design

### 1. `GET /api/textbooks`

목적:

- 선택 가능한 교과서 PDF 목록 반환

### 2. `POST /api/pdf-preview`

입력:

- `pdf_path`

출력:

- `page_count`
- 페이지 이미지 또는 썸네일 경로 목록

### 3. `POST /api/validate-page-map`

입력:

- 차시 목록
- 각 차시의 `start_page`, `end_page`

출력:

- overlap 여부
- gap 여부
- reverse range 여부
- 빈 차시 여부

### 4. `POST /api/create-config-from-page-map`

입력:

- `subject`
- `pdf_path`
- `unit_title`
- `output_filename`
- `footer`
- 차시 목록
- page map

출력:

- 생성된 config 경로

## Frontend Design

필요한 새 UI 컴포넌트:

- `PdfPageGrid`
- `LessonEditor`
- `LessonPageMapper`
- `PageMapReview`

화면 상태:

1. 교과서 선택
2. 차시 목록 편집
3. 페이지 범위 선택
4. 검토 후 config 생성

## Orchestrator Changes

새 기준:

- section에 `pdf_pages`가 모두 있으면 source parsing stage를 스킵한다.

즉 다음 stage부터 바로 시작할 수 있다.

- `lesson_analysis_agent`
- `lesson_review_agent`
- `activity_plan_agent`
- `activity_review_agent`
- `html_card_agent`
- `capture_agent`
- `numbers_compose_agent`
- `verify_agent`

구체 규칙:

- 모든 section이 `pdf_pages`를 가지면 `schedule_parse_agent`부터 `source_validation_agent`까지 skip
- 일부만 `pdf_pages`가 있으면 혼합 모드는 당장은 허용하지 않는 편이 안전하다

## Validation Rules

수동 입력이어도 최소 검증은 반드시 필요하다.

필수 검증:

- `start_page <= end_page`
- 모든 차시에 페이지가 지정됨
- 차시 간 overlap 없음
- page number가 1 이상이고 총 페이지 수 이하

선택 검증:

- 단원 도입 페이지 포함 여부
- 마지막 차시 뒤 단원 정리 페이지 여부

## Benefits

- 가장 불안정한 차시 경계 추론을 제거
- 과목별 진도표 형식 문제 제거
- 교과서만 있으면 작업 가능
- 교사가 실제 수업 기준으로 차시를 나눌 수 있음
- downstream 파이프라인 품질 검증이 쉬워짐

## Costs

- 초기 사용자 입력 증가
- 완전 자동화는 아님
- PDF 썸네일/그리드 UI 구현 필요

## Recommended Implementation Order

1. PDF preview API 추가
2. 차시 편집 UI 추가
3. 페이지 범위 선택 UI 추가
4. `create-config-from-page-map` API 추가
5. orchestrator에서 `pdf_pages` config fast-path 추가

## Conclusion

이 구조는 현재 목표에 더 적합하다.

정확한 차시 페이지 분류를 AI가 끝까지 자동으로 맞추려 하기보다,
교사가 차시와 페이지 범위를 확정하고 AI는 그 이후 생성에 집중하게 만드는 것이
더 정확하고, 더 범용적이며, 실제 운영에도 적합하다.
