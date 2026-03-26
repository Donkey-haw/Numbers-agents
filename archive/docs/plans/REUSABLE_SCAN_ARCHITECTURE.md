# Reusable Scan Architecture

## 목적
- 다교재 단원 생성에서 매 실행마다 전체 교과서와 진도표를 다시 분석하지 않도록 한다.
- 최초 1회 스캔 결과를 구조화 아티팩트로 저장하고, 이후에는 해당 아티팩트를 재사용해 단원별 config를 빠르게 생성한다.

## 왜 필요한가
- 다교재 단원은 `사회 + 사회과부도`, `수학 + 수학익힘`, `과학 + 실험관찰`처럼 2권 이상 PDF를 동시에 다뤄야 한다.
- 매 실행마다 전체 PDF를 다시 읽으면:
  - 실행 시간이 길어진다.
  - 페이지 텍스트 추출이 반복된다.
  - Gemini에 넘길 문맥도 커져 토큰 낭비가 커진다.
- 특히 한 학기 전체를 반복 제작하는 경우, 동일 교재를 계속 다시 스캔하는 비용이 불필요하다.

## 권장 구조

### 1. Scan Once
- 교과서 PDF 전체 스캔
- 보조 교재 PDF 전체 스캔
- 진도표 전체 스캔
- 제목/차시/단원 후보 추출

### 2. Save Structured Artifacts
- `resource_catalog.json`
- `resource_index.json`
- `progress_chart_map.json`
- `unit_bundle.json`

### 3. Reuse Per Run
- 원하는 단원만 선택
- 기존 artifact에서 실행용 config 생성
- 해당 단원에 필요한 source chunk만 Gemini와 렌더 파이프라인에 전달

## 아티팩트 계층

### A. Resource Catalog
- 어떤 프로젝트에 어떤 PDF가 연결되는지 정의한다.
- 예:
  - 사회
  - 사회과부도
  - 수학
  - 수학익힘
  - 과학
  - 실험관찰

### B. Resource Index
- 교재별 전체 스캔 결과
- 페이지 텍스트, normalized text, 제목 후보, 검색용 메타데이터를 담는다.

### C. Progress Chart Map
- 진도표를 단원/주제/차시 구조로 정리한 결과
- 차시명, 주제명, 도입/정리 여부, 활동 요약을 담는다.

### D. Unit Bundle
- 특정 단원 실행에 필요한 source mapping 묶음
- 각 차시에 대해 어떤 resource가 어떤 역할로 들어가는지 확정한다.
- 첫 본차시가 `주제 도입` 페이지를 함께 포함해야 하는지 여부도 여기서 확정한다.

### E. Runtime Config
- 실제 Numbers 생성기가 읽는 실행용 config
- 가능한 한 얇게 유지한다.

## 파일 역할

### resource_catalog.json
- 전역 교재 선언
- PDF 경로
- 과목명
- 교재 종류

### resource_index.json
- resource 하나에 대한 전 페이지 인덱스
- 페이지별 텍스트와 검색 메타데이터
- 제목 후보
- 이미지 캐시 키

### progress_chart_map.json
- 진도표 전체 구조
- 단원/주제/차시/도입/정리 포함

### unit_bundle.json
- 하나의 단원 실행 단위
- 각 lesson마다 `sources[]` 포함
- source별 role과 page mapping 포함

### generated config
- 현재 `generate_numbers_lesson.py` 또는 후속 오케스트레이터가 읽는 최종 실행 입력

## 권장 디렉토리

```text
artifacts/
  scan/
    social_6_1/
      resource_catalog.json
      progress_chart_map.json
      resources/
        social_textbook.resource_index.json
        social_atlas.resource_index.json
      bundles/
        unit2_democracy_election.unit_bundle.json
        unit2_state_agencies.unit_bundle.json
      generated_configs/
        social_6_1_unit2_democracy_election.generated.json
```

## 실행 흐름

### Step 1. Build Resource Catalog
- 입력:
  - 프로젝트 루트
  - 교재 목록
- 출력:
  - `resource_catalog.json`

### Step 2. Build Resource Index
- 입력:
  - 각 PDF
- 출력:
  - `*.resource_index.json`
- 수행 내용:
  - 전 페이지 text 추출
  - normalized text 저장
  - 제목 후보 추출
  - 검색 인덱스 준비

### Step 3. Build Progress Chart Map
- 입력:
  - 진도표 PDF 또는 이미지
- 출력:
  - `progress_chart_map.json`

### Step 4. Build Unit Bundle
- 입력:
  - `resource_catalog`
  - `resource_index`
  - `progress_chart_map`
  - 선택 단원
- 출력:
  - `unit_bundle.json`
- 수행 내용:
  - 차시별 source 결정
  - title_query 제안
  - page range mapping
  - `주제 도입`을 별도 시트로 둘지, 첫 본차시에 흡수할지 결정
  - 정리 페이지 포함 여부 결정

### Step 5. Build Runtime Config
- 입력:
  - `unit_bundle`
- 출력:
  - `generated config`

### Step 6. Generate Numbers
- 입력:
  - `generated config`
- 출력:
  - `.numbers`

## Gemini 최적화 관점

### 현재 문제
- 실행 시마다 전체 문서를 다시 읽고 문맥을 구성하면 비효율적이다.

### 개선 방향
- Gemini에는 `unit_bundle` 기반 차시별 source chunk만 전달한다.
- 전 페이지 텍스트는 `resource_index`에만 저장하고, Gemini prompt에는 필요한 일부만 실어 보낸다.

### 기대 효과
- prompt 축소
- 토큰 절감
- 재시도 비용 감소
- 다교재 단원에서도 차시 단위 병렬화 유지 가능

## 다교재에서 중요한 설계 결정

### 1. source mapping은 unit bundle에서 확정한다
- 런타임에 모든 것을 다시 유추하지 않는다.

### 2. optional supplement를 허용한다
- 모든 차시에 보조교재가 반드시 붙지 않을 수 있다.
- 보조교재는 기본적으로 Numbers 배치용 보조 자료이며, Gemini 활동 생성의 1차 입력은 주교과서로 유지한다.

### 3. 도입/정리 차시는 별도 섹션 타입으로 유지한다
- 진도표 구조를 보존해야 한다.
- 다만 교과서 본문의 `주제 도입`은 항상 별도 시트가 되는 것이 아니라, 뒤쪽 주제에서는 첫 본차시에 흡수될 수 있다.

### 4. main resource와 supplement resource를 구분한다
- 추론 규칙과 배치 규칙이 다르다.

## 권장 스키마 세트
- `resource_catalog.schema.json`
- `resource_index.schema.json`
- `progress_chart_map.schema.json`
- `unit_bundle.schema.json`

이번 단계에서는 핵심 두 개를 우선 만든다.
- `resource_index.schema.json`
- `unit_bundle.schema.json`

## 구현 우선순위
1. `resource_index` 생성기
2. `progress_chart_map` 재사용 정리
3. `unit_bundle` 생성기
4. `generated config` 생성기
5. 기존 파이프라인 연결

## 성공 기준
- 같은 학기 자료에 대해 PDF 전체 스캔은 최초 1회만 수행한다.
- 단원 실행은 기존보다 훨씬 작은 입력만으로 가능하다.
- 다교재 단원에서도 source mapping이 명시적으로 저장된다.
- 기존 단일 교재 실행도 동일 구조로 설명 가능하다.
