# Runtime Agent Spec: lesson_analysis_agent

아래 AGENT.md는 이 단계의 역할과 경계를 정의한다.
문서에 적힌 역할만 수행하고, 하지 말아야 할 일은 넘지 마라.
출력 형식 요구가 있으면 반드시 지켜라.

# lesson_analysis_agent

## identity
- status: active
- layer: generation
- implementation: `scripts/lesson_analysis_agent.py`

## responsibility
- 차시별 lesson analysis를 생성한다.
- 생성 결과를 정규화해 최종 `lesson_analysis.json`으로 확정한다.

## inputs
- required:
  - `source/schedule_draft.json`
  - `source/textbook_context.json`
- optional:
  - `source/local_baseline/<lesson>.lesson_analysis.json`

## outputs
- `sections/<lesson>/lesson_analysis.context.json`
- `sections/<lesson>/lesson_analysis.prompt.md`
- `sections/<lesson>/lesson_analysis_ai.json`
- `sections/<lesson>/lesson_analysis.json`
- `sections/<lesson>/lesson_analysis.status.json`

## allowed_tools
- local:
  - prompt/context assembly
  - JSON normalization
- model:
  - Gemini CLI

## allowed_actions
- lesson별 prompt 구성
- lesson analysis 생성
- baseline fallback 사용
- lesson 단위 병렬 실행

## forbidden_actions
- source 경계 수정
- activity 생성
- render/output 조작

## rules
- lesson semantic analysis generation은 반드시 이 Agent를 통해서만 수행한다.

## hook_contract
- trigger_if_missing:
  - `sections/<lesson>/lesson_analysis.json`
- unlocks:
  - `lesson_review_agent`
  - `activity_plan_agent`

## success_criteria
- 각 lesson에 `lesson_analysis.json`이 생성된다.
- lesson별 status file이 존재한다.

## failure_modes
- Gemini timeout
- AI JSON 생성 실패
- normalization 실패
- baseline fallback 사용


# Execution Task

You are helping a local textbook-to-Numbers pipeline.

Rules:
- Ignore progress-chart page numbers entirely.
- Treat the textbook PDF as the primary source of truth.
- Do not invent page boundaries.
- Return JSON only.
- Do not include markdown fences.
- Do not include fields outside the provided schema unless they already appear in the baseline object.
- If a value is uncertain, keep the baseline value or explain uncertainty in `notes`.
- Keep `review_status` as `draft`.
- Keep the output grounded in the supplied section context only.
- Do not infer details from other lessons unless they are explicitly included as neighboring boundary hints.


Generate one `lesson_analysis` JSON object for the section below.

Section:
{
  "sheet_name": "2-3차시",
  "card_file": "___2-3차시",
  "title": "지구본과 지도로 보는 세계 — 지구본의 특징 살펴보기",
  "badge": "2-3차시",
  "pdf_pages": [
    112,
    113,
    114,
    115
  ],
  "textbook_source": {
    "resource_id": "main",
    "title_query": "지구본과 지도로 보는 세계 — 지구본의 특징 살펴보기",
    "start_page": 112,
    "end_page": 115,
    "confidence": 0.55,
    "status": "matched"
  }
}

Baseline lesson analysis:
{
  "lesson_id": "2-3차시",
  "sheet_name": "2-3차시",
  "lesson_title": "지구본과 지도로 보는 세계 — 지구본의 특징 살펴보기",
  "lesson_type": "core",
  "pdf_pages": [
    112,
    113,
    114,
    115
  ],
  "essential_question": "지구본과 지도로 보는 세계 — 지구본의 특징 살펴보기",
  "learning_goals": [
    "지구본과 지도로 보는 세계 — 지구본의 특징 살펴보기의 핵심 내용을 설명할 수 있다."
  ],
  "key_concepts": [
    "지구본",
    "지도",
    "보는",
    "세계",
    "특징"
  ],
  "vocabulary": [
    "지구본",
    "지도",
    "보는"
  ],
  "misconceptions": [],
  "difficulty_band": "on-level",
  "content_chunks": [
    {
      "chunk_id": "2-3차시-chunk-1",
      "label": "학습 덩어리 1",
      "knowledge_type": "comparison",
      "summary": "지구본 지구본은 지구의 모습을 본떠 작게 나타낸 모형이다.",
      "source_pages": [
        112,
        113
      ]
    },
    {
      "chunk_id": "2-3차시-chunk-2",
      "label": "학습 덩어리 2",
      "knowledge_type": "procedure",
      "summary": "정보 활용 능력 1 \u0007지구본과 세계지도에서 남극 대륙을 찾아보고, 그 모양을 그려 봅시다.",
      "source_pages": [
        114,
        115
      ]
    }
  ],
  "source_page_refs": [
    112,
    113,
    114,
    115
  ],
  "analysis_confidence": 0.75,
  "notes": "자동 생성 초안. lesson title, key concepts, chunks를 검토 후 승인 필요."
}

Schedule draft:
{
  "schema_version": "1.0.0",
  "generated_at": "2026-03-30T15:20:26.092351+00:00",
  "sections": [
    {
      "sheet_name": "1차시",
      "lesson_title": "3단원 도입 — [단원 도입] 우리 친구는 누구?",
      "title_query": "3단원 도입 — [단원 도입] 우리 친구는 누구?"
    },
    {
      "sheet_name": "2-3차시",
      "lesson_title": "지구본과 지도로 보는 세계 — 지구본의 특징 살펴보기",
      "title_query": "지구본과 지도로 보는 세계 — 지구본의 특징 살펴보기"
    },
    {
      "sheet_name": "4차시",
      "lesson_title": "지구본과 지도로 보는 세계 — 디지털 공간 영상 정보의 의미 알아보기",
      "title_query": "지구본과 지도로 보는 세계 — 디지털 공간 영상 정보의 의미 알아보기"
    }
  ]
}

Section context:
{
  "schema_version": "1.0.0",
  "generated_at": "2026-03-30T15:34:26.371931+00:00",
  "pdf_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/textbook/사회/[사회]6_1_교과서.pdf",
  "current_section": {
    "section_key": "___2-3차시__지구본과_지도로_보는_세계___지구본의_특징_살펴보기",
    "sheet_name": "2-3차시",
    "lesson_title": "지구본과 지도로 보는 세계 — 지구본의 특징 살펴보기",
    "title_query": "지구본과 지도로 보는 세계 — 지구본의 특징 살펴보기",
    "pdf_pages": [
      112,
      113,
      114,
      115
    ],
    "baseline_analysis_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/artifacts/runs/1-20260331-002018/source/local_baseline/___2-3차시__지구본과_지도로_보는_세계___지구본의_특징_살펴보기.lesson_analysis.json",
    "extracted_text": "지구본\n지구본은 지구의 모습을 본떠 작게 나타낸 모형이다. 지구본은 지구의 \n실제 모습과 비슷해서 세계 여러 나라의 위치, 거리, 영토 모양 등을 비교적 \n정확하게 표현할 수 있다. 하지만 전 세계의 모습을 한눈에 살펴보기 어렵고, \n가지고 다니기에도 불편하다.\n세계를 어떻게 살펴볼 수 있을까요?\n하나\n내 장래 희망은 비행기 조종사야. 그래서 나는 비행경로가 표시된 지도를 보는 \n걸 좋아해. 그런데 내가 본 지도에서는 비행경로를 직선이 아닌 곡선으로 표시하더라고. 직선\n으로 가면 더 빠를 텐데, 왜 곡선으로 표시하는 걸까?\n생각 깨우기\n60°\n90°\n30°\n0°\n30°\n구경: 320 mm\n축척: 1:40,000,000\n60°\n90°\n30°\n0°\n30°\n인 도 양\n북극해\n대서양\n동해\n60°\n60°\n90°\n90°\n120°\n150°\n150°\n180°\n30°\n30°\n0°\n60°\n60°\n90°\n90°\n120°\n150°\n150°\n180°\n30°\n30°\n0°\n지구본을 살펴보고\n특징을 이야기해 볼까?\n애니메이션\n112\n3 지구, 대륙 그리고 국가들\n\n세계지도\n세계지도는 둥근 지구를 축소해 평면으로 표현한 것이다. 그래서 세계 \n여러 나라의 위치와 영역을 한눈에 살펴볼 수 있다. 하지만 둥근 지구를 \n평면으로 나타냈기 때문에 영토 모양이나 면적, 거리 등이 실제와 다르게 \n표현된다. \n동해\n미국\n브라질\n필리핀\n칠레\n페루\n이집트\n알제리\n말리\n차드수단\n사우디\n아라비아\n튀르키예\n타이\n타이\n카자흐스탄\n아르헨티나\n멕시코\n인도네시아\n독일\n프랑스\n마다가스카르 \n탄자니아\n앙골라\n남아프리카 \n공화국\n에스파냐\n영국\n스웨덴\n대한민국\n일본\n이란\n뉴질랜드\n인도\n오스트레일리아\n몽골\n러 시 아\n중국\n캐 나 다\n아르헨티나\n멕시코\n인도네시아\n독일\n프랑스\n마다가스카르 \n탄자니아\n앙골라\n남아프리카 \n공화국\n에스파냐\n영국\n스웨덴\n대한민국\n일본\n인도양\n대서양 \n대서양 \n태평양  \n북극해\n남극해\n이집트사우디\n아라비아\n튀르키예\n카자흐스탄\n페루\n알제리\n말리\n차드수단\n칠레\n150°\n0°\n60°\n60°\n30°\n30°\n0°\n30°\n60°\n60° 30°\n90°\n90°\n120°\n120°\n150°\n180°\n150°\n0°\n30°\n60°\n60° 30°\n90°\n90°\n120°\n120°\n150°\n180°\n0°\n30°\n60°\n60°\n30°\n0\n2,000km\n적도\n적도\n동해\n실제 면적보다 \n넓게 표현된 곳이 \n생겼어.\n ‌\u0007둥근 지구 표면을 일정한 크기로 잘라 \n펼치면 빈 곳이 생긴다. 그래서 육지와 \n바다의 빈 곳을 이어 평면에 나타내면 \n세계지도가 실제와 다르게 표현된다.\n세계\n지도가 \n실제와 다\n르게 표현\n되는 까\n닭\n지도의 빈 곳을\n채워 지도를\n만들어 볼까?\n113\n1   지구본과 지도로 보는 세계\n\n정보 활용 능력\n1 \u0007지구본과 세계지도에서 남극 대륙을 찾아보고, 그 모양을 그려 봅시다.\n지구본과 세계지도의 특징 알아보기\n스스로\n해 보기\n2 \u0007지구본과 세계지도에서 표현된 남극 대륙의 모양과 면적이 서로 다른 까닭을 이야기해 봅시다.\n세계지도\n지구본\n1  서울에서 런던으로 가는 가장 짧은 이동 경로를 예상해 봅니다.\n2  ‌\u00071 에서 예상한 경로를 활동 자료10  에 빨간색 색연필로\n     표시합니다.\n3  ‌\u0007끈을 팽팽하게 당긴 상태에서 서울과 런던을\n     동시에 지나도록 지구본 위에 올립니다.\n4  ‌\u00073 에서 확인한 경로를 활동 자료10  에 파란색 \n색연필로 표시합니다. \n5  ‌\u0007활동 자료10  에 표시한 두 가지 경로를 비교\n해 보고 알게 된 점을 이야기합니다. \n활\n방\n동\n법\n3 \u0007대한민국 서울에서 영국 런던까지 가장 짧은 이동 경로를 찾아봅시다.\n지구본, 활동 자료10  , 색연필(빨간색, 파란색), 끈\n준비물\n지구본과 세계지도를 활용해 \nㅅ\nㄱ\n 의 모습을 살펴볼 수 있다.\n한 문장 정리\n끈은 이동 \n경로를 보여 주는 \n역할을 해.\n배움 확인\n114\n3 지구, 대륙 그리고 국가들\n\n만약 물고기가 세계지도를 그린다면 어떤 모습일까? 미국의 \n아델스탄 스필하우스(Athelstan F. Spilhaus)라는 학자는 물고기가 \n지도를 그린다고 상상하며 독특한 세계지도를 만들었다. 이 지도의 \n중심에는 남극 대륙이 있고, 바다가 지도의 대부분을 차지한다. 또한 \n땅은 지도의 가장자리에 조금 그려져 있어, 바다가 지구의 중심처럼 \n느껴지도록 표현했다. \n우리나라에서 흔히 보는 지도는 우리나라가 중앙에 있다. 미국에서 \n흔히 사용하는 지도는 미국이 중앙에 있고, 영국에서는 영국이 중앙에 \n있는 지도를 사용한다. \t \n국제연합(UN)의 깃발은 북극에서 \t\n내려다본 지구의 모습을 \t\n나타낸다. 이처럼 세계\t \n지도는 둥근 지구를 평면\n으로 표현하는 과정에서 \n무엇을 중점으로  \n표현하느냐에 따라 \t\n다양하게 표현된다. \n세상을 다른 각도로!\n         독특한 세계지도가 알려 주는 것들\n다양한 형태의 세계지도를 더 찾아봅시다.\n우\n사이\n리\n들\n \n우\n리\n가\n \n들\n려\n주\n는\n \n사\n회\n \n이\n야\n기\n태 평 양\n대서양\n인도양\n남극해\n북극해\n동해\n 물고기의 관점에서 그린 세계지도\n 북극을 중심으로 그린 국제연합 깃발\n115\n1   지구본과 지도로 보는 세계",
    "extracted_text_truncated": false
  },
  "neighbor_sections": [
    {
      "relation": "previous",
      "section_key": "___1차시__3단원_도입____단원_도입__우리_친구는_누구_",
      "sheet_name": "1차시",
      "lesson_title": "3단원 도입 — [단원 도입] 우리 친구는 누구?",
      "title_query": "3단원 도입 — [단원 도입] 우리 친구는 누구?",
      "pdf_pages": [
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23,
        24,
        25,
        26,
        27,
        28,
        29,
        30,
        31,
        32,
        33,
        34,
        35,
        36,
        37,
        38,
        39,
        40,
        41,
        42,
        43,
        44,
        45,
        46,
        47,
        48,
        49,
        50,
        51,
        52,
        53,
        54,
        55,
        56,
        57,
        58,
        59,
        60,
        61,
        62,
        63,
        64,
        65,
        66,
        67,
        68,
        69,
        70,
        71,
        72,
        73,
        74,
        75,
        76,
        77,
        78,
        79,
        80,
        81,
        82,
        83,
        84,
        85,
        86,
        87,
        88,
        89,
        90,
        91,
        92,
        93,
        94,
        95,
        96,
        97,
        98,
        99,
        100,
        101,
        102,
        103,
        104,
        105,
        106,
        107,
        108,
        109,
        110,
        111
      ]
    },
    {
      "relation": "next",
      "section_key": "___4차시__지구본과_지도로_보는_세계___디지털_공간_영상_정보의_의미_알아보기",
      "sheet_name": "4차시",
      "lesson_title": "지구본과 지도로 보는 세계 — 디지털 공간 영상 정보의 의미 알아보기",
      "title_query": "지구본과 지도로 보는 세계 — 디지털 공간 영상 정보의 의미 알아보기",
      "pdf_pages": [
        116
      ]
    }
  ]
}

Target schema:
{
  "required_root_fields": [
    "schema_version",
    "generated_at",
    "lesson_id",
    "sheet_name",
    "lesson_title",
    "pdf_pages",
    "essential_question",
    "learning_goals",
    "key_concepts",
    "vocabulary",
    "misconceptions",
    "content_chunks",
    "source_page_refs",
    "analysis_confidence"
  ],
  "optional_root_fields": [
    "lesson_type",
    "difficulty_band",
    "review_status",
    "notes"
  ],
  "lesson_type_enum": [
    "intro",
    "core",
    "review",
    "summary",
    "mixed"
  ],
  "difficulty_band_enum": [
    "core",
    "on-level",
    "extension",
    "mixed"
  ],
  "review_status_enum": [
    "draft",
    "reviewed",
    "approved",
    "rejected"
  ],
  "required_content_chunk_fields": [
    "chunk_id",
    "label",
    "content_type",
    "knowledge_type",
    "summary",
    "source_pages"
  ],
  "content_type_enum": [
    "text",
    "image",
    "diagram",
    "map",
    "activity",
    "summary",
    "mixed"
  ],
  "knowledge_type_enum": [
    "fact",
    "concept",
    "procedure",
    "comparison",
    "cause-effect",
    "opinion",
    "application",
    "mixed"
  ],
  "constraints": {
    "pdf_pages_min_items": 1,
    "learning_goals_min_items": 1,
    "key_concepts_min_items": 1,
    "content_chunks_min_items": 1,
    "source_page_refs_min_items": 1,
    "analysis_confidence_range": [
      0,
      1
    ],
    "additional_properties": false
  }
}

Requirements:
- Preserve `sheet_name`, `lesson_id`, `lesson_title`, and `pdf_pages`.
- Improve `essential_question`, `learning_goals`, `key_concepts`, `vocabulary`, `misconceptions`, and `content_chunks` if the context supports it.
- `content_chunks` must stay grounded in the supplied `pdf_pages`.
- `source_page_refs` must match the actual section pages.
- Use `current_section.extracted_text` as the primary evidence.
- Use `neighbor_sections` only to avoid crossing lesson boundaries.
- Keep the result concise and classroom-usable.
- Output a single JSON object only.
