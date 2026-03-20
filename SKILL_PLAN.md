# NumbersAuto Skill Plan

## 목표
- 이 저장소의 수작업 절차를 재사용 가능한 Codex Skill로 정리한다.
- 입력 파일만 바꾸면 다른 단원이나 다른 과목도 같은 흐름으로 Numbers 교재 파일을 만들 수 있게 한다.

## Skill 범위
- 입력:
  - 교과서 PDF
  - 빈 Numbers 파일
  - 차시 구성이 적힌 진도표 이미지 또는 구조화된 JSON/YAML
- 출력:
  - 차시별 시트가 구성된 `.numbers` 파일
  - 중간 산출물 HTML 템플릿
  - 실행 로그와 검증 결과

## 권장 Skill 구조
- `SKILL.md`
  - 언제 이 Skill을 써야 하는지
  - 필요한 입력물
  - 기본 실행 순서
  - 실패 시 점검 항목
- `templates/`
  - 공통 카드 HTML 템플릿
  - 색상 프리셋
  - 시트 이름 규칙 예시
- `scripts/`
  - PDF 페이지 추출
  - 진도표 파싱 또는 설정 파일 생성
  - 카드 렌더링
  - Numbers 삽입
  - 검증 및 cleanup
- `references/`
  - 쪽수 매핑 규칙
  - Numbers AppleScript 제약 사항

## 구현 단계

### 1. 설정 중심 구조로 전환
- 현재 `generate_unit2_cards.py` 안의 하드코딩된 `SECTIONS`를 외부 설정 파일로 분리한다.
- 예시:

```json
{
  "unit_title": "민주화와 산업화로 달라진 생활 문화",
  "output_file": "6-1-2. 민주화와 산업화로 달라진 생활 문화.numbers",
  "sections": [
    {
      "sheet_name": "7차시",
      "title": "주제 도입 / 민주화 운동은 왜 일어났을까요?",
      "textbook_pages": [26, 27, 28, 29]
    }
  ]
}
```

### 2. 교과서 쪽수와 PDF 페이지 매핑 일반화
- 현재는 `PDF 페이지 = 교과서 쪽수 + 2`로 가정하고 있다.
- 이 규칙을 설정으로 분리한다.
- 과목별로 표지/목차 길이가 다르면 offset을 바꿀 수 있게 해야 한다.

### 3. 진도표 입력 자동화
- 1차 목표:
  - 사용자가 진도표를 보고 직접 JSON/YAML을 작성하도록 하는 최소 버전
- 2차 목표:
  - OCR 기반으로 진도표 이미지에서 차시명과 쪽수를 추출하는 보조 스크립트 추가
- OCR 결과는 반드시 사람이 검토하도록 설계한다.

### 4. 카드 템플릿 모듈화
- 현재 생성 스크립트가 HTML 문자열을 직접 만들고 있다.
- 공통 Jinja2 템플릿 또는 정적 HTML 템플릿으로 분리해 재사용성을 높인다.
- 카드 종류:
  - 도입형
  - 일반 2열형
  - 단일 페이지형
  - 주제 마무리형

### 5. Numbers 삽입 자동화 일반화
- AppleScript가 현재 파일명과 시트명을 직접 들고 있다.
- 입력 설정을 읽어 시트 생성과 이미지 삽입을 동적으로 하도록 수정한다.
- 삽입 후 검증 단계에서 시트명 목록을 다시 읽어 기대값과 비교한다.

### 6. 실행 래퍼 추가
- 한 번에 전체를 실행하는 CLI를 만든다.
- 예시:

```bash
python3 scripts/generate_numbers_lesson.py \
  --pdf "[사회]6_1_교과서.pdf" \
  --template "빈 넘버스 파일.numbers" \
  --config "configs/unit2.json"
```

### 7. 결과 검증과 cleanup 표준화
- 검증:
  - 출력 `.numbers` 파일 존재 여부
  - 시트명 일치 여부
  - 카드 PNG 생성 여부
- cleanup:
  - 성공 시 임시 `assets/pages`, `assets/cards` 삭제
  - 실패 시 디버깅용 보관 옵션 추가

## 바로 다음 작업
- `configs/` 디렉토리를 만들고 단원별 설정을 누적한다. 완료: `unit2.json`
- [scripts/generate_numbers_lesson.py](/Users/jonyeock/Desktop/Tool/NumbersAuto/scripts/generate_numbers_lesson.py) 를 기준 실행기로 삼고 구식 단원 전용 스크립트를 정리한다.
- `진도표` 이미지에서 설정 초안을 만들기 위한 OCR 보조 스크립트를 추가한다. 완료: `ocr_progress_chart.swift`, `draft_config_from_progress_chart.py`
- `TextBookInSkill`에 예시 config, 체크리스트, 실패 사례를 더 보강한다.

## 완료 기준
- 새로운 PDF와 차시 설정 파일만 주면 코드를 수정하지 않고 `.numbers` 파일을 생성할 수 있다.
- 사용자 입력이 이미지 진도표뿐일 때도 최소한 설정 초안을 자동 생성할 수 있다.
- 원본 PDF와 원본 Numbers 템플릿은 항상 보존된다.
