# Optimization Analysis

## 목적
- 현재 파이프라인의 실행 시간 병목을 정리하고, 이미 반영된 최적화와 남은 최적화를 구분한다.
- 기준 파이프라인:
  1. 교과서/보조교재 분석 및 차시 범위 추론
  2. Gemini CLI로 `lesson_analysis` / `activity_plan` 생성
  3. 교과서 카드 + 보조자료 카드 + 활동 HTML 렌더 및 PNG 캡처
  4. AppleScript로 Numbers 삽입
  5. 결과 검증 및 cleanup

## 최근 실측 기준
- 사회 `민주주의와 선거` 교과서만:
  - 전체 파이프라인 약 `155.34s`
  - Gemini/전처리 구간 약 `126.40s`
  - 렌더 + Numbers 삽입 구간 약 `28.94s`
- 사회 `민주화와 산업화로 달라진 생활 문화` 교과서 + 사회과부도:
  - 교과서/보조교재만 Numbers 생성 약 `39.17s`
  - 활동 포함 최종 합성 단계 약 `52.90s`
- 수학 `각기둥과 각뿔` 교과서 + 수학익힘:
  - 렌더 자체는 정상
  - Numbers 자동 삽입은 간헐적으로 AppleScript 호출 실패가 남아 있음

## 현재 병목
- 1순위: Gemini 차시별 호출 시간
- 2순위: Playwright 캡처 시간
- 3순위: Numbers AppleScript 삽입 안정성

## 권장 실행 순서 상태

### 1. Gemini 프롬프트 축소
- 상태: 완료
- 반영 내용:
  - [run_gemini_cli_pipeline.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/run_gemini_cli_pipeline.py) 는 차시별 `current_section.extracted_text` 중심으로 프롬프트를 구성한다.
  - 전체 단원 본문을 차시마다 반복 전송하지 않는다.

### 2. 차시 단위 Gemini 병렬화
- 상태: 완료
- 반영 내용:
  - [run_gemini_cli_pipeline.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/run_gemini_cli_pipeline.py) 에 `ThreadPoolExecutor(max_workers=...)`가 들어가 있다.
  - 차시 간 병렬, 차시 내부 `lesson_analysis -> activity_plan` 순서는 유지한다.

### 3. Playwright 고정 sleep 제거
- 상태: 완료
- 반영 내용:
  - [generate_numbers_lesson.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/generate_numbers_lesson.py)
  - [generate_numbers_with_activities.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/generate_numbers_with_activities.py)
  - 위 두 경로 모두 `networkidle`, `document.fonts.ready`, selector visible 기반으로 대기한다.

### 4. 브라우저 캡처 단일 세션화
- 상태: 부분 완료
- 반영 내용:
  - 교과서 카드 캡처 루프 내부에서는 browser 세션을 하나로 유지한다.
  - 활동 카드 캡처 루프 내부에서도 browser 세션을 하나로 유지한다.
- 아직 남은 점:
  - 교과서 카드와 활동 카드를 하나의 capture queue로 완전히 통합하지는 않았다.
  - 즉 `generate_numbers_with_activities.py` 기준으로는 두 번의 별도 캡처 단계가 남아 있다.

### 5. Numbers 검증 재오픈 제거
- 상태: 완료
- 반영 내용:
  - 삽입 AppleScript가 마지막에 시트명을 반환한다.
  - [generate_numbers_lesson.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/generate_numbers_lesson.py) 와 [generate_numbers_with_activities.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/generate_numbers_with_activities.py) 는 반환된 시트명으로 검증한다.
  - 기본 경로에서 별도 reopen/verify/close 한 사이클은 제거됐다.

### 6. PDF 텍스트/이미지 캐시
- 상태: 부분 완료
- 텍스트 캐시:
  - 완료
  - [generate_numbers_lesson.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/generate_numbers_lesson.py) 에 `TEXT_CACHE_KEY`, `NORMALIZED_TEXT_CACHE_KEY`가 있다.
- 이미지 캐시:
  - 부분 완료
  - 같은 출력 PNG가 있으면 재사용한다.
  - [build_resource_index.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/build_resource_index.py) 도 재사용 스캔 구조를 만든다.
- 아직 남은 점:
  - `pdf path + page number + scale` 기준의 영속 이미지 캐시 체계를 전체 렌더 경로가 완전히 공유하진 않는다.

## 중간 우선순위 상태

### 7. PDF 페이지 이미지 캐시
- 상태: 부분 완료
- 현재:
  - `extract_pages()`는 기존 PNG가 있으면 재생성하지 않는다.
- 남은 점:
  - 전역 캐시 정책과 무효화 규칙이 아직 없다.

### 8. 이미지 크기 재측정 제거
- 상태: 완료
- 반영 내용:
  - 캡처 직후 `capture_size`를 저장한다.
  - [generate_numbers_with_activities.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/generate_numbers_with_activities.py) 는 이 메타데이터를 사용해 scaled height를 계산한다.

### 9. 프롬프트/스키마 로드 캐시
- 상태: 완료
- 반영 내용:
  - [run_gemini_cli_pipeline.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/run_gemini_cli_pipeline.py) 에 `PROMPT_CACHE`, `TEXT_CACHE`, `SCHEMA_CACHE`가 있다.

### 10. OCR payload 축소
- 상태: 부분 완료
- 현재:
  - chart 입력은 선택적이다.
  - config만으로도 다수 실행 경로가 동작한다.
- 남은 점:
  - chart를 붙였을 때 payload 최소화 규칙은 더 정리할 수 있다.

## 낮은 우선순위 상태

### 11. JSON 추출 파서 단순화
- 상태: 부분 완료
- 현재:
  - wrapper JSON과 trailing JSON object 파서를 사용한다.
- 남은 점:
  - brace-balanced tail parser로 더 단순화할 여지는 있다.

### 12. artifact 기록 레벨 분리
- 상태: 완료
- 반영 내용:
  - [run_gemini_cli_pipeline.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/run_gemini_cli_pipeline.py) 의 `--debug-artifacts`가 있을 때만 raw/wrapper/response를 상세 저장한다.

### 13. Numbers 템플릿 복사 재사용 모드
- 상태: 미완료
- 현재:
  - [generate_numbers_lesson.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/generate_numbers_lesson.py) 의 `copy_template()`는 기본적으로 항상 새 복사를 수행한다.

## 다교재 확장과 성능
- 다교재 자체는 렌더/합성 경로에 반영되었다.
- 보조교재는 `supplement_card`로 관리되고, 교과서 아래에 배치된다.
- 활동 생성은 현재 원칙상 주교과서 중심으로 유지하고 있어, Gemini 토큰 폭증을 막는다.
- 재사용 스캔 구조는 아래 단계까지 구축되었다.
  - [build_resource_index.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/build_resource_index.py)
  - [build_unit_bundle.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/build_unit_bundle.py)
  - [build_runtime_config.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/build_runtime_config.py)
  - [generate_numbers_from_bundle.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/generate_numbers_from_bundle.py)

## 현재 남은 핵심 과제
1. Numbers AppleScript 호출 안정화
- 사회/수학 모두에서 간헐적인 `osascript` 실패가 남아 있다.
- 자산/스크립트 자체는 정상이어도 첫 호출이 실패하고, 재시도나 수동 스크립트 실행은 통과하는 경우가 있다.

2. 교과서 카드와 활동 카드 캡처 완전 통합
- 현재는 교과서 캡처와 활동 캡처가 분리돼 있다.
- 하나의 capture queue로 합치면 브라우저 시작/종료 비용을 더 줄일 수 있다.

3. 재사용 캐시의 영속성 강화
- `resource_index`, `unit_bundle`, generated config는 갖췄다.
- 하지만 페이지 raster cache와 render cache까지 완전히 재사용되는 구조는 아직 아니다.

## 현재 판단 요약
- 문서의 권장 실행 순서 기준으로 핵심 큰 항목은 대부분 반영됐다.
- 상태를 한 줄로 요약하면:
  - 완료: `1, 2, 3, 5`
  - 부분 완료: `4, 6`
  - 미완료: `13`

## 다음 권장 작업
1. `run_gemini_cli_pipeline.py` 와 `generate_numbers_lesson.py` 의 Numbers 자동 삽입 실패를 재현 가능하게 고정
2. 교과서 카드/활동 카드 캡처를 하나의 browser queue로 통합
3. render cache 정책을 명시하고 재사용 경로를 강화
