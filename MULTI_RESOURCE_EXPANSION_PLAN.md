# Multi-Resource Expansion Plan

## 목적
- 현재의 단일 교과서 중심 Numbers 생성 파이프라인을 확장해, 여러 교재를 함께 사용하는 단원을 범용적으로 지원한다.
- 최종 목표는 과목 종류와 무관하게 `교과서 PDF + 진도표 + 보조 교재 PDF`만 있으면 원하는 단원을 Numbers로 생성할 수 있게 하는 것이다.

## 배경
- 현재 표준 config는 `pdf_path` 하나를 전제로 한다.
- 현재 차시 경계 추론은 단일 PDF에서만 수행된다.
- 현재 manifest는 `textbook_card`, `activity_sheet`만 지원한다.
- 현재 Numbers 배치는 자산을 좌에서 우로 한 줄에 순서대로 삽입하는 단순 모델이다.

즉, 현재 구조는 `사회`, `수학`, `과학`처럼 주교재 1권만 있는 흐름에는 맞지만,
`사회 + 사회과부도`, `수학 + 수학익힘`, `과학 + 실험관찰`처럼 여러 교재를 함께 쓰는 차시를 직접 표현하지 못한다.

## 활동 규칙 기준 해석
[ACTIVITY_RULE.md](/Users/jonyeock/Desktop/Tool/NumbersAuto/ACTIVITY_RULE.md) 기준으로 한 차시 시트는 아래 객체로 구성된다.

### 수업 전
- 교과서
- 추가자료

### 수업 중
- 학습 노트
- 활동 영역

### 수업 후
- 참고 자료
- 학습지
- AI 코스웨어 연계 영역

핵심 해석:
- `추가자료`는 선택적 장식이 아니라 정식 객체다.
- `추가자료`는 주교과서 뒤 또는 하단에 배치되어야 한다.
- 교과서 객체에는 해당 주제의 `주제 도입` 페이지가 항상 포함되어야 한다.
- `주제 도입`이 별도 차시가 아니면 첫 본차시 교과서 카드가 `주제 도입 + 본문 시작`을 함께 담아야 한다.
- 활동 생성과 차시 해석의 기본 근거는 주교과서로 유지한다.
- 보조교재는 우선 Numbers 배치용 resource로 다루고, Gemini 입력 확장은 필요할 때만 진행한다.
- 다교재 단원 지원은 단순 PDF 추가가 아니라, Numbers 객체 모델 자체를 확장하는 일이다.

## 현재 제약

### 1. config 제약
- 전역 `pdf_path` 하나만 받는다.
- 한 section은 암묵적으로 한 교과서만 가진다.

### 2. 분석 제약
- 차시 경계 추론은 한 문서 안에서만 수행된다.
- 추가자료 PDF는 분석 대상이 아니다.

### 3. 렌더 제약
- 한 section당 교과서 카드 1개만 렌더한다.
- 추가자료 카드 개념이 없다.

### 4. 합성 제약
- manifest가 자산 종류를 2개만 표현한다.
- Numbers 배치는 가로 한 줄 기준이라 상하 배치를 표현하기 어렵다.

## 확장 원칙

### 1. 주교재와 보조교재를 모두 1급 개체로 다룬다
- 모든 PDF는 `resource`로 선언한다.
- 차시별로 어떤 resource를 쓰는지 명시한다.

### 2. 교재별 분석은 독립적으로 수행한다
- 각 PDF는 자체 `title_query`, `search_start_page`, `end_before_query` 규칙을 가질 수 있다.
- 여러 PDF를 한 번에 섞어서 페이지 경계를 찾지 않는다.

### 3. 차시는 하나지만 source는 여러 개일 수 있다
- 한 `sheet_name` 아래에 `main textbook`, `supplement`, `reference`가 함께 들어갈 수 있다.

### 4. 배치는 역할 기반으로 한다
- 단순 삽입 순서가 아니라 `stage`와 `placement role`을 기준으로 좌표를 잡는다.

## 목표 데이터 모델

### 전역 config 초안
```json
{
  "project_root": "/absolute/path/to/project",
  "template_path": "빈 넘버스 파일.numbers",
  "output_file": "output/result.numbers",
  "subject": "social",
  "footer": "사회 6-1 · 2단원 · 민주주의와 시민 참여",
  "resources": [
    {
      "resource_id": "social_textbook",
      "label": "사회",
      "kind": "textbook",
      "pdf_path": "[사회]6_1_교과서.pdf"
    },
    {
      "resource_id": "atlas",
      "label": "사회과부도",
      "kind": "supplement",
      "pdf_path": "[사회]6_사회과 부도.pdf"
    }
  ],
  "sections": []
}
```

### section 초안
```json
{
  "sheet_name": "8차시",
  "lesson_id": "8차시",
  "title": "국가기관의 의미와 종류를 알아볼까요?",
  "badge": "8차시",
  "accent": ["#6366f1", "#818cf8"],
  "sources": [
    {
      "resource_id": "social_textbook",
      "role": "textbook",
      "title_query": "민주 국가는 어떻게 운영될까요?",
      "search_start_page": 70
    },
    {
      "resource_id": "atlas",
      "role": "supplement",
      "title_query": "국가기관",
      "search_start_page": 42,
      "optional": true
    }
  ]
}
```

## resource 종류

### `kind`
- `textbook`
- `supplement`
- `reference`
- `worksheet`
- `courseware`

### `role`
- `textbook`
- `supplement`
- `reference`

설명:
- `kind`는 교재의 본질
- `role`은 해당 차시에서의 쓰임새

예를 들어 `사회과부도`는 전역적으로는 `supplement`지만, 어떤 차시에서는 `reference` 역할로도 쓰일 수 있다.

## 차시 분석 구조 확장

### 현재
- `section -> pdf_pages`

### 목표
- `section -> source_ranges[]`

예시:
```json
{
  "sheet_name": "8차시",
  "source_ranges": [
    {
      "resource_id": "social_textbook",
      "role": "textbook",
      "pdf_pages": [72, 73]
    },
    {
      "resource_id": "atlas",
      "role": "supplement",
      "pdf_pages": [44, 45]
    }
  ]
}
```

## lesson_analysis 확장

### 현재 문제
- `source_page_refs`가 단순 페이지 배열이다.
- 어느 교재의 근거인지 구분할 수 없다.

### 목표
```json
{
  "source_refs": [
    {
      "resource_id": "social_textbook",
      "pages": [72, 73]
    },
    {
      "resource_id": "atlas",
      "pages": [44, 45]
    }
  ]
}
```

### Gemini 입력 방향
- Gemini에는 차시별 단일 텍스트가 아니라 `source_docs[]`를 준다.
- 각 source에 `resource_id`, `label`, `role`, `pages`, `extracted_text`를 포함한다.
- 활동 초안은 여러 교재 근거를 함께 참조할 수 있어야 한다.

## render_manifest 확장

### 현재 asset type
- `textbook_card`
- `activity_sheet`

### 추가 필요 asset type
- `supplement_card`
- `reference_card`
- `worksheet_card`
- `courseware_card`

### 추가 필요 필드
- `stage`
  - `before_class`
  - `during_class`
  - `after_class`
- `placement_role`
  - `main`
  - `below_main`
  - `right_of_main`
  - `after_activity`
- `resource_id`
- `group_id`

## Numbers 배치 모델

### v1 배치 규칙
- `before_class`:
  - `textbook_card`는 좌상단
  - `supplement_card`는 주교과서 하단 또는 우측
- `during_class`:
  - 학습 노트, 활동 영역은 중간
- `after_class`:
  - 참고 자료, 학습지, AI 연계는 우측

### v1에서 권장하는 단순 규칙
- 상단 행: 주교과서
- 하단 행: 추가자료
- 다음 가로 구간: 학습 노트, 활동
- 마지막 구간: 참고 자료, 학습지, AI

이 방식이면 [ACTIVITY_RULE.md](/Users/jonyeock/Desktop/Tool/NumbersAuto/ACTIVITY_RULE.md)의 객체 배치 규칙과 잘 맞고, AppleScript도 복잡해지지 않는다.

## 과목별 적용 예시

### 수학 + 수학익힘
- `textbook`: 개념 도입
- `supplement`: 연습, 적용
- 기본 정책:
  - 수학 교과서 상단
  - 수학익힘 하단
  - 활동/노트는 그 오른쪽

### 사회 + 사회과부도
- `textbook`: 핵심 본문
- `supplement`: 지도, 통계, 참고 자료
- 기본 정책:
  - 사회 상단
  - 사회과부도 하단
  - 필요 시 `reference_card`로도 분리 가능

### 과학 + 실험관찰
- `textbook`: 개념 설명
- `supplement`: 실험 절차, 기록
- 기본 정책:
  - 과학 교과서 상단
  - 실험관찰 하단
  - 활동지/관찰 기록 카드는 옆에 배치

## 구현 단계

### M1. config 스키마 확장
- `resources[]` 추가
- `section.sources[]` 추가
- 기존 `pdf_path` 단일 구조는 backward compatibility로 유지

### M2. 분석 계층 분리
- resource별 문서 열기
- source별 `title_query -> pdf_pages` 추론
- 결과를 `section["source_ranges"]`에 기록

### M3. 렌더 계층 분리
- `textbook_card` 렌더러
- `supplement_card` 렌더러
- 이후 `reference_card` 추가

### M4. manifest 확장
- asset type, stage, placement role 추가
- layout metadata 기반 검증 추가

### M5. Numbers 배치 엔진 확장
- 단순 `currentX` 증가 모델 탈피
- stage/lane 기반 좌표 시스템 도입

### M6. lesson_analysis / activity_plan 확장
- `source_refs`를 다교재 구조로 전환
- Gemini 입력에 여러 source 포함

## 권장 구현 순서
1. `사회 + 사회과부도` 샘플 config 하나를 새 구조로 만든다.
2. `generate_numbers_lesson.py`에서 단일 `pdf_path`와 `resources[]`를 모두 받게 만든다.
3. section당 `sources[]` 기반으로 여러 PDF 범위를 추론한다.
4. `supplement_card`를 같은 시트에 추가 삽입한다.
5. 그다음에 `lesson_analysis`, `activity_plan`을 다교재형으로 확장한다.

## 다음 단계

### 바로 이어서 할 일
- `config` 스키마 초안 구현
- `사회 + 사회과부도` 샘플 config 작성
- `generate_numbers_lesson.py`의 로더와 페이지 추론 함수에 `resources[]` 지원 추가

### 이번 단계에서 보류할 것
- 과목별 자동 placement 최적화
- AI 코스웨어 전용 카드
- 답안지/학습지 전용 별도 레이아웃 엔진
- 자유 생성 HTML 단계의 다교재 최적화

## 성공 기준
- 하나의 차시에 2개 이상의 PDF에서 페이지를 추출할 수 있다.
- 같은 sheet에 `textbook_card + supplement_card + activity_sheet`가 공존할 수 있다.
- 기존 단일 교과서 config도 회귀 없이 계속 동작한다.
- `사회 + 사회과부도`, `수학 + 수학익힘`, `과학 + 실험관찰` 세 케이스를 같은 config 모델로 설명할 수 있다.
