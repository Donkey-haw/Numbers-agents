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
  "sheet_name": "1차시",
  "card_file": "___1차시",
  "title": "2단원 도입 — [단원 도입] 우리 친구는 누구?",
  "badge": "1차시",
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
    53
  ],
  "textbook_source": {
    "resource_id": "main",
    "title_query": "2단원 도입 — [단원 도입] 우리 친구는 누구?",
    "start_page": 4,
    "end_page": 53,
    "confidence": 0.55,
    "status": "matched"
  }
}

Baseline lesson analysis:
{
  "lesson_id": "1차시",
  "sheet_name": "1차시",
  "lesson_title": "2단원 도입 — [단원 도입] 우리 친구는 누구?",
  "lesson_type": "core",
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
    53
  ],
  "essential_question": "2단원 도입 — [단원 도입] 우리 친구는 누구?",
  "learning_goals": [
    "2단원 도입 — [단원 도입] 우리 친구는 누구의 핵심 내용을 설명할 수 있다."
  ],
  "key_concepts": [
    "도입",
    "친구",
    "누구",
    "평화",
    "민주화"
  ],
  "vocabulary": [
    "도입",
    "친구",
    "누구"
  ],
  "misconceptions": [
    "선거를 단순히 사람을 뽑는 행사로만 이해할 수 있다.",
    "민주주의의 핵심이 참여보다 결과에만 있다고 오해할 수 있다."
  ],
  "difficulty_band": "on-level",
  "content_chunks": [
    {
      "chunk_id": "1차시-chunk-1",
      "label": "학습 덩어리 1",
      "knowledge_type": "procedure",
      "summary": "안녕, 친구들!",
      "source_pages": [
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
        28
      ]
    },
    {
      "chunk_id": "1차시-chunk-2",
      "label": "학습 덩어리 2",
      "knowledge_type": "procedure",
      "summary": "민주화 산업화 생활 문화 4.19 혁명 5.18 민주화 운동 6월 민주 항쟁 지방 자치제 시민 의식 중화학 공업 생태환경 경제성장 시민운동 직선제 독재 경공업 1 낱말 구름을 보고, 이 주제에서 배울 내용이 무엇인지 생각해 봅시다.",
      "source_pages": [
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
        53
      ]
    }
  ],
  "source_page_refs": [
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    11
  ],
  "analysis_confidence": 0.75,
  "notes": "자동 생성 초안. lesson title, key concepts, chunks를 검토 후 승인 필요."
}

Schedule draft:
{
  "schema_version": "1.0.0",
  "generated_at": "2026-03-30T15:13:01.760315+00:00",
  "sections": [
    {
      "sheet_name": "14차시",
      "lesson_title": "1단원 정리 — [단원 마무리] 나만의 누리집 완성하기 / 창의·융 합 사고력 쑥쑥",
      "title_query": "1단원 정리 — [단원 마무리] 나만의 누리집 완성하기 / 창의·융 합 사고력 쑥쑥"
    },
    {
      "sheet_name": "1차시",
      "lesson_title": "2단원 도입 — [단원 도입] 우리 친구는 누구?",
      "title_query": "2단원 도입 — [단원 도입] 우리 친구는 누구?"
    },
    {
      "sheet_name": "2차시",
      "lesson_title": "민주주의와 선거 — 선거의 의미와 중요성 파악하기",
      "title_query": "민주주의와 선거 — 선거의 의미와 중요성 파악하기"
    }
  ]
}

Section context:
{
  "schema_version": "1.0.0",
  "generated_at": "2026-03-30T15:19:02.898312+00:00",
  "pdf_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/textbook/사회/[사회]6_1_교과서.pdf",
  "current_section": {
    "section_key": "___1차시__2단원_도입____단원_도입__우리_친구는_누구_",
    "sheet_name": "1차시",
    "lesson_title": "2단원 도입 — [단원 도입] 우리 친구는 누구?",
    "title_query": "2단원 도입 — [단원 도입] 우리 친구는 누구?",
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
      53
    ],
    "baseline_analysis_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/artifacts/runs/1-20260331-001255/source/local_baseline/___1차시__2단원_도입____단원_도입__우리_친구는_누구_.lesson_analysis.json",
    "extracted_text": "안녕, 친구들! 나는 ‘우리’야.\n너희들은 ‘사회’라는 단어를 들으면 어떤 모습이 떠오르니?\n ‘사회’는 우리가 살아가는 일상 속에서 일어나는 \n여러 사건과 현상을 이해하고, \n더 나은 세상을 만들어 가는 데 중요한 역할을 하는 과목이야.\n교과서를 펼칠 준비가 됐니? \n이제 나와 함께 배움 여행을 떠나 보자!\n이 책의구성과 \n  특징\n1\n평화 통일을 위한 노력\n1\n민주화와 산업화로 달라진 생활 문화\n2\n  \n   \n    \n    \n     \n    \n 분\n단  \n평화\n 통\n일 \n 민\n주화\n  \n산업\n화  \n평화 통일을 위한 \n노력, 민주화와 \n산업화\n애니메이션\n사람들의 이야기를 듣고, 나와 함께 이 단원을 공부할 \n내 친구 하나를 찾아 줘.\n평화 통일 캠페인 전시관에서 받은 한반도기를 \n들고 있어. \n전시회에서 다양한 자료를 받아 간다며 큰 배낭\n을 메고 왔던데?\n나와 가발 만들기 체험을 하고, 또 다른 체험을 \n경험해 보고 싶다고 했어. \n1\n평화 통일을 \n위한 노력\n 분단으로 생겨난 문제점과 평화 통일의 필요성을 설명할 수 있어요.\n 분단과 관련된 장소를 평화의 장소로 만들려는 노력을 찾아볼 수 있어요.\n 평화 통일을 위해 우리가 할 수 있는 일을 탐색할 수 있어요.\n이 주제를 배우면 나는\n이 산책로에 있는\n푯말은 무엇을 의미할까?\n1\n10\n1 평화 통일을 위한 노력, 민주화와 산업화\n1  낱말 구름을 보고, 이 주제에서 배울 내용이 무엇인지 생각해 봅시다.\n2  낱말 구름에 있는 낱말 9개를 골라서 빙고 놀이를 해 봅시다.\n평화 통일\n분단\n협력\n화해\n전쟁\n남한\n북한\n비무장 지대\n교류\n대립\n이산가족\n남북 정상 회담\n휴전선\n북한 이탈 주민\n문화 차이\n이 사람들이 들고 있는\n깃발은 무엇을\n상징할까?\n2\n11\n1  평화 통일을 위한 노력\n이 주제에서 배울 낱말들로 \n재미있는 빙고 놀이도 해 보자! \n준비됐니? \n대단원 도입\n이 단원의 내용을 그림으로 간단히 소개하고 \n있어. 대화창에 있는 힌트를 보며 우리와 함께 \n공부할 새로운 친구도 찾아보자!\n주제 도입\n주제와 관련한 사진을 보며 떠오르는 생각\n이나 경험을 자유롭게 나눠 볼까?\n나는 우리 친구\n행복이!\n\n본문\n주요 개념을 생활 속 다양한 장면이 담긴 사진과 \n그림으로 제시해 더 쉽게 이해할 수 있을 거야. \n스스로 / 함께해 보기\n혼자 또는 친구들과 함께하는 다양한 활동과 탐구\n를 통해 사회 과목의 역량을 키워 갈 수 있어. \n우리봇이 알려 주는 사회\n궁금하지만 잘 몰랐던 내용은 ‘우리봇’이 친절하게 \n설명해 줄 거야. \n비판적 사고력\n문제 해결력 및\n의사 결정력\n선거에 참여하는 바람직한 태도는 \n무엇일까요?\n넷\n민주 시민으로서 주권을 행사하려면 선거에 적극적으로 참여하는 것이 \n매우 중요하다. 선거에 관심이 부족하거나 참여하는 사람이 적으면 시민\n들의 의견을 충분히 반영할 수 있는 적합한 대표를 선출하기 어렵다. 또한 \n자신의 선택이 사회와 공동체에 끼치는 영향을 고려하고, 자신의 가치관과 \n신념을 바탕으로 책임감 있게 선거 과정에 참여하는 태도가 필요하다.\n2   ◯◯ 지역 주민들의 의견을 충분히 반영할 수 있는 대표를 선출하려면 어떻게 해야 할지 이\n야기해 봅시다.\n1   위 대화에서 밑줄 친 부분과 같은 걱정을 하는 까닭이 무엇일지 이야기해 봅시다. \n선거에 적극적으로 참여해야 하는 까닭 알아보기\n스스로\n해 보기\n이번  지역 선거는 \n투표율이 낮았습니다. 선거권이 \n있는 총 100명의 주민 중 단 35명만 \n투표에 참여했습니다.\n그렇습니다. 그중 3번 후보가 \n13표를 얻어 지역 대표로 당선\n되었습니다. 100명 중 13표를 얻은 \n대표자가 과연 지역 주민들의 의견을 잘 \n대변할 수 있을지 우려가 큽니다.\n투표가 끝난 후 텔레비전에서 지역별 투표율을 알려 주는 방송을 봤어. 투표율이 \n높은 지역과 낮은 지역의 차이가 꽤 크더라고. 난 투표를 하고 싶어도 못하는데, 투표하지 않는 \n사람도 있다니……. 투표하지 않는 사람이 많아지면 어떻게 될까?\n생각 깨우기\n신념  굳게 믿는 마음\n당선\n애니메이션\n64\n2 민주주의와 시민 참여\n후보자의 능력과 \n도덕성 등을 \n확인해야 해.\n후보자의 공약과 \n자질을 분석하는 방법을 \n알아볼까?\n후보자가 우리 지역이나 \n나라에 실제로 필요한 \n공약을 제시하는지 따져 \n봐야 해.\n후보자의 공약이 \n실천 가능한 것인지\n분석해 봐야 해.\n선거 과정에서 후보자의 공약과 자질을 꼼꼼히 분석하는 태도도 중요하다. \n공약과 자질을 분석해 보면 후보자가 시민들의 의견을 얼마나 잘 반영할 \n수 있을지 판단할 수 있기 때문이다.\n도덕성  옳은 일을 하려고 \n하는 마음과 행동\n자질  어떤 분야의 일에 대한 \n능력이나 실력의 정도\n후보자를 선택할 때\n또 어떤 점을 고려해야 \n할지 생각해 보자.\n우리나라는 원래 19세부터 선거에 참여할 수 있었지만, \n2020년에 실시한 제21대 국회의원 선거부터 18세도 선거 \n에 참여할 수 있게 되었다. 선거관리위원회에서는 18세 청소\n년들을 대상으로 선거 교육을 실시해 청소년들이 첫 선거에 \n참여할 수 있도록 도왔다. 선거에 참여할 수 있는 나이가 \n낮아지면서 청소년들도 우리 사회와 미래를 위해 소중한 한 \n표를 행사할 수 있게 되었다.\n청소년도 선거에 참여할 수 있을까?\n우리봇이 알려 주는 사회\n65\n1  민주주의와 선거\n생각 깨우기\n우리들의 이야기로 수업을 활기차게 시작해 볼까? \n사회과 교과 역량 \n창의적 사고력\n비판적 사고력\n정보 활용 능력\n의사소통 및\n협업 능력\n문제 해결력 및\n의사 결정력\n색칠한 원이 한 개면 한 차시 학습\n색칠한 원이 두 개면 두 차시 학습\n\n우\n리\n가\n \n들\n려\n주\n는\n \n사\n회\n \n이\n야\n기\n우\n사이\n들\n리\n우리나라에서는 18세 이상 대한민국 국민이라면 누구나 자유롭게 투표에 참여할 수 \n있지만, 투표에 참여하지 않는 사람들도 있다. 반면에 벨기에, 오스트레일리아, 볼리비아 등 \n일부 나라에서는 의무 투표제를 시행해 투표권이 있는 모든 사람이 반드시 투표에 참여하도\n록 하고 있다. 그중 몇몇 나라들은 투표에 참여하지 않는 사람들에게 벌금을 내게 하거나, \n정치 참여를 제한하는 등의 불이익을 주기도 한다. 그 결과, 의무 투표제를 시행하는 나라들\n에서는 투표율이 높게 나타나는 편이다.\n투표하지 않으면\n \n내 권리가 제한된다고요? \n우리나라에서 의무 투표제를 시행한다면 어떤 장점과 단점이 있을지 이야기해 봅시다.\n전 세계에서 처음으로 의무 투표\n제를 도입한 벨기에는 정당한 이유 \n없이 15년 동안 4번 이상 투표에 \n참여하지 않으면 10년 동안의 투표권\n을 박탈해.\n오스트레일리아에서는 \n정당한 이유 없이 투표에 \n참여하지 않은 사람들에게 \n벌금을 내게 해.\n볼리비아에서는 투표에 \n참여하지 않은 사람의 은행 \n거래를 제한하고, 여권 발급\n을 막는 등의 불이익을 줘.\n68\n2 민주주의와 시민 참여\n함께 그리는 평화로운 미래,  \n \n남북 어린이 교류 현장 속으로!\n우\n친\n소\n   \n  \n  \n  \n  \n  \n  \n  \n \n \n우\n리\n \n친\n구\n들\n의\n \n이\n야\n기\n를\n \n소\n개\n합\n니\n다\n \n  \n   \n남북\n 어\n린이\n 평\n화 그\n림전\n 북한 어린이가 쓴 편지\n2023년, 경기도 파주시 교하 도서관에서 남북 어린이 \n평화 그림전 ‘피스 갤러리ʼ가 열렸다. 이 행사에서는 \n2000년대 남북 어린이들이 주고받은 편지와 사진 등이 \n전시되었다. 전시회를 관람한 어린이들은 평화 통일의 \n내용을 담은 그림 편지를 쓰며, 앞으로 남북한 어린이들\n의 교류가 더욱 활발히 이루어지길 소망했다.\n평화 통일의 숲\n가꾸기 대회\n2006년, 서울의 한 초등학교 학생들은 \n설레는 마음으로 개성 땅을 밟았다. ‘개성 \n청소년 평화 통일의 숲 가꾸기’ 대회에 참여\n하기 위해서였다. 이 행사는 개성 송악산을 \n푸르게 가꾸며 한반도에 평화의 숲을 조성\n하고, 평화 통일을 기원하는 의미를 담고 \n있었다. 학생들은 평화와 통일을 상징하는 \n나무를 심으며 평화 통일을 기원했다.\n남북 어린이들이 참여할 수 있는 교류 사례를 더 찾아봅시다. \n24\n1 평화 통일을 위한 노력, 민주화와 산업화\n우친소\n자신의 일을 주도적으로 이끌어 간 멋진 \n친구들의 이야기도 들려줄게.\n우리들 사이\n우리 주변에서 일어나는 흥미로운 이야기\n들이 가득 담",
    "extracted_text_truncated": true
  },
  "neighbor_sections": [
    {
      "relation": "previous",
      "section_key": "___14차시__1단원_정리____단원_마무리__나만의_누리집_완성하기___창의_융_합_사고력_쑥쑥",
      "sheet_name": "14차시",
      "lesson_title": "1단원 정리 — [단원 마무리] 나만의 누리집 완성하기 / 창의·융 합 사고력 쑥쑥",
      "title_query": "1단원 정리 — [단원 마무리] 나만의 누리집 완성하기 / 창의·융 합 사고력 쑥쑥",
      "pdf_pages": [
        49
      ]
    },
    {
      "relation": "next",
      "section_key": "___2차시__민주주의와_선거___선거의_의미와_중요성_파악하기",
      "sheet_name": "2차시",
      "lesson_title": "민주주의와 선거 — 선거의 의미와 중요성 파악하기",
      "title_query": "민주주의와 선거 — 선거의 의미와 중요성 파악하기",
      "pdf_pages": [
        54
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
