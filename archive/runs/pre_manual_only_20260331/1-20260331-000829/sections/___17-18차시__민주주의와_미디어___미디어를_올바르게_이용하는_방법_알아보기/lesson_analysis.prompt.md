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
  "sheet_name": "17-18차시",
  "card_file": "___17-18차시",
  "title": "민주주의와 미디어 — 미디어를 올바르게 이용하는 방법 알아보기",
  "badge": "17-18차시",
  "accent": [
    "#6366f1",
    "#818cf8"
  ],
  "sources": [
    {
      "resource_id": "main",
      "role": "textbook",
      "title_query": "민주주의와 미디어 — 미디어를 올바르게 이용하는 방법 알아보기",
      "_inference": {
        "status": "matched",
        "start_page": 7,
        "end_page": 48,
        "start_query": "민주주의와 미디어 — 미디어를 올바르게 이용하는 방법 알아보기",
        "start_match_pages": [
          7,
          90,
          100,
          102,
          103
        ],
        "start_match_count": 5,
        "end_strategy": "boundary_decision_agent",
        "end_reference_query": null,
        "intro_boundary_page": null,
        "reason": "Transitional heuristic: choose highest-ranked candidate and cut before next lesson candidate",
        "confidence": 0.55
      },
      "pdf_pages": [
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
        48
      ]
    }
  ],
  "source_ranges": [
    {
      "resource_id": "main",
      "role": "textbook",
      "pdf_pages": [
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
        48
      ]
    }
  ],
  "pdf_pages": [
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
    48
  ]
}

Baseline lesson analysis:
{
  "lesson_id": "17-18차시",
  "sheet_name": "17-18차시",
  "lesson_title": "민주주의와 미디어 — 미디어를 올바르게 이용하는 방법 알아보기",
  "lesson_type": "core",
  "pdf_pages": [
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
    48
  ],
  "essential_question": "민주주의와 미디어 — 미디어를 올바르게 이용하는 방법 알아보기",
  "learning_goals": [
    "민주주의와 미디어 — 미디어를 올바르게 이용하는 방법 알아보기의 핵심 내용을 설명할 수 있다."
  ],
  "key_concepts": [
    "미디어",
    "올바르게",
    "이용하",
    "방법",
    "알아보기"
  ],
  "vocabulary": [
    "미디어",
    "올바르게",
    "이용하"
  ],
  "misconceptions": [
    "선거를 단순히 사람을 뽑는 행사로만 이해할 수 있다.",
    "민주주의의 핵심이 참여보다 결과에만 있다고 오해할 수 있다."
  ],
  "difficulty_band": "on-level",
  "content_chunks": [
    {
      "chunk_id": "17-18차시-chunk-1",
      "label": "학습 덩어리 1",
      "knowledge_type": "procedure",
      "summary": "다음 내용이 옳으면 ◯표를, 틀리면 ×표를 선택해 오늘의 점심 식단을 찾아봅시다.",
      "source_pages": [
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
        27
      ]
    },
    {
      "chunk_id": "17-18차시-chunk-2",
      "label": "학습 덩어리 2",
      "knowledge_type": "procedure",
      "summary": "2 민주화와 산업화로 달라진 생활 문화 민주화를 이루려는 다양한 분야 사람들의 노력을 설명할 수 있어요.",
      "source_pages": [
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
        48
      ]
    }
  ],
  "source_page_refs": [
    7,
    8,
    9,
    10,
    11,
    12,
    13,
    14
  ],
  "analysis_confidence": 0.75,
  "notes": "자동 생성 초안. lesson title, key concepts, chunks를 검토 후 승인 필요."
}

Schedule draft:
{
  "schema_version": "1.0.0",
  "generated_at": "2026-03-30T15:08:35.863392+00:00",
  "sections": [
    {
      "sheet_name": "16차시",
      "lesson_title": "민주주의와 미디어 — 미디어의 내용을 비판적으로 분석해야 하는 까 닭 알아보기",
      "title_query": "민주주의와 미디어 — 미디어의 내용을 비판적으로 분석해야 하는 까 닭 알아보기"
    },
    {
      "sheet_name": "17-18차시",
      "lesson_title": "민주주의와 미디어 — 미디어를 올바르게 이용하는 방법 알아보기",
      "title_query": "민주주의와 미디어 — 미디어를 올바르게 이용하는 방법 알아보기"
    },
    {
      "sheet_name": "19차시",
      "lesson_title": "2단원 정리 — [단원 마무리] 나만의 누리집 완성하기 / 창의·융 합 사고력 쑥쑥",
      "title_query": "2단원 정리 — [단원 마무리] 나만의 누리집 완성하기 / 창의·융 합 사고력 쑥쑥"
    }
  ]
}

Section context:
{
  "schema_version": "1.0.0",
  "generated_at": "2026-03-30T15:28:16.800480+00:00",
  "pdf_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/textbook/사회/[사회]6_1_교과서.pdf",
  "current_section": {
    "section_key": "___17-18차시__민주주의와_미디어___미디어를_올바르게_이용하는_방법_알아보기",
    "sheet_name": "17-18차시",
    "lesson_title": "민주주의와 미디어 — 미디어를 올바르게 이용하는 방법 알아보기",
    "title_query": "민주주의와 미디어 — 미디어를 올바르게 이용하는 방법 알아보기",
    "pdf_pages": [
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
      48
    ],
    "baseline_analysis_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/artifacts/runs/1-20260331-000829/source/local_baseline/___17-18차시__민주주의와_미디어___미디어를_올바르게_이용하는_방법_알아보기.lesson_analysis.json",
    "extracted_text": "다음 내용이 옳으면 ◯표를, 틀리면 ×표를 선택해 오늘의 점심 식단을 찾아봅시다. \n미디어를 올바르게 이용하려는 \n노력은 국가만 하면 된다.\n미디어에서는 잘못된 정보가 \n무분별하게 퍼지기도 한다. \n미디어의 내용은 비판적으로 \n받아들여야 한다.\n미디어의 정보는 모두 믿어도 \n된다. \n정보를 전달하는 매체를 미디어\n라고 한다.\n이번 주제에서 배운 내용을 정리하며 우리가 행복이를 만날 수 있는 길을 찾아봅시다.\no\n김치찌개\nx\n된장찌개\no\n떡갈비\nx\n떡볶이\no\n탕수육\nx\n돈가스\no\n배추김치\nx\n깍두기\no\n달걀말이\nx\n두부구이\n주제마무리\n되돌아가기를 만나면 교과서를 살펴본 후 처음부터 시작합니다.\n98~101쪽\n92~96쪽\n102쪽\n1.  민주주의에서 미디어의 의미와 역할을 이해했나요?\n \n예 \n \n \n아니요 \n \n2.  미디어의 내용을 비판적으로 분석하고 평가할 수 있나요?\n \n예 \n \n \n아니요 \n \n3.  미디어를 올바르게 이용하는 태도를 지니게 되었나요?\n \n예 \n \n \n아니요 \n \n1\n3\n2\n4\n5\n요약 정리\n103\n3  민주주의와 미디어\n사고력\n쑥쑥 \n창의ㆍ융합\n단원마무리\n1  내가 만들고 싶은 세계지도의 주제를 정해 봅시다.\n나만의 세계지도 만들기\n2  세계지도를 만드는 데 필요한 자료를 조사해 봅시다.\n \n          지도에 자료를 골고루 나타낼 수 있도록 대륙별로 한 나라씩 조사합니다.\n도움말\n나는 세계 여러 나라의 \n축구 대표 팀 유니폼을 알려 \n주는 지도를 만들래.\n나는 세계의 전통 음식을 \n지도에 표현해 볼 거야.\n나는 세계의 유명 건축물이 \n나타난 지도를 만들래.\n대륙\n나라\n주제: \n건축물\n대륙\n나라\n주제: \n북아메리카\n미국\n자유의 여신상\n아시아\n중국\n만리장성\n예시\n152\n3 지구, 대륙 그리고 국가들\n3. 지구, 대륙 그리고 국가들\n3  조사한 내용을 바탕으로 활동 자료13  을 활용해 ‘나만의 세계지도’를 만들어 봅시다.\n4  친구들이 만든 지도를 보고, 가장 기억에 남는 세계지도를 이야기해 봅시다.\n5  나만의 세계지도 만들기 활동을 하고 난 후 스스로 평가해 봅시다.\n지도의 주제가 잘 \n드러나도록 대륙별\n로 알맞은 나라를 \n선정했나요?\n다양한 조사 방법\n을 활용해 주제에 \n관한 자료를 수집\n했나요?\n지도 만들기 활동\n에 성실하게 참여\n했나요?\n예시\n153\n단원 마무리\n단원마무리\n용어 콕!\n이 단원의\n물어보세요\n우리에게\n민주 선거의 기본 원칙에는 무엇\n이 있을까요?\n민주 시민으로서 선거에 참여하는 \n바람직한 태도를 알려 주세요.\n선거에 적극적으로 참여하는 모습\n을 보여 주세요.\n선거의 역할은 무엇일까요?\n선거를 하는 까닭은 무엇일까요?\n모든 사람이 한자리에 모여 공동체의 \n중요한 일을 결정하는 것이 어렵기 때문\n이에요.\n선거는 대표자를 선출하고, 선출된 대표자\n의 권력을 견제해 대표자가 책임 있는 \n정치를 하게 해요.\n후보자의 \n2  \n \n과/와 자질을 꼼꼼히 \n분석하는 태도도 중요해요.\n선거에 관심을 가지고 적극적으로 참여\n하는 태도를 가져야 해요. \n보통 선거, 평등 선거, 직접 선거, 비밀 \n선거가 있어요.\n  선거에 참여해 첫 \n투표를 한 학생들\n  선거에 참여하자는 \n캠페인 활동\n민주주의\n1  \n \n이/가 국민\n에게 있는 정치 형태\n선거\n공동체의 대표를 선출\n하는 과정\n국가기관\n법에 따라 나랏일을 \n하는 기관\n정보를 전달하는 매체\n미디어\n 안에 알맞은 말을 쓰거나 활동 자료1 의 붙임딱지를 붙여 봅시다.\n붙임딱지 \n붙임딱지 \n104\n2 민주주의와 시민 참여\n2. 민주주의와 시민 참여\n나만의 누리집 완성하기\n민주주의와 미디어\n카드 뉴스로 보는\n인기 영상\n이 단원의\n국회의원들로 구성된 국민의 \n대표 기관으로, \n3 \n을/를 만들고 \n고치는 일을 함.\n국가기관을 가다 \n- 국회 편\n민주주의에서 미디어의 역할\n•\u0001선거\u0001후보자의\u0001공약,\u0001정책이나\u0001중요한\u0001사회\u0001\n문제에\u0001관한\u0001\n6 \n \n을/를\u0001제공함.\u0001\n•\u0001사회\u0001문제에\u0001대한\u0001사람들의\u0001관심과\u0001참여를\u0001\n이끌고,\u0001여론을\u0001형성함.\n01\n미디어의 비판적 분석\n•정보의\u0001출처,\u0001저자,\u0001날짜\u0001확인하기\n•\n7  \n \n\u0001과/와\u0001의견\u0001구분하기\n•근거와\u0001자료의\u0001타당성\u0001확인하기\n•관련된\u0001사실\u0001더\u0001찾아보기\n국가기관을 가다 \n- 법원 편\n법에 따라 \n5  \n \n을/를 \n하는 기관으로, 개인 간의 다툼\n을 해결하는 역할을 함.\n국가기관을 가다 \n- 행정부 편\n법에 따라 나라 살림을 맡아 \n하는 기관으로, \n4  \n \n \n을/를 중심으로 구성됨.\n02\n단원 게임\n105\n단원 마무리\n단원 마무리\n이번 단원에서 배운 내용들을 모아, \n나만의 특별한 누리집을 만들어 \n보자. 그리고 창의력과 사고력을 \n키울 수 있는 창의・융합 활동으로 \n이번 단원을 마무리할 거야. \n주제 마무리\n재미있는 놀이로 배운 내용을 복습하고, \n코딩을 활용해 얼마나 잘 이해했는지 \n점검해 보자.\n\n1\n  \n \n평\n화\n 통\n일\n을\n \n위\n한\n \n노\n력\n,\n민\n주\n화\n와\n \n산\n업\n화\n10쪽\n1\n 평\n화\n 통\n일\n을 \n위\n한\n \n노\n력\n2\n 민\n주\n화\n와 \n산\n업\n화로\n \n달\n라\n진\n \n생\n활 \n문\n화\n26쪽\n6학년 1학기 사회 수업 시간에는\n어떤 내용이 우리를 기다리고 있을까?\n이 책의차례\n\n2\n54쪽\n3  \n민주\n주의\n와 미\n디어\n90쪽\n2\n \n국\n가\n기\n관\n이 \n하\n는\n \n일\n70쪽\n \n  \n  \n \n민\n주\n주\n의\n와\n \n시\n민\n \n참\n여\n3\n   \n지\n구\n, \n대\n륙 \n그\n리\n고\n \n국\n가\n들\n60°\n90°\n30°\n0°\n30°\n구경: 320 mm\n축척: 1:40,000,000\n60°\n90°\n30°\n0°\n30°\n인 도 양\n북극해\n대서양\n동해\n60°\n60°\n90°\n90°\n120°\n150°\n150°\n180°\n30°\n30°\n0°\n60°\n60°\n90°\n90°\n120°\n150°\n150°\n180°\n30°\n30°\n0°\n110쪽\n1\n \n지\n구\n본\n과\n 지\n도\n로\n 보\n는\n \n세\n계\n2  \n세\n계\n의 \n대\n륙\n, \n대\n양\n, \n나\n라\n132쪽\n1\n 민\n주\n주\n의\n와\n 선\n거\n\n1\n평화 통일을 위한 노력\n1\n민주화와 산업화로 달라진 생활 문화\n2\n  \n   \n    \n    \n     \n    \n 분\n단  \n평화\n 통\n일 \n 민\n주화\n  \n산업\n화  \n평화 통일을 위한 \n노력, 민주화와 \n산업화\n애니메이션\n\n사람들의 이야기를 듣고, 나와 함께 이 단원을 공부할 \n내 친구 하나를 찾아 줘.\n평화 통일 캠페인 전시관에서 받은 한반도기를 \n들고 있어. \n전시회에서 다양한 자료를 받아 간다며 큰 배낭\n을 메고 왔던데?\n나와 가발 만들기 체험을 하고, 또 다른 체험을 \n경험해 보고 싶다고 했어.\n\n1\n평화 통일을 \n위한 노력\n 분단으로 생겨난 문제점과 평화 통일의 필요성을 설명할 수 있어요.\n 분단과 관련된 장소를 평화의 장소로 만들려는 노력을 찾아볼 수 있어요.\n 평화 통일을 위해 우리가 할 수 있는 일을 탐색할 수 있어요.\n이 주제를 배우면 나는\n이 산책로에 있는\n푯말은 무엇을 의미할까?\n1\n10\n1 평화 통일을 위한 노력, 민주화와 산업화\n\n1  낱말 구름을 보고, 이 주제에서 배울 내용이 무엇인지 생각해 봅시다.\n2  낱말 구름에 있는 낱말 9개를 골라서 빙고 놀이를 해 봅시다.\n평화 통일\n분단\n협력\n화해\n전쟁\n남한\n북한\n비무장 지대\n교류\n대립\n이산가족\n남북 정상 회담\n휴전선\n북한 이탈 주민\n문화 차이\n이 사람들이 들고 있는\n깃발은 무엇을\n상징할까?\n2\n11\n1   평화 통일을 위한 노력\n\n북한의 핵 실험과 미사일 발사 등 군사적 위협이 \n지속되면서 한반도는 항상 군사적 충돌 위험에 놓여 \n있으며, 이 때문에 남북한 모두 막대한 국방비를 지출\n하고 있다. 남북 간 군사적 대립은 전쟁 발생에 대한 \n불안감을 일으키며, 동아시아와 세계 평화\n에도 심각한 위협이 되고 있다.\n군사적 긴장\n분단으로 어떤 문제가 발생했을까요?\n하나\n한반도는 광복 후 분단되었고, 6·25 전쟁 이후 분단 상황이 굳어졌다. \n70년이 넘는 긴 세월 동안 남북 간 적대 관계가 지속되었으며, 사회·문화적 \n차이가 커지는 등 여러 가지 문제점이 나타났다.\n북한 이탈 주민들이 출연하는 방송을 보고 있었는데, 출연자 중 한 사람이 “일 \n없습니다.”라고 하는 거야. ‘할 일이 없다.’라는 뜻인지 궁금해서 고개를 갸웃했더니, 아빠 \n께서 ‘괜찮다.’라는 뜻이라고 알려 ",
    "extracted_text_truncated": true
  },
  "neighbor_sections": [
    {
      "relation": "previous",
      "section_key": "___16차시__민주주의와_미디어___미디어의_내용을_비판적으로_분석해야_하는_까_닭_알아보기",
      "sheet_name": "16차시",
      "lesson_title": "민주주의와 미디어 — 미디어의 내용을 비판적으로 분석해야 하는 까 닭 알아보기",
      "title_query": "민주주의와 미디어 — 미디어의 내용을 비판적으로 분석해야 하는 까 닭 알아보기",
      "pdf_pages": [
        90
      ]
    },
    {
      "relation": "next",
      "section_key": "___19차시__2단원_정리____단원_마무리__나만의_누리집_완성하기___창의_융_합_사고력_쑥쑥",
      "sheet_name": "19차시",
      "lesson_title": "2단원 정리 — [단원 마무리] 나만의 누리집 완성하기 / 창의·융 합 사고력 쑥쑥",
      "title_query": "2단원 정리 — [단원 마무리] 나만의 누리집 완성하기 / 창의·융 합 사고력 쑥쑥",
      "pdf_pages": [
        49
      ]
    }
  ]
}

Target schema:
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://numbersauto.local/schemas/lesson_analysis.schema.json",
  "title": "Lesson Analysis",
  "type": "object",
  "required": [
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
  "properties": {
    "schema_version": {
      "type": "string"
    },
    "generated_at": {
      "type": "string",
      "format": "date-time"
    },
    "lesson_id": {
      "type": "string"
    },
    "sheet_name": {
      "type": "string"
    },
    "lesson_title": {
      "type": "string"
    },
    "lesson_type": {
      "type": "string",
      "enum": ["intro", "core", "review", "summary", "mixed"]
    },
    "pdf_pages": {
      "type": "array",
      "items": {
        "type": "integer",
        "minimum": 1
      },
      "minItems": 1
    },
    "essential_question": {
      "type": "string"
    },
    "learning_goals": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "minItems": 1
    },
    "key_concepts": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "minItems": 1
    },
    "vocabulary": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "misconceptions": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "difficulty_band": {
      "type": "string",
      "enum": ["core", "on-level", "extension", "mixed"]
    },
    "content_chunks": {
      "type": "array",
      "items": {
        "type": "object",
        "required": [
          "chunk_id",
          "label",
          "content_type",
          "knowledge_type",
          "summary",
          "source_pages"
        ],
        "properties": {
          "chunk_id": {
            "type": "string"
          },
          "label": {
            "type": "string"
          },
          "content_type": {
            "type": "string",
            "enum": ["text", "image", "diagram", "map", "activity", "summary", "mixed"]
          },
          "knowledge_type": {
            "type": "string",
            "enum": ["fact", "concept", "procedure", "comparison", "cause-effect", "opinion", "application", "mixed"]
          },
          "summary": {
            "type": "string"
          },
          "source_pages": {
            "type": "array",
            "items": {
              "type": "integer",
              "minimum": 1
            },
            "minItems": 1
          },
          "suggested_activity_types": {
            "type": "array",
            "items": {
              "type": "string"
            }
          }
        },
        "additionalProperties": false
      }
    },
    "source_page_refs": {
      "type": "array",
      "items": {
        "type": "integer",
        "minimum": 1
      },
      "minItems": 1
    },
    "analysis_confidence": {
      "type": "number",
      "minimum": 0,
      "maximum": 1
    },
    "review_status": {
      "type": "string",
      "enum": ["draft", "reviewed", "approved", "rejected"]
    },
    "notes": {
      "type": "string"
    }
  },
  "additionalProperties": false
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
