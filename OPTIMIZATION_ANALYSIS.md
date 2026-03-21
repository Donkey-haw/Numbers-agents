# Optimization Analysis

## 목적
- 현재 기능은 그대로 유지하면서 전체 단원 생성 시간을 줄일 수 있는 지점을 정리한다.
- 기준 파이프라인:
  1. 교과서 분석 및 차시 범위 추론
  2. Gemini CLI로 `lesson_analysis` / `activity_plan` 생성
  3. 교과서 카드 + 활동 HTML 렌더 및 PNG 캡처
  4. AppleScript로 Numbers 삽입
  5. 결과 검증 및 cleanup

## 최근 실측 기준
- 전체 단원 실행: 약 `13분 28초`
- 결과 파일: [1-1. 평화 통일을 위한 노력.numbers](/Users/jonyeock/Desktop/Tool/NumbersAuto/output/1-1.%20평화%20통일을%20위한%20노력.numbers)
- 현재 병목 후보는 크게 `Gemini 호출`, `Playwright 캡처`, `Numbers AppleScript 삽입` 세 구간이다.

## 우선순위 높은 최적화

### 1. Gemini 프롬프트 중복 축소
- 영향도: 매우 큼
- 현재 문제:
  - [run_gemini_cli_pipeline.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/run_gemini_cli_pipeline.py#L211) 에서 단원 전체 `textbook_context`를 만들고
  - [run_gemini_cli_pipeline.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/run_gemini_cli_pipeline.py#L252) 에서 그 전체 컨텍스트를 각 차시 프롬프트마다 다시 주입한다.
  - 차시 수가 `N`개면, 단원 전체 텍스트가 사실상 `N`번 반복 전송된다.
- 최적화 방향:
  - 현재 차시에 해당하는 `extracted_text`만 프롬프트에 넣는다.
  - 필요하면 앞뒤 차시 제목 정도만 경계 정보로 추가한다.
  - 전체 `ocr_lines` 같은 원시 데이터는 제외한다.
- 기능 유지 근거:
  - 최종 결과는 여전히 각 차시별 분석/활동 생성이다.
  - 차시 외 텍스트를 반복 제공하지 않아도 요구 기능은 동일하다.

### 2. Gemini 호출 병렬화
- 영향도: 매우 큼
- 현재 문제:
  - [run_gemini_cli_pipeline.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/run_gemini_cli_pipeline.py#L344) 이후 루프가 차시별로 완전히 직렬 실행된다.
  - `lesson_analysis -> activity_plan`은 같은 차시 안에서는 순서가 필요하지만, 차시 간에는 독립적이다.
- 최적화 방향:
  - 차시 단위 worker pool을 두고 2~3개씩 병렬 실행한다.
  - 각 worker 안에서는 `lesson_analysis -> activity_plan` 순서를 유지한다.
- 기능 유지 근거:
  - 차시 간 데이터 의존성이 없어 출력 의미가 바뀌지 않는다.
  - 단지 wall-clock 시간만 줄어든다.

### 3. Playwright 캡처의 고정 대기 제거
- 영향도: 큼
- 현재 문제:
  - [generate_numbers_lesson.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/generate_numbers_lesson.py#L189) 과 [generate_numbers_with_activities.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/generate_numbers_with_activities.py#L85) 에서 카드마다 `wait_for_timeout(1200)`를 사용한다.
  - 카드 수만큼 최소 `1.2초`가 누적된다.
- 최적화 방향:
  - `page.wait_for_load_state("networkidle")`
  - `document.fonts.ready`
  - 필요하면 `.sheet` 또는 `.card` 렌더 완료 sentinel
  - 위 조건을 만족하면 바로 screenshot
- 기능 유지 근거:
  - “충분히 렌더된 뒤 캡처”라는 조건은 유지된다.
  - 고정 sleep만 제거한다.

### 4. 브라우저 캡처 단일 세션화
- 영향도: 큼
- 현재 문제:
  - [generate_numbers_with_activities.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/generate_numbers_with_activities.py#L273) 에서 교과서 카드 캡처
  - [generate_numbers_with_activities.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/generate_numbers_with_activities.py#L280) 에서 활동 카드 캡처
  - 두 번의 별도 Chromium 루프를 돈다.
- 최적화 방향:
  - 교과서 카드와 활동 카드를 하나의 capture queue로 합친다.
  - 하나의 browser session과 소수의 page worker만 사용한다.
- 기능 유지 근거:
  - 입력 HTML과 출력 PNG는 동일하다.
  - 브라우저 시작/종료와 직렬 루프만 줄인다.

### 5. Numbers 검증 재오픈 제거
- 영향도: 중간 이상
- 현재 문제:
  - [generate_numbers_with_activities.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/generate_numbers_with_activities.py#L286) 에서 삽입 후
  - [generate_numbers_lesson.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/generate_numbers_lesson.py#L274) 의 별도 open/verify/close를 다시 탄다.
- 최적화 방향:
  - 삽입 AppleScript 안에서 마지막에 sheet names를 읽어 반환한다.
  - 저장 후 닫기 전에 검증까지 끝낸다.
- 기능 유지 근거:
  - 검증은 그대로 유지된다.
  - Numbers open/close 한 번을 제거한다.

## 중간 우선순위 최적화

### 6. PDF 페이지 텍스트 캐시
- 현재 문제:
  - [generate_numbers_lesson.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/generate_numbers_lesson.py#L41) 의 `find_query_pages()`가 검색 때마다 각 페이지 텍스트를 다시 읽는다.
  - [run_gemini_cli_pipeline.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/run_gemini_cli_pipeline.py#L225) 에서도 페이지 텍스트를 다시 읽는다.
- 최적화 방향:
  - `page_num -> normalized_text`
  - `page_num -> raw_text`
  - 둘 다 문서 단위로 메모리 캐시
- 기능 유지 근거:
  - 동일 텍스트를 재사용할 뿐이므로 결과는 바뀌지 않는다.

### 7. PDF 페이지 이미지 캐시
- 현재 문제:
  - [generate_numbers_lesson.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/generate_numbers_lesson.py#L121) 의 `extract_pages()`가 매번 동일 페이지를 다시 rasterize한다.
- 최적화 방향:
  - 캐시 키: `pdf path + page number + render scale`
  - 기존 PNG가 유효하면 재생성 생략
- 기능 유지 근거:
  - 같은 PDF와 같은 렌더 옵션이면 이미지 결과는 동일하다.

### 8. 이미지 크기 재측정 제거
- 현재 문제:
  - [generate_numbers_with_activities.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/generate_numbers_with_activities.py#L104) 의 `compute_scaled_height()`가 PNG를 다시 열어 높이를 계산한다.
- 최적화 방향:
  - screenshot 직후 width/height를 같이 기록
  - manifest는 그 메타데이터를 재사용
- 기능 유지 근거:
  - 같은 이미지의 치수만 전달 방식만 바뀐다.

### 9. 프롬프트/스키마 로드 캐시
- 현재 문제:
  - [run_gemini_cli_pipeline.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/run_gemini_cli_pipeline.py#L74), [run_gemini_cli_pipeline.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/run_gemini_cli_pipeline.py#L153), [run_gemini_cli_pipeline.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/run_gemini_cli_pipeline.py#L163), [run_gemini_cli_pipeline.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/run_gemini_cli_pipeline.py#L170) 에서 파일을 반복 읽는다.
- 최적화 방향:
  - 프로세스 시작 시 prompt text와 schema를 한 번만 load
- 기능 유지 근거:
  - 내용은 동일하고 I/O만 감소한다.

### 10. OCR payload 축소
- 현재 문제:
  - [run_gemini_cli_pipeline.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/run_gemini_cli_pipeline.py#L182) 에서 chart가 있으면 `ocr_lines`와 `ocr_sections`를 모두 싣는다.
- 최적화 방향:
  - `ocr_sections`만 유지
  - config에 차시명 정보가 이미 있으면 OCR 자체를 skip
- 기능 유지 근거:
  - 현재 규칙상 쪽수는 무시하고 차시명 중심이므로 기능과 일치한다.

## 낮은 우선순위 최적화

### 11. JSON 추출 파서 단순화
- 현재 문제:
  - [run_gemini_cli_pipeline.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/run_gemini_cli_pipeline.py#L78) 에서 여러 후보에 대해 `json.loads()`를 반복 시도한다.
- 최적화 방향:
  - wrapper JSON을 먼저 파싱
  - `response` 내부는 brace-balanced tail parser로 마지막 객체만 추출
- 기능 유지 근거:
  - 반환 JSON 해석 규칙은 동일하다.

### 12. artifact 기록 레벨 분리
- 현재 문제:
  - [run_gemini_cli_pipeline.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/run_gemini_cli_pipeline.py#L105) 가 prompt/raw/wrapper/parsed를 모두 기록한다.
- 최적화 방향:
  - 기본 실행은 parsed JSON + stderr만 저장
  - 상세 기록은 `--debug-artifacts`에서만 저장
- 기능 유지 근거:
  - 핵심 산출물은 유지되고 디버그 부가 산출물만 줄어든다.

### 13. Numbers 템플릿 복사 재사용 모드
- 현재 문제:
  - [generate_numbers_lesson.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/generate_numbers_lesson.py#L107) 의 `copy_template()`가 항상 전체 `.numbers` 번들을 새로 복사한다.
- 최적화 방향:
  - 프로파일링/반복 실행용 `--reuse-output` 모드 추가
- 기능 유지 근거:
  - 반복 개발 시에만 쓰고, 기본 동작은 유지할 수 있다.

## 권장 실행 순서
1. Gemini 프롬프트 축소
2. 차시 단위 Gemini 병렬화
3. Playwright 고정 sleep 제거
4. 브라우저 캡처 단일 세션화
5. Numbers 검증 재오픈 제거
6. PDF 텍스트/이미지 캐시

## 예상 효과
- 1~4번만 적용해도 현재 `13분대` 실행을 가장 크게 줄일 가능성이 높다.
- 특히 전체 단원 실행에서는 `Gemini 호출 직렬화`와 `카드별 1.2초 sleep`이 가장 먼저 손봐야 할 지점이다.
