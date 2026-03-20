# 📐 Numbers 활동 섹션 HTML 디자인 원칙

> 실제 Numbers 앱에서 학생들에게 배부되는 활동 시트 11종을 정밀 분석하여, HTML로 변환할 때 반드시 지켜야 할 디자인 원칙을 정리한 문서입니다.

---

## 1. 활동 유형 분류 (Activity Type Taxonomy)

분석된 11개 스크린샷에서 추출한 활동 유형은 크게 **10가지 카테고리**로 분류됩니다.

| # | 활동 유형 | 영문명 | 핵심 레이아웃 | 용도 |
|---|--------|------|----------|-----|
| 1 | 배움 노트 | Learning Note | 줄 간격 노트 + 사이드 참조 패널 | 학습 내용 정리 |
| 2 | 질문의 종류 | Question Types Grid | 3×3 컬러 그리드 | 사고력 질문 유형 분류 |
| 3 | 보이다-생각-궁금 | See-Think-Wonder | 3-컬럼 균등 분할 | 관찰 기반 사고 활동 |
| 4 | 프레이어 모델 | Frayer Model | 4-사분면 + 중앙 주제 | 개념 정의/분석 |
| 5 | 개념 은행 + 결합하기 | Concept Bank + Combine | 좌측 리스트 + 우측 사분면 | 개념 수집 및 통합 |
| 6 | 감정/의견 스펙트럼 | Spectrum Line | 수평 양극 축 + 포스트잇 | 의견/감정 배치 |
| 7 | 참고 자료 | Reference Materials | 이미지 갤러리 카드 | 영상/사진 자료 제공 |
| 8 | AI CLASS (지니아튜터) | AI Tutor Activity | 링크 버튼 + 결과 캡처 영역 | AI 도구 활동 |
| 9 | 생각 톡톡 | Thinking Talk | 영상 썸네일 + 응답 컬럼 | 영상 기반 사고 활동 |
| 10 | 활동지 / 학습지 | Worksheet / Assessment | 문제-답변 구조 | 교과서 기반 활동/평가 |

---

## 2. 공통 디자인 원칙 (Universal Design Principles)

### 2.1 🏷️ 섹션 배지 시스템 (Section Badge System)

모든 활동은 **좌상단 배지(Badge)**로 유형을 구분합니다. 이 배지는 활동의 정체성을 결정하는 가장 중요한 시각적 요소입니다.

```
배지 구조:
┌─────────────────┐
│ 🎯 아이콘 + 텍스트 │  ← 둥근 모서리, 컬러 배경
└─────────────────┘
```

**관찰된 배지 유형과 컬러:**

| 배지 텍스트 | 배경색 | 아이콘 | 용도 |
|-----------|------|------|------|
| 노트 정리 | `#F5C842` (골드) | 📝 | 배움 노트 |
| 생각 톡톡 | `#FF6B8A` (코랄) | 💡 | 사고 활동 |
| Numbers 앱 활동 | `#4CAF50` (그린) | 📊 | Numbers 연동 활동 |
| 참고 자료 | `#FF9800` (오렌지) | 🔴 | 보조 자료 |
| AI CLASS | `#2196F3` (블루) | 🤖 | AI 활동 |
| 활동지 | `#FF7043` (딥오렌지) | 📋 | 교과서 활동 |
| 학습지 | `#42A5F5` (라이트블루) | 📝 | 평가/확인 |
| 학습 정리 | `#90CAF9` (페일블루) | 📑 | 정리 활동 |

**HTML 구현 원칙:**
```html
<div class="activity-badge" style="background: var(--badge-color);">
  <span class="badge-icon">🎯</span>
  <span class="badge-text">활동 유형명</span>
</div>
```

**CSS 원칙:**
- `border-radius: 20px` — 완전한 둥근 모서리 (pill shape)
- `padding: 6px 16px` — 수평 여백 강조
- `font-weight: 700` — 볼드체
- `font-size: 14px` — 적당한 크기
- `color: white` — 배경색 위 흰색 텍스트
- 배지는 항상 **컨테이너 외부 좌상단**에 약간 겹치도록 배치 (`position: relative; top: -12px;`)

---

### 2.2 📦 컨테이너 시스템 (Container System)

모든 활동 영역은 **명확한 시각적 경계**를 가집니다.

#### 외부 컨테이너 (Outer Container)
```css
.activity-container {
  background: var(--section-bg);     /* 섹션별 연한 배경색 */
  border-radius: 16px;
  padding: 24px;
  margin: 16px 0;
}
```

#### 내부 작성 영역 (Inner Writing Area)
```css
.writing-area {
  background: #FFFFFF;
  border: 2px solid #333333;         /* 굵은 검정 테두리 — 핵심 특징 */
  border-radius: 8px;
  padding: 16px;
  min-height: 120px;
}
```

**관찰된 배경색 팔레트:**

| 용도 | 배경색 | CSS Variable |
|------|------|-------------|
| 노트 정리 | `#FFF8E7` (크림) | `--bg-cream` |
| 생각 톡톡 | `#FFE4E8` (핑크) | `--bg-pink` |
| AI CLASS | `#E3F2FD` (라이트블루) | `--bg-lightblue` |
| 학습지 | `#E8F5E9` (라이트그린) | `--bg-lightgreen` |
| 참고 자료 | `#F5F5F5` (연회색) | `--bg-gray` |
| 학습 정리 | `#E3F2FD` (아이스블루) | `--bg-iceblue` |

> [!IMPORTANT]
> **테두리 스타일이 핵심 정체성입니다.** Numbers 활동의 학생 작성 영역은 반드시 **2px 이상의 검정 실선 테두리**(`border: 2px solid #333`)를 사용합니다. 이것이 "디지털 학습지" 느낌을 만드는 가장 중요한 요소입니다. 가는 회색 테두리(`1px solid #ccc`)를 사용하면 원본의 감성이 살지 않습니다.

---

### 2.3 🎨 컬러 시스템 (Color System)

#### 라벨/해더 컬러 (Color-Coded Labels)

각 카드/섹션의 상단 라벨은 **부드러운 파스텔 톤**을 사용하며, 서로 구별 가능한 **색상 코드**를 부여합니다.

```css
:root {
  /* 라벨 배경 색상 — 파스텔 톤 */
  --label-purple:  #C5B3E6;  /* 정의, 예 */
  --label-pink:    #F4A5B8;  /* 성찰, 어떤 생각 */
  --label-green:   #A8E6A3;  /* 궁금, 연결 */
  --label-blue:    #7EC8E3;  /* 기능, 형태 */
  --label-coral:   #F5A89A;  /* 책임, 성질 */
  --label-yellow:  #FFE082;  /* 원인, 변화 */
  --label-mint:    #80F0D0;  /* 중앙 주제 (민트/터콰이즈) */

  /* 텍스트 색상 */
  --text-primary:  #333333;
  --text-label:    #FFFFFF;  /* 라벨 위 흰색 텍스트 */
}
```

> [!TIP]
> **색상 대비 규칙:** 라벨 배경은 충분히 채도가 있어야 하며, 그 위의 텍스트는 반드시 **흰색 또는 매우 진한 색**이어야 합니다. Numbers 원본에서 라벨 텍스트는 항상 **볼드 + 센터 정렬 + 흰색**입니다.

---

### 2.4 📏 레이아웃 그리드 시스템 (Layout Grid)

Numbers 활동의 레이아웃은 크게 **5가지 패턴**으로 분류됩니다.

#### 패턴 A: N-컬럼 균등 분할 (Equal Column Split)
```
┌──────────┬──────────┬──────────┐
│  컬럼 1   │  컬럼 2   │  컬럼 3   │
│ (라벨A)   │ (라벨B)   │ (라벨C)   │
│          │          │          │
│  작성영역  │  작성영역  │  작성영역  │
│          │          │          │
└──────────┴──────────┴──────────┘
```
- **사용 예:** 보이다-생각-궁금 (3컬럼), 형태-기능-원인 (3컬럼)
- **CSS:** `display: grid; grid-template-columns: repeat(N, 1fr); gap: 12px;`
- **특징:** 각 컬럼 상단에 **둥근 파스텔 컬러 라벨**, 하단은 **흰색 작성 영역**

#### 패턴 B: 사분면 + 중앙 허브 (Quadrant + Central Hub)
```
┌────────┬────────┐
│  LT    │  RT    │
│        │        │
├───┬────┴────┬───┤
│   │ 중앙주제 │   │
├───┴────┬────┴───┤
│  LB    │  RB    │
│        │        │
└────────┴────────┘
```
- **사용 예:** 프레이어 모델, 개념 은행+결합하기
- **CSS:** `display: grid; grid-template: repeat(2, 1fr) / repeat(2, 1fr);` + 중앙 absolute positioned element
- **특징:** 4개 사분면 + 정중앙에 주제 박스 (컬러 라벨 + 볼드 텍스트)

#### 패턴 C: 좌우 비대칭 분할 (Asymmetric Split)
```
┌───────┬──────────────┐
│       │              │
│ 좌측  │    우측       │
│(리스트)│  (그래픽)     │
│       │              │
└───────┴──────────────┘
```
- **사용 예:** 개념 은행 + 결합하기, 배움 노트 + 질문의 종류
- **CSS:** `display: grid; grid-template-columns: 1fr 2fr;` (또는 비율 조절)

#### 패턴 D: 수평 스펙트럼 (Horizontal Spectrum)
```
부정적 ◄───────────────────────► 긍정적
         ┌─────────────┐
         │  의견 입력란  │
         └─────────────┘
  🟦 🟪 🟩 🟧 🩷  (포스트잇 도구)
```
- **사용 예:** 감정/의견 스펙트럼
- **CSS:** 양극 라벨 + 중앙 작성 영역 + 하단 포스트잇 팔레트

#### 패턴 E: 세로 스택 (Vertical Stack)
```
┌──────────────────────────────┐
│  지시문 / 설명                │
├──────────────────────────────┤
│  이미지 / 영상 썸네일          │
├──────────────────────────────┤
│  작성 영역 (3-컬럼 등)        │
└──────────────────────────────┘
```
- **사용 예:** 생각 톡톡, 활동지
- **CSS:** `display: flex; flex-direction: column; gap: 16px;`

---

### 2.5 ✍️ 학생 입력 영역 원칙 (Student Input Area Principles)

학생이 직접 작성하는 영역은 활동의 핵심이며, 다음 원칙을 반드시 지킵니다.

#### 줄 간격 노트 (Lined Note)
```css
.lined-input {
  background: repeating-linear-gradient(
    transparent, transparent 27px, #CCCCCC 27px, #CCCCCC 28px
  );
  line-height: 28px;
  min-height: 200px;
  border: none;
  width: 100%;
  font-size: 16px;
}
```

#### 자유 작성 영역 (Free Writing Box)
```css
.free-writing {
  background: #FFFFFF;
  border: 2px solid #333333;
  border-radius: 8px;
  min-height: 150px;
  padding: 12px;
}
```

#### 인라인 답변 줄 (Inline Answer Line)
```css
.answer-line {
  border-bottom: 1.5px solid #333333;
  min-width: 200px;
  display: inline-block;
  padding: 4px 0;
}
```

> [!IMPORTANT]
> **입력 영역의 크기가 충분해야 합니다.** Numbers에서 학생들은 터치로 타이핑하므로, `min-height`를 넉넉하게 잡아야 합니다. 일반 작성 영역은 최소 `150px`, 메인 작성 영역은 최소 `250px`을 확보합니다.

---

### 2.6 🖼️ 미디어 영역 원칙 (Media Area Principles)

#### 영상 썸네일 (Video Thumbnail)
```css
.video-thumbnail {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  max-width: 100%;
  aspect-ratio: 16/9;
}
```

#### 이미지 갤러리 (Image Gallery)
```css
.image-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.gallery-item {
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 4px rgba(0,0,0,0.12);
}
```

#### 참고 자료 카드 (Reference Card)
```css
.reference-card {
  display: flex;
  gap: 16px;
  background: #F5F5F5;
  border-radius: 12px;
  padding: 16px;
  align-items: stretch;
}
```

---

### 2.7 🔗 인터랙티브 요소 (Interactive Elements)

#### 링크/버튼 (Link Button)
```css
.activity-link-button {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(135deg, #2196F3, #1976D2);
  color: white;
  border-radius: 12px;
  padding: 12px 20px;
  font-weight: 700;
  font-size: 18px;
  text-decoration: none;
  box-shadow: 0 2px 8px rgba(33,150,243,0.3);
}
```
- **사용 예:** "지니아튜터" 버튼 (AI CLASS 섹션)
- **특징:** 둥근 모서리, 그라데이션 배경, 아이콘(🔗) + 텍스트 + 화살표(➡️)

#### 포스트잇 (Post-it Notes)
```css
.postit {
  width: 60px;
  height: 60px;
  border-radius: 2px;
  box-shadow: 2px 2px 4px rgba(0,0,0,0.2);
  transform: rotate(-2deg);
  cursor: grab;
}

.postit--blue    { background: #81D4FA; }
.postit--purple  { background: #CE93D8; }
.postit--green   { background: #C5E1A5; }
.postit--orange  { background: #FFCC80; }
.postit--pink    { background: #F48FB1; }
```

---

## 3. 활동 유형별 HTML 구조 템플릿

### 3.1 보이다-생각-궁금 (See-Think-Wonder)

```html
<section class="activity-container" style="--section-bg: #FFE4E8;">
  <div class="activity-badges">
    <span class="activity-badge" style="--badge-color: #FF6B8A;">💡 생각 톡톡</span>
    <span class="activity-badge" style="--badge-color: #4CAF50;">📊 Numbers 앱 활동</span>
  </div>
  <p class="activity-instruction">영상을 보고 아래의 표를 채워봅시다.</p>
  
  <div class="media-area">
    <img class="video-thumbnail" src="thumbnail.jpg" alt="영상 썸네일">
  </div>
  
  <div class="column-grid columns-3">
    <div class="column-card">
      <div class="column-label" style="--label-color: #C5B3E6;">무엇이 보이나요?</div>
      <div class="writing-area"></div>
    </div>
    <div class="column-card">
      <div class="column-label" style="--label-color: #F4A5B8;">어떤 생각이 드나요?</div>
      <div class="writing-area"></div>
    </div>
    <div class="column-card">
      <div class="column-label" style="--label-color: #A8E6A3;">무엇이 궁금한가요?</div>
      <div class="writing-area"></div>
    </div>
  </div>
</section>
```

### 3.2 프레이어 모델 (Frayer Model)

```html
<section class="activity-container" style="--section-bg: #FFFFFF;">
  <div class="frayer-model">
    <div class="frayer-quadrant frayer-tl">
      <div class="quadrant-label" style="--label-color: #F4A5B8;">정의</div>
      <div class="writing-area"></div>
    </div>
    <div class="frayer-quadrant frayer-tr">
      <div class="quadrant-label" style="--label-color: #7EC8E3;">성질/특성</div>
      <div class="writing-area"></div>
    </div>
    <div class="frayer-center">
      <span class="center-topic">주제</span>
    </div>
    <div class="frayer-quadrant frayer-bl">
      <div class="quadrant-label" style="--label-color: #C5B3E6;">예</div>
      <div class="writing-area"></div>
    </div>
    <div class="frayer-quadrant frayer-br">
      <div class="quadrant-label" style="--label-color: #F5A89A;">예가 아닌 것</div>
      <div class="writing-area"></div>
    </div>
  </div>
</section>
```

### 3.3 개념 은행 + 결합하기 (Concept Bank + Combine)

```html
<section class="activity-container" style="--section-bg: #E3F2FD;">
  <span class="activity-badge" style="--badge-color: #90CAF9;">📑 학습 정리</span>
  
  <div class="split-layout">
    <div class="concept-bank">
      <div class="section-header" style="--header-color: #1976D2;">개념 은행</div>
      <div class="writing-area tall"></div>
    </div>
    <div class="combine-area">
      <div class="section-header" style="--header-color: #1976D2;">결합하기</div>
      <div class="frayer-model">
        <!-- 4사분면 + 중앙 주제 (터콰이즈) -->
        <div class="frayer-quadrant">
          <p class="quadrant-prompt">내가 생각하는 [주제]은</p>
          <div class="writing-area"></div>
        </div>
        <!-- ... 나머지 사분면 ... -->
        <div class="frayer-center" style="background: #80F0D0;">
          <span class="center-topic">[주제란]?</span>
        </div>
      </div>
    </div>
  </div>
</section>
```

### 3.4 배움 노트 (Learning Note)

```html
<section class="activity-container" style="--section-bg: #FFF8E7;">
  <span class="activity-badge" style="--badge-color: #F5C842;">📝 노트 정리</span>
  
  <div class="learning-note">
    <div class="note-header">
      <h2>배움 노트</h2>
      <p class="note-subtitle">학습 내용 정리하기</p>
      <div class="note-date">오늘의 날짜: <span class="answer-line"></span></div>
    </div>
    
    <div class="note-meta">
      <div class="meta-row">단원명 <span class="answer-line wide"></span></div>
      <div class="meta-row">학습문제 <span class="answer-line wide"></span></div>
    </div>
    
    <div class="lined-input" contenteditable="true"></div>
    
    <div class="note-footer">
      <div class="footer-row">
        <span>오늘 내용 요약</span>
        <span>메모</span>
      </div>
      <div class="footer-content">
        <div class="writing-area"></div>
        <div class="writing-area"></div>
      </div>
      <div class="footer-question">
        궁금한 것, 질문 <span class="answer-line wide"></span>
      </div>
    </div>
  </div>
</section>
```

### 3.5 감정/의견 스펙트럼 (Spectrum)

```html
<section class="activity-container" style="--section-bg: #FFFFFF;">
  <div class="spectrum-activity">
    <div class="spectrum-area">
      <!-- 넓은 자유 작성 영역 -->
      <div class="writing-area tall"></div>
    </div>
    
    <div class="spectrum-line">
      <span class="spectrum-label left">부정적</span>
      <div class="spectrum-bar"></div>
      <span class="spectrum-label right">긍정적</span>
    </div>
    
    <div class="spectrum-input">
      <div class="writing-area" style="background: #F5E0DC;"></div>
    </div>
    
    <div class="postit-palette">
      <p class="palette-instruction">포스트잇으로 활용하세요.</p>
      <div class="postit-row">
        <div class="postit postit--blue"></div>
        <div class="postit postit--purple"></div>
        <div class="postit postit--green"></div>
        <div class="postit postit--orange"></div>
        <div class="postit postit--pink"></div>
      </div>
    </div>
  </div>
</section>
```

### 3.6 AI CLASS (지니아튜터)

```html
<section class="activity-container" style="--section-bg: #E3F2FD;">
  <span class="activity-badge" style="--badge-color: #2196F3;">🤖 AI CLASS</span>
  
  <a href="#" class="activity-link-button">
    🔗 지니아튜터 <span class="link-arrow">➡️</span>
  </a>
  
  <div class="writing-area tall">
    <p class="placeholder-text">지니아 튜터 결과 캡처해서 넣기</p>
  </div>
</section>
```

### 3.7 참고 자료 (Reference Materials)

```html
<section class="activity-container" style="--section-bg: #F5F5F5;">
  <span class="activity-badge" style="--badge-color: #FF9800;">🔴 참고 자료</span>
  
  <div class="reference-grid">
    <div class="reference-card">
      <img src="ref1.jpg" alt="참고 자료 1" class="reference-image">
    </div>
    <div class="reference-card">
      <img src="ref2.jpg" alt="참고 자료 2" class="reference-image">
    </div>
  </div>
</section>
```

### 3.8 활동지 (Worksheet)

```html
<section class="activity-container" style="--section-bg: #F3E5F5;">
  <span class="activity-badge" style="--badge-color: #FF7043;">📋 활동지</span>
  
  <div class="worksheet-spread">
    <div class="worksheet-page">
      <div class="worksheet-header">
        <span class="textbook-badge">교과서 활동지</span>
        <h3>활동 제목</h3>
        <div class="student-info">| 6학년 <span class="answer-line"></span> 반 이름: <span class="answer-line"></span></div>
      </div>
      
      <p class="instruction">● 다음 사진 자료를 보고, 물음에 답해 봅시다.</p>
      
      <div class="image-gallery">
        <!-- 이미지 그리드 -->
      </div>
      
      <div class="question-list">
        <div class="question">
          <span class="q-number">1</span>
          <span class="q-text">질문 내용</span>
          <div class="answer-line wide"></div>
        </div>
      </div>
    </div>
  </div>
</section>
```

### 3.9 학습지 / 확인 문제 (Assessment)

```html
<section class="activity-container" style="--section-bg: #E3F2FD;">
  <span class="activity-badge" style="--badge-color: #42A5F5;">📝 학습지</span>
  
  <div class="assessment-layout">
    <div class="assessment-sheet">
      <div class="assessment-header">
        <span class="check-badge">확인 문제</span>
        <div class="topic-info">단원명 / 차시</div>
        <div class="student-info">학년 반 번 이름 <span class="answer-line"></span></div>
      </div>
      
      <div class="question-section">
        <div class="question ox-question">
          <span class="q-number">1.</span>
          <p class="q-text">다음 설명을 읽고 옳으면 ○표, 옳지 않으면 X표를 하시오.</p>
          <div class="sub-questions">
            <div class="sub-q">(1) 설명 내용 <span class="answer-circle">( )</span></div>
          </div>
        </div>
        
        <div class="question matching-question">
          <span class="q-number">3.</span>
          <p class="q-text">알맞게 선으로 연결하시오.</p>
          <div class="matching-grid">
            <!-- 좌: 용어, 중: 설명, 우: 이미지 -->
          </div>
        </div>
      </div>
    </div>
    
    <div class="answer-key">
      <h3>답지</h3>
    </div>
  </div>
</section>
```

---

## 4. 타이포그래피 원칙 (Typography Principles)

```css
:root {
  /* 폰트 패밀리 */
  --font-primary: 'Pretendard', 'Apple SD Gothic Neo', sans-serif;
  --font-handwriting: 'Nanum Pen Script', cursive;  /* 학생 손글씨 느낌 */

  /* 폰트 크기 체계 */
  --fs-badge: 14px;           /* 배지 텍스트 */
  --fs-section-title: 24px;   /* 섹션 대제목 */
  --fs-label: 16px;           /* 컬럼/사분면 라벨 */
  --fs-instruction: 15px;     /* 지시문 */
  --fs-body: 16px;            /* 본문/작성 텍스트 */
  --fs-meta: 13px;            /* 학년 반 이름 등 메타 정보 */

  /* 폰트 굵기 */
  --fw-badge: 700;
  --fw-title: 800;
  --fw-label: 700;
  --fw-instruction: 500;
  --fw-body: 400;
}
```

**핵심 규칙:**
- **라벨 텍스트**는 항상 **볼드 + 센터 정렬**
- **지시문**(●로 시작)은 **중간 굵기 + 좌정렬**
- **번호 있는 질문**의 번호는 **볼드 + 컬러(주로 빨강/파랑)**
- **플레이스홀더 텍스트**는 **연한 회색 + 이탤릭** 또는 빨간 밑줄

---

## 5. 간격과 여백 원칙 (Spacing Principles)

```css
:root {
  /* 활동 간 간격 */
  --gap-between-activities: 32px;

  /* 컨테이너 내부 패딩 */
  --padding-container: 24px;

  /* 그리드 컬럼 간격 */
  --gap-columns: 12px;

  /* 라벨-작성영역 간격 */
  --gap-label-to-area: 8px;

  /* 미디어-작성영역 간격 */
  --gap-media-to-area: 16px;
}
```

> [!TIP]
> Numbers에서의 활동은 iPad 화면에 최적화되어 있습니다. HTML 변환 시 **최소 너비 768px** (iPad portrait)을 기준으로 디자인하고, 데스크톱에서는 **max-width: 1024px**로 제한하여 가독성을 유지합니다.

---

## 6. 반응형 디자인 원칙 (Responsive Design)

```css
/* iPad 세로 모드 기준 (기본) */
.column-grid.columns-3 {
  grid-template-columns: repeat(3, 1fr);
}

/* 작은 모바일 화면 */
@media (max-width: 600px) {
  .column-grid.columns-3 {
    grid-template-columns: 1fr;
  }
  
  .split-layout {
    grid-template-columns: 1fr;
  }
  
  .frayer-model {
    grid-template-columns: 1fr;
  }
}
```

---

## 7. 접근성 원칙 (Accessibility)

- 모든 `contenteditable` 영역에 `aria-label` 부여
- 컬러 라벨은 색상만으로 구분하지 않고, **텍스트 라벨**을 항상 병행
- 최소 터치 영역 `44px × 44px` (Apple HIG 기준)
- 포커스 시 `outline: 3px solid #2196F3` 적용

---

## 8. CSS 변수 통합 정리 (Complete CSS Variables)

```css
:root {
  /* === 배지 컬러 === */
  --badge-note:      #F5C842;
  --badge-thinking:  #FF6B8A;
  --badge-numbers:   #4CAF50;
  --badge-reference: #FF9800;
  --badge-ai:        #2196F3;
  --badge-worksheet: #FF7043;
  --badge-assessment:#42A5F5;
  --badge-review:    #90CAF9;

  /* === 섹션 배경색 === */
  --bg-cream:      #FFF8E7;
  --bg-pink:       #FFE4E8;
  --bg-lightblue:  #E3F2FD;
  --bg-lightgreen: #E8F5E9;
  --bg-gray:       #F5F5F5;
  --bg-iceblue:    #E3F2FD;
  --bg-lavender:   #F3E5F5;

  /* === 라벨 컬러 === */
  --label-purple:  #C5B3E6;
  --label-pink:    #F4A5B8;
  --label-green:   #A8E6A3;
  --label-blue:    #7EC8E3;
  --label-coral:   #F5A89A;
  --label-yellow:  #FFE082;
  --label-mint:    #80F0D0;

  /* === 테두리 === */
  --border-writing: 2px solid #333333;
  --border-light:   1px solid #E0E0E0;
  --border-radius-card: 8px;
  --border-radius-badge: 20px;
  --border-radius-container: 16px;

  /* === 그림자 === */
  --shadow-card:  0 1px 4px rgba(0,0,0,0.12);
  --shadow-media: 0 2px 8px rgba(0,0,0,0.15);
  --shadow-button: 0 2px 8px rgba(33,150,243,0.3);

  /* === 간격 === */
  --gap-activities: 32px;
  --padding-container: 24px;
  --gap-columns: 12px;
  --gap-label-area: 8px;
  --gap-media-area: 16px;

  /* === 타이포그래피 === */
  --font-primary: 'Pretendard', 'Apple SD Gothic Neo', sans-serif;
}
```

---

## 9. 체크리스트: HTML 활동 디자인 시 확인 사항

- [ ] 섹션 배지가 활동 유형에 맞는 색상과 아이콘을 사용하는가?
- [ ] 외부 컨테이너에 연한 배경색이 적용되었는가?
- [ ] 학생 작성 영역에 **2px 검정 테두리**가 적용되었는가?
- [ ] 컬럼 라벨이 **파스텔 배경 + 흰색 볼드 텍스트**인가?
- [ ] 작성 영역의 최소 높이가 충분한가? (150px 이상)
- [ ] 지시문에 ● 기호가 포함되어 있는가?
- [ ] 반응형 breakpoint가 적용되었는가? (768px → 600px)
- [ ] 필요한 미디어 영역에 적절한 rounded corner와 shadow가 있는가?
- [ ] 포스트잇, 링크 버튼 등 인터랙티브 요소가 충분히 큰가? (44px 이상)
- [ ] CSS Variable을 활용하여 일관성을 유지하고 있는가?

---

## 10. 참고 이미지 (Reference Screenshots)

아래는 분석에 사용된 원본 활동 스크린샷입니다.

| # | 유형 | 파일명 |
|---|------|--------|
| 1 | 배움 노트 + 질문의 종류 | `스크린샷 2026-03-20 오전 9.11.53.png` |
| 2 | 프레이어 모델 | `스크린샷 2026-03-20 오전 9.12.01.png` |
| 3 | 보이다-생각-궁금 | `스크린샷 2026-03-20 오전 9.12.07.png` |
| 4 | 개념 은행 + 결합하기 | `스크린샷 2026-03-20 오전 9.12.12.png` |
| 5 | 감정/의견 스펙트럼 | `스크린샷 2026-03-20 오전 9.12.19.png` |
| 6 | 참고 자료 | `스크린샷 2026-03-20 오전 9.12.44.png` |
| 7 | AI CLASS | `스크린샷 2026-03-20 오전 9.12.52.png` |
| 8 | 생각 톡톡 | `스크린샷 2026-03-20 오전 9.12.59.png` |
| 9 | 활동지 | `스크린샷 2026-03-20 오전 9.13.15.png` |
| 10 | 학습지 | `스크린샷 2026-03-20 오전 9.13.20.png` |
| 11 | 학습 정리 (개념 은행 확장) | `스크린샷 2026-03-20 오전 9.13.35.png` |
