# 🍎 Numbers 수업 자료 자동 생성 파이프라인

> **HTML/CSS → 스크린샷 → Numbers 삽입** 방식으로 초고퀄리티 수업용 Numbers 파일을 자동 생성하는 전체 프로세스 설계 문서

---

## 1. 핵심 아이디어

Apple Numbers의 `.iwa` 포맷은 폐쇄형(Protobuf)이어서 코드로 직접 디자인을 그리는 것이 불가능하다. 이를 우회하기 위해 **HTML/CSS로 자유롭게 디자인한 뒤, Headless 브라우저로 고해상도 이미지를 캡처하고, AppleScript로 빈 Numbers 파일에 삽입**하는 파이프라인을 구축한다.

```mermaid
graph LR
    A[교과서 PDF] -->|PyMuPDF 페이지 추출| B[페이지별 PNG]
    B --> C[HTML/CSS 카드 생성]
    C -->|Playwright 스크린샷| D[카드 이미지 PNG]
    D -->|AppleScript 삽입| E[완성 .numbers 파일]
```

---

## 2. 기술 스택

| 도구 | 역할 | 비고 |
|------|------|------|
| **PyMuPDF** (`fitz`) | PDF → 이미지 변환 | 3x 줌(216 DPI)으로 고해상도 추출 |
| **HTML + Tailwind CSS** | 카드 UI 디자인 | 그라데이션, 둥근 모서리, 그림자 등 자유로운 디자인 |
| **Playwright** (Chromium) | HTML → PNG 스크린샷 | `device_scale_factor=2`로 Retina 해상도 캡처 |
| **AppleScript** (`osascript`) | Numbers 앱 원격 제어 | 이미지 삽입, 표 생성, 시트 관리 |

---

## 3. 전체 파이프라인 (단계별)

### STEP 1. 교과서 PDF 분석 및 차시 분할

```python
import fitz
doc = fitz.open("교과서.pdf")

# 각 페이지의 텍스트를 추출하여 제목/주제 변경점을 탐지
for i in range(doc.page_count):
    text = doc[i].get_text("text")[:200]
    print(f"Page {i+1}: {text}")
```

**차시 분할 원칙:**
- 표지, 구성, 목차 → 별도 시트로 분리
- 주제(제목)가 바뀌는 지점에서 차시를 나눔
- 예: p.22~25 "평화 통일을 위해 어떤 노력을 해야 할까요?" = 1개 차시

### STEP 2. 페이지를 고해상도 이미지로 렌더링

```python
for page_num in target_pages:  # 예: [21, 22, 23, 24] (0-indexed)
    page = doc[page_num]
    mat = fitz.Matrix(3, 3)  # 3배 줌 = 216 DPI
    pix = page.get_pixmap(matrix=mat)
    pix.save(f"교과서_p{page_num+1}.png")
```

**결과물:** 각 페이지가 약 1829×2424px의 선명한 PNG 파일로 저장됨.

### STEP 3. HTML/CSS로 카드 UI 디자인

교과서 페이지를 담을 카드 레이아웃을 HTML로 디자인한다.

**배치 원칙:**
- 한 행(row)에 최대 **2페이지**를 가로로 나란히 배치
- 3페이지 이상이면 하단으로 이어서 2열 그리드로 배치
- 예: 4페이지 → 2×2 그리드

```
┌─────────────────────────────────────┐
│  📖 교과서 학습 — [차시 제목]  STEP 1  │ ← 보라색 그라데이션 헤더
├──────────────┬──────────────────────┤
│   p.22       │      p.23           │ ← 2페이지 가로 배치
│              │                     │
├──────────────┼──────────────────────┤
│   p.24       │      p.25           │ ← 다음 2페이지 하단 배치
│              │                     │
├─────────────────────────────────────┤
│  • 사회 6-1 · 1단원 · 평화 통일     │ ← 하단 정보바
└─────────────────────────────────────┘
```

**카드 종류 (수업 요소별):**

| 카드 | 아이콘 | 헤더 색상 | 용도 |
|------|--------|-----------|------|
| 교과서 카드 | 📖 | 보라 (`#4f46e5→#7c3aed`) | 교과서 PDF 페이지 배치 |
| 영상 카드 | ▶️ | 빨강 (`#dc2626→#ef4444`) | 유튜브/동영상 썸네일 |
| 노트 카드 | 📝 | 남색 (`#1e40af→#3b82f6`) | 코넬 노트 / 필기 영역 |
| 활동 카드 | ✅ | 초록 (`#059669→#10b981`) | 체크리스트 / 모둠 활동 |
| 사회과부도 카드 | 🗺️ | 주황 (`#d97706→#f59e0b`) | 사회과 부도 지도/자료 |

### STEP 4. Playwright 스크린샷 캡처

```python
from playwright.async_api import async_playwright

async def capture(html_path, output_path):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(
            viewport={'width': 1600, 'height': 2400},
            device_scale_factor=2  # Retina 해상도
        )
        await page.goto(f'file://{html_path}')
        await page.wait_for_timeout(2000)
        
        # 카드 크기에 맞춘 정확한 캡처
        card = await page.query_selector('.card')
        box = await card.bounding_box()
        await page.set_viewport_size({
            'width': int(box['width']),
            'height': int(box['height']) + 10
        })
        await page.screenshot(path=output_path, full_page=True)
        await browser.close()
```

### STEP 5. AppleScript로 Numbers에 삽입

```applescript
tell application "Numbers"
    activate
    open POSIX file "/path/to/빈 넘버스 파일.numbers"
    delay 2
    
    tell active sheet of document 1
        -- 기존 요소 모두 삭제
        try
            delete every table
            delete every image
            delete every text item
            delete every shape
        end try
        
        -- 카드 이미지 삽입
        set img to make new image with properties ¬
            {file: POSIX file "/path/to/교과서_차시카드.png"}
        set position of img to {20, 20}
    end tell
    
    save document 1
end tell
```

**위치(position) 가이드:** (단위: pt, 72pt = 1인치)

| 카드 | x 좌표 | y 좌표 | 비고 |
|------|--------|--------|------|
| 교과서 | 20 | 20 | 좌측 상단, 메인 |
| 영상 | 820 | 20 | 우측 상단 |
| 노트 | 820 | 500 | 우측 중단 |
| 활동 | 820 | 900 | 우측 하단 |

---

## 4. 시트 구성 전략

하나의 `.numbers` 파일 안에 여러 시트(탭)를 활용하여 수업 흐름을 구성한다.

| 시트 | 내용 | 카드 구성 |
|------|------|-----------|
| 표지 | 단원명, 학습 목표 | 타이틀 카드 |
| 1차시 | 교과서 p.12~15 + 활동 | 교과서 + 노트 + 활동 |
| 2차시 | 교과서 p.16~19 + 영상 | 교과서 + 영상 + 노트 |
| 3차시 | 교과서 p.20~21 + 부도 | 교과서 + 부도 + 활동 |
| 4차시 | 교과서 p.22~25 + 정리 | 교과서 + 노트 + 활동 |
| 정리 | 단원 마무리 퀴즈 | 활동 카드 |

---

## 5. 자동화 확장 계획

### 5-1. 일괄 생성 스크립트
```
python3 generate_all.py --pdf "교과서.pdf" --lessons "12-15,16-19,20-21,22-25" --output "1단원_통일.numbers"
```
- 입력: 교과서 PDF + 차시별 페이지 범위
- 출력: 모든 차시가 시트별로 정리된 완성 Numbers 파일

### 5-2. 카드 커스터마이징
- `cards/` 폴더에 카드 종류별 HTML 템플릿을 모듈화
- JSON 설정 파일로 차시별 카드 조합을 정의

```json
{
  "단원명": "평화 통일을 위한 노력",
  "차시": [
    {
      "시트명": "1차시",
      "카드": [
        {"type": "textbook", "pages": [12, 13, 14, 15]},
        {"type": "notes", "title": "코넬 노트"},
        {"type": "activity", "items": ["학습 목표 확인", "핵심 단어 정리"]}
      ]
    }
  ]
}
```

---

## 6. 디렉토리 구조 및 에셋 관리 규칙

### 6-1. 폴더 구조

```
NumbersAuto/
│
├── [사회]6_1_교과서.pdf              # 📥 원본 교과서 PDF (입력, 불변)
├── [사회]6_사회과 부도.pdf           # 📥 원본 사회과부도 (입력, 불변)
├── 빈 넘버스 파일.numbers            # 📥 빈 Numbers 베이스 파일 (입력, 불변)
├── 넘버스 교재 템플릿.numbers/       # 📥 기존 참고 템플릿 (참고용)
├── 6-1-1-1. 평화 통일을 위한 노력.numbers/  # 📥 완성 예시 (참고용)
│
├── assets/                           # 🖼️ 모든 이미지 에셋 (임시)
│   ├── pages/                        #   PDF에서 추출한 개별 교과서 페이지 PNG
│   ├── cards/                        #   HTML 카드를 캡처한 스크린샷 PNG
│   └── backgrounds/                  #   배경/레이아웃 이미지
│
├── html/                             # 🎨 HTML/CSS 카드 템플릿 소스
│   ├── 교과서카드.html
│   ├── 교과서_차시카드.html
│   ├── modular_layout.html
│   └── 초고퀄_템플릿_배경.html
│
├── scripts/                          # ⚙️ 자동화 스크립트
│   ├── snap_modular.py               #   Playwright 스크린샷
│   └── build_modular_numbers.scpt    #   AppleScript Numbers 조작
│
├── output/                           # 📤 생성 완료된 Numbers 파일 (최종 결과물)
│
└── PROCESS.md                        # 📄 본 설계 문서
```

### 6-2. 에셋 관리 원칙

| 규칙 | 설명 |
|------|------|
| **에셋은 반드시 `assets/` 하위에 저장** | 루트 디렉토리에 이미지 파일을 직접 두지 않는다. |
| **하위 폴더별 분류** | `pages/` = PDF 추출 이미지, `cards/` = 카드 스크린샷, `backgrounds/` = 배경 이미지 |
| **네이밍 규칙** | 페이지: `교과서_p{번호}.png`, 카드: `{카드종류}_{차시정보}.png` |
| **원본 PDF는 불변** | `[사회]6_1_교과서.pdf` 등 입력 파일은 절대 수정/삭제하지 않는다. |
| **HTML 소스는 `html/`에 보관** | 카드 디자인 템플릿은 재사용을 위해 영구 보관한다. |

### 6-3. 🧹 에셋 정리(Cleanup) 정책

> [!IMPORTANT]
> **Numbers 파일 생성이 완료되면, `assets/` 폴더의 이미지를 삭제한다.**

Numbers 파일은 패키지 내부에 삽입된 이미지를 자체적으로 보관하므로, 외부의 임시 에셋은 더 이상 필요하지 않다.

**자동 정리 명령어:**
```bash
# Numbers 파일 생성 완료 후 실행
rm -rf assets/pages/*
rm -rf assets/cards/*
rm -rf assets/backgrounds/*
echo "✅ 에셋 정리 완료. output/ 폴더의 .numbers 파일만 남았습니다."
```

**정리 타이밍:**
1. `output/` 폴더에 최종 `.numbers` 파일이 저장된 것을 확인한다.
2. 해당 `.numbers` 파일을 Numbers 앱에서 열어 정상 렌더링을 검증한다.
3. 검증 통과 후 위 정리 명령어를 실행한다.

**삭제하지 않는 것:**
- `html/` 폴더 (카드 디자인 재사용을 위해 영구 보관)
- `scripts/` 폴더 (자동화 스크립트 영구 보관)
- 루트의 원본 PDF 파일들
- `PROCESS.md`
