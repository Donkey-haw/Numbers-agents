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
  "textbook_source": {
    "resource_id": "main",
    "title_query": "민주주의와 미디어 — 미디어를 올바르게 이용하는 방법 알아보기",
    "start_page": 7,
    "end_page": 48,
    "confidence": 0.55,
    "status": "matched"
  }
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
  "generated_at": "2026-03-30T15:14:42.342846+00:00",
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
  "generated_at": "2026-03-30T15:30:09.735433+00:00",
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
    "baseline_analysis_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/artifacts/runs/1-20260331-001435/source/local_baseline/___17-18차시__민주주의와_미디어___미디어를_올바르게_이용하는_방법_알아보기.lesson_analysis.json",
    "extracted_text": "다음 내용이 옳으면 ◯표를, 틀리면 ×표를 선택해 오늘의 점심 식단을 찾아봅시다. \n미디어를 올바르게 이용하려는 \n노력은 국가만 하면 된다.\n미디어에서는 잘못된 정보가 \n무분별하게 퍼지기도 한다. \n미디어의 내용은 비판적으로 \n받아들여야 한다.\n미디어의 정보는 모두 믿어도 \n된다. \n정보를 전달하는 매체를 미디어\n라고 한다.\n이번 주제에서 배운 내용을 정리하며 우리가 행복이를 만날 수 있는 길을 찾아봅시다.\no\n김치찌개\nx\n된장찌개\no\n떡갈비\nx\n떡볶이\no\n탕수육\nx\n돈가스\no\n배추김치\nx\n깍두기\no\n달걀말이\nx\n두부구이\n주제마무리\n되돌아가기를 만나면 교과서를 살펴본 후 처음부터 시작합니다.\n98~101쪽\n92~96쪽\n102쪽\n1.  민주주의에서 미디어의 의미와 역할을 이해했나요?\n \n예 \n \n \n아니요 \n \n2.  미디어의 내용을 비판적으로 분석하고 평가할 수 있나요?\n \n예 \n \n \n아니요 \n \n3.  미디어를 올바르게 이용하는 태도를 지니게 되었나요?\n \n예 \n \n \n아니요 \n \n1\n3\n2\n4\n5\n요약 정리\n103\n3  민주주의와 미디어\n사고력\n쑥쑥 \n창의ㆍ융합\n단원마무리\n1  내가 만들고 싶은 세계지도의 주제를 정해 봅시다.\n나만의 세계지도 만들기\n2  세계지도를 만드는 데 필요한 자료를 조사해 봅시다.\n \n          지도에 자료를 골고루 나타낼 수 있도록 대륙별로 한 나라씩 조사합니다.\n도움말\n나는 세계 여러 나라의 \n축구 대표 팀 유니폼을 알려 \n주는 지도를 만들래.\n나는 세계의 전통 음식을 \n지도에 표현해 볼 거야.\n나는 세계의 유명 건축물이 \n나타난 지도를 만들래.\n대륙\n나라\n주제: \n건축물\n대륙\n나라\n주제: \n북아메리카\n미국\n자유의 여신상\n아시아\n중국\n만리장성\n예시\n152\n3 지구, 대륙 그리고 국가들\n3. 지구, 대륙 그리고 국가들\n3  조사한 내용을 바탕으로 활동 자료13  을 활용해 ‘나만의 세계지도’를 만들어 봅시다.\n4  친구들이 만든 지도를 보고, 가장 기억에 남는 세계지도를 이야기해 봅시다.\n5  나만의 세계지도 만들기 활동을 하고 난 후 스스로 평가해 봅시다.\n지도의 주제가 잘 \n드러나도록 대륙별\n로 알맞은 나라를 \n선정했나요?\n다양한 조사 방법\n을 활용해 주제에 \n관한 자료를 수집\n했나요?\n지도 만들기 활동\n에 성실하게 참여\n했나요?\n예시\n153\n단원 마무리\n단원마무리\n용어 콕!\n이 단원의\n물어보세요\n우리에게\n민주 선거의 기본 원칙에는 무엇\n이 있을까요?\n민주 시민으로서 선거에 참여하는 \n바람직한 태도를 알려 주세요.\n선거에 적극적으로 참여하는 모습\n을 보여 주세요.\n선거의 역할은 무엇일까요?\n선거를 하는 까닭은 무엇일까요?\n모든 사람이 한자리에 모여 공동체의 \n중요한 일을 결정하는 것이 어렵기 때문\n이에요.\n선거는 대표자를 선출하고, 선출된 대표자\n의 권력을 견제해 대표자가 책임 있는 \n정치를 하게 해요.\n후보자의 \n2  \n \n과/와 자질을 꼼꼼히 \n분석하는 태도도 중요해요.\n선거에 관심을 가지고 적극적으로 참여\n하는 태도를 가져야 해요. \n보통 선거, 평등 선거, 직접 선거, 비밀 \n선거가 있어요.\n  선거에 참여해 첫 \n투표를 한 학생들\n  선거에 참여하자는 \n캠페인 활동\n민주주의\n1  \n \n이/가 국민\n에게 있는 정치 형태\n선거\n공동체의 대표를 선출\n하는 과정\n국가기관\n법에 따라 나랏일을 \n하는 기관\n정보를 전달하는 매체\n미디어\n 안에 알맞은 말을 쓰거나 활동 자료1 의 붙임딱지를 붙여 봅시다.\n붙임딱지 \n붙임딱지 \n104\n2 민주주의와 시민 참여\n2. 민주주의와 시민 참여\n나만의 누리집 완성하기\n민주주의와 미디어\n카드 뉴스로 보는\n인기 영상\n이 단원의\n국회의원들로 구성된 국민의 \n대표 기관으로, \n3 \n을/를 만들고 \n고치는 일을 함.\n국가기관을 가다 \n- 국회 편\n민주주의에서 미디어의 역할\n•\u0001선거\u0001후보자의\u0001공약,\u0001정책이나\u0001중요한\u0001사회\u0001\n문제에\u0001관한\u0001\n6 \n \n을/를\u0001제공함.\u0001\n•\u0001사회\u0001문제에\u0001대한\u0001사람들의\u0001관심과\u0001참여를\u0001\n이끌고,\u0001여론을\u0001형성함.\n01\n미디어의 비판적 분석\n•정보의\u0001출처,\u0001저자,\u0001날짜\u0001확인하기\n•\n7  \n \n\u0001과/와\u0001의견\u0001구분하기\n•근거와\u0001자료의\u0001타당성\u0001확인하기\n•관련된\u0001사실\u0001더\u0001찾아보기\n국가기관을 가다 \n- 법원 편\n법에 따라 \n5  \n \n을/를 \n하는 기관으로, 개인 간의 다툼\n을 해결하는 역할을 함.\n국가기관을 가다 \n- 행정부 편\n법에 따라 나라 살림을 맡아 \n하는 기관으로, \n4  \n \n \n을/를 중심으로 구성됨.\n02\n단원 게임\n105\n단원 마무리\n단원 마무리\n이번 단원에서 배운 내용들을 모아, \n나만의 특별한 누리집을 만들어 \n보자. 그리고 창의력과 사고력을 \n키울 수 있는 창의・융합 활동으로 \n이번 단원을 마무리할 거야. \n주제 마무리\n재미있는 놀이로 배운 내용을 복습하고, \n코딩을 활용해 얼마나 잘 이해했는지 \n점검해 보자.\n\n1\n  \n \n평\n화\n 통\n일\n을\n \n위\n한\n \n노\n력\n,\n민\n주\n화\n와\n \n산\n업\n화\n10쪽\n1\n 평\n화\n 통\n일\n을 \n위\n한\n \n노\n력\n2\n 민\n주\n화\n와 \n산\n업\n화로\n \n달\n라\n진\n \n생\n활 \n문\n화\n26쪽\n6학년 1학기 사회 수업 시간에는\n어떤 내용이 우리를 기다리고 있을까?\n이 책의차례\n\n2\n54쪽\n3  \n민주\n주의\n와 미\n디어\n90쪽\n2\n \n국\n가\n기\n관\n이 \n하\n는\n \n일\n70쪽\n \n  \n  \n \n민\n주\n주\n의\n와\n \n시\n민\n \n참\n여\n3\n   \n지\n구\n, \n대\n륙 \n그\n리\n고\n \n국\n가\n들\n60°\n90°\n30°\n0°\n30°\n구경: 320 mm\n축척: 1:40,000,000\n60°\n90°\n30°\n0°\n30°\n인 도 양\n북극해\n대서양\n동해\n60°\n60°\n90°\n90°\n120°\n150°\n150°\n180°\n30°\n30°\n0°\n60°\n60°\n90°\n90°\n120°\n150°\n150°\n180°\n30°\n30°\n0°\n110쪽\n1\n \n지\n구\n본\n과\n 지\n도\n로\n 보\n는\n \n세\n계\n2  \n세\n계\n의 \n대\n륙\n, \n대\n양\n, \n나\n라\n132쪽\n1\n 민\n주\n주\n의\n와\n 선\n거\n\n1\n평화 통일을 위한 노력\n1\n민주화와 산업화로 달라진 생활 문화\n2\n  \n   \n    \n    \n     \n    \n 분\n단  \n평화\n 통\n일 \n 민\n주화\n  \n산업\n화  \n평화 통일을 위한 \n",
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
