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
  "sheet_name": "6차시",
  "card_file": "___6차시",
  "title": "지구본과 지도로 보는 세계 — 경도와 경선의 의미 알아보기",
  "badge": "6차시",
  "pdf_pages": [
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
    109
  ],
  "textbook_source": {
    "resource_id": "main",
    "title_query": "지구본과 지도로 보는 세계 — 경도와 경선의 의미 알아보기",
    "start_page": 54,
    "end_page": 109,
    "confidence": 0.55,
    "status": "matched"
  }
}

Baseline lesson analysis:
{
  "lesson_id": "6차시",
  "sheet_name": "6차시",
  "lesson_title": "지구본과 지도로 보는 세계 — 경도와 경선의 의미 알아보기",
  "lesson_type": "core",
  "pdf_pages": [
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
    109
  ],
  "essential_question": "지구본과 지도로 보는 세계 — 경도와 경선의 의미 알아보기",
  "learning_goals": [
    "지구본과 지도로 보는 세계 — 경도와 경선의 의미 알아보기의 핵심 내용을 설명할 수 있다."
  ],
  "key_concepts": [
    "지구본",
    "지도",
    "보는",
    "세계",
    "경도"
  ],
  "vocabulary": [
    "지구본",
    "지도",
    "보는"
  ],
  "misconceptions": [
    "선거를 단순히 사람을 뽑는 행사로만 이해할 수 있다.",
    "민주주의의 핵심이 참여보다 결과에만 있다고 오해할 수 있다."
  ],
  "difficulty_band": "on-level",
  "content_chunks": [
    {
      "chunk_id": "6차시-chunk-1",
      "label": "학습 덩어리 1",
      "knowledge_type": "procedure",
      "summary": "사람들이 몸으로 만든 저 모양은 무엇을 의미하는 걸까?",
      "source_pages": [
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
        81
      ]
    },
    {
      "chunk_id": "6차시-chunk-2",
      "label": "학습 덩어리 2",
      "knowledge_type": "procedure",
      "summary": "법원의 구성과 하는 일 법원은 법에 따라 재판을 하는 기관이다.",
      "source_pages": [
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
        109
      ]
    }
  ],
  "source_page_refs": [
    54,
    55,
    56,
    57,
    58,
    59,
    60,
    61
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
      "sheet_name": "5차시",
      "lesson_title": "지구본과 지도로 보는 세계 — 위도와 위선의 의미 알아보기",
      "title_query": "지구본과 지도로 보는 세계 — 위도와 위선의 의미 알아보기"
    },
    {
      "sheet_name": "6차시",
      "lesson_title": "지구본과 지도로 보는 세계 — 경도와 경선의 의미 알아보기",
      "title_query": "지구본과 지도로 보는 세계 — 경도와 경선의 의미 알아보기"
    },
    {
      "sheet_name": "7차시",
      "lesson_title": "지구본과 지도로 보는 세계 — 위도와 경도를 이용해 위치를 표현하는 방법 살 펴보기",
      "title_query": "지구본과 지도로 보는 세계 — 위도와 경도를 이용해 위치를 표현하는 방법 살 펴보기"
    }
  ]
}

Section context:
{
  "schema_version": "1.0.0",
  "generated_at": "2026-03-30T15:33:13.538969+00:00",
  "pdf_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/textbook/사회/[사회]6_1_교과서.pdf",
  "current_section": {
    "section_key": "___6차시__지구본과_지도로_보는_세계___경도와_경선의_의미_알아보기",
    "sheet_name": "6차시",
    "lesson_title": "지구본과 지도로 보는 세계 — 경도와 경선의 의미 알아보기",
    "title_query": "지구본과 지도로 보는 세계 — 경도와 경선의 의미 알아보기",
    "pdf_pages": [
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
      109
    ],
    "baseline_analysis_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/artifacts/runs/1-20260331-001435/source/local_baseline/___6차시__지구본과_지도로_보는_세계___경도와_경선의_의미_알아보기.lesson_analysis.json",
    "extracted_text": "사람들이\n몸으로 만든 저 모양은 무엇을\n의미하는 걸까?\n 민주주의에서 선거의 의미와 역할 및 중요성을 파악할 수 있어요.\n 민주 국가의 선거 과정과 선거 원칙을 파악할 수 있어요.\n 선거에 주체적으로 참여하는 태도를 지닐 수 있어요.\n이 주제를 배우면 나는\n민주주의와 선거\n1\n1\n54\n2 민주주의와 시민 참여\n\n1  낱말 구름을 보고, 이 주제에서 배울 내용이 무엇인지 생각해 봅시다.\n2  낱말 구름에 있는 낱말 9개를 골라서 빙고 놀이를 해 봅시다.\n선거\n민주주의\n투표\n공약\n주권\n선거관리위원회\n정치\n투표율\n선출\n유권자\n대표\n보통 선거\n직접 선거\n평등 선거\n비밀 선거\n왜 학생들이\n투표소 앞에서 사진을 \n촬영하고 있을까?\n2\n55\n1   민주주의와 선거\n\n현대 사회에서는 많은 사람이 함께 살아가기 때문에 모든 구성원이 한\n자리에 모여  공동체의 중요한 일을 결정하는 것이 어렵다. 따라서 사람들은 \n자신을 대신하여 공동체를 위해 일할 대표를 선출하는데, 이 과정을 선거\n라고 한다. \n선거란 무엇일까요?\n하나\n요즘 선거 운동이 한창이라 동네가 시끌벅적해. 분명 얼마 전에 선거를 한 것 \n같은데, 올해 또 선거를 한다고? 알고 보니 저번에는 국회의원을 뽑는 선거였고, 이번에는 우리 \n지역 대표를 뽑는 선거라고 해. 그런데 왜 주민들이 국회의원이나 지역 대표를 뽑는 걸까? \n생각 깨우기\n선출  여럿 가운데서 골라냄.\n애니메이션\n 국민의 대표인 \n   국회의원을 선출함.\n투표와 선거는\n같은 의미일까?\n국회의원 선거\n ‌\u0007각 지방 자치 단체를 대표하는  \n사람들을 선출함.\n지방 선거\n대통령 선거\n ‌\u0007우리나라를 대표하는 \n대통령을 선출함.\n투표는 표를 통해 자신의 의견을 표현하는 \n거야. 어떤 의견에 찬반을 묻는 투표를 할 수 \n있지만, 이는 대표를 선출하는 것은 아니기 때문에 \n투표와 선거가 같은 의미는 아니야.\n56\n2 민주주의와 시민 참여\n\n창의적 사고력\n공동체를 위해 일할 대표를 선출하는 과정을 \nㅅ\nㄱ\n (이)라고 한다.\n한 문장 정리\n민주주의 국가에서 국가의 중요한 일은 국민의 뜻에 따라 결정된다. 선거\n는 국민이 직접  주권을 행사하는 대표적인 방법으로, 민주주의에서 가장 \n기본적이고 중요한 정치 참여 활동이다. 이러한 의미를 담아 선거를 ‘민주\n주의의 꽃’이라고도 부른다.\n주권  국가의 의사를 최종\n적으로 결정하는 권력\n2\t \u0007선거와 관련된 경험을 떠올려 보고, 누구를 선출하는 선거였으며, 그때 어떤 기분이 들었는지 \n이야기해 봅시다.\u0007\n선거 경험 떠올려 보기\n스스로\n해 보기\n어떤 후보를 뽑아야\n할까?\n나와 의견이 비슷한 \n후보가 당선되었으면\n좋겠어.\n1\t \u0007위 그림 속 학생이 선거에 대해 어떤 생각을 할지 상상해 써 봅시다.\n배움 확인\n57\n1   민주주의와 선거\n\n선거의 가장 기본적인 역할은 공동체의 대표자를  선출하는 것이다. 사람\n들은 선거에 나온 후보자 중에서 자신의 의견을 가장 잘 대변해 줄 수 있는 \n사람을 대표자로 선출한다. 선출된 대표자는 구성원들의 동의와 지지를 \n받았으므로 공동체를 대표해 일할 수 있게 된다. \n민주주의에서 선거는 \n어떤 역할을 할까요? \n둘\n오늘 학교 가는 길에 ‘국가의 주인은 국민’이라는 팻말을 들고 선거 운동을 하는 \n분들을 봤어. 그분들은 국가의 주인으로서 우리 지역 대표를 뽑는 선거에 꼭 참여해야 한다고 \n말씀하셨어. 선거와 국가의 주인은 어떤 관계가 있는 걸까?\n생각 깨우기\n대변  어떤 사람이나 단체를 \n대신해 의견을 말함.\n선거로 대표를 선출해 \n우리 지역의 일을 맡기는 건 \n어떨까요?\n우리 지역의 경제 문제를 \n해결하겠습니다.\n어떤 후보를\n선택해야 할까?\n우리 지역의 교통 문제를 \n해결하겠습니다.\n일이 바쁜데 매번 주민\n투표로 모든 결정을 하려고 \n하니 너무 힘들어.\n주민 여러분, 저를 뽑아 주셔서 \n감사합니다. 지역 주민들의 \n의견을 잘 반영해 지역의 교통 \n문제를 해결하겠습니다.\n지역의 대표를 뽑았으니 \n이제 지역문제들이 \n잘 해결될 거야.\n○\n○ \n지역\n의 선\n거\n애니메이션\n58\n2 민주주의와 시민 참여\n\n선거로 선출된 대표자는 구성원들의 뜻을 반영한 공약을 실천한다. 만약 \n대표자의 능력이 부족하거나 역할을 제대로 수행하지 못해 사람들의 지지를 \n받지 못하면, 다음 선거에서 대표자로 선출되기 어려울 수 있다. 이처럼 민주\n주의에서 선거는 선출된 대표자의 권력을 견제하고, 대표자가 책임 있는 정치\n를 하게 한다.\n2 \u00071과 같은 장면을 그린 까닭을 선거의 역할과 연결 지어 이야기해 봅시다.\n공약  후보자가 어떤 일을 \n하겠다고 약속하는 것\n견제  상대가 지나치게 권력을 \n행사하거나 자유롭게 행동\n하지 못하게 억누름.\n어떻게 해야 \n할까?\n지역 대표가 선거 후보였을\n때 약속했던 공약을 지키지 \n않아서 너무 실망스러워.\n선거는 대표자를 \nㅅ\nㅊ\n 하고, 대표자의 권력을 견제해 책임 있는 정치를 하게 한다.\n한 문장 정리\n창의적 사고력\n비판적 사고력\n1 \u0007만화를 읽고 빈칸에 들어갈 장면을 상상해 그려 봅시다.\n◯◯ 지역의 선거 사례를 통해 선거의 역할 파악하기\n스스로\n해 보기\n지역의 교통 문제를\n해결하겠다고 해서 \n뽑았는데……. 달라진 것이 \n없잖아.\n배움 확인\n59\n1   민주주의와 선거\n\n제가 우리 지역의 \n대표자가 되고 \n싶습니다.\n여러분, 열심히 \n일하겠습니다. 저를 \n뽑아 주세요!\n여러분들의 소중한 한 표, \n부탁드리겠습니다.\n3  선거 운동\n후보자들이 정해진 기간 \n동안 선거 운동을 한다.\n2  후보자 등록\n선거에 출마하고자 하는 \n사람은 선거관리위원회에 \n후보자 등록을 한다.\n우리\n나라\n의 선\n거 과\n정\n선거관리위원회  선거와 국민 \n투표를 관리하기 위해 설치\n한 국가기관\n선거인 명부  선거권이 있는 \n사람을 적은 장부\n출마  선거에 나감.\n1   선거인 명부 작성\n선거권이 있는 사람들을 \n조사한다.\n공정한 선거를 위한 노력\n우리나라는 공정한 선거를 위해 선거 과정을 법으로 정해 두었다. 또한 \n선거관리위원회를 두어 선거 과정을 공정하게 관리하며, 사람들이 선거에 \n적극적으로 참여하도록 다양한 홍보 활동을 한다.\n민주주의에서 선거는 어떻게 \n이루어질까요?\n셋\n오늘은 기다리던 투표 날이야! 아빠를 따라간 투",
    "extracted_text_truncated": true
  },
  "neighbor_sections": [
    {
      "relation": "previous",
      "section_key": "___5차시__지구본과_지도로_보는_세계___위도와_위선의_의미_알아보기",
      "sheet_name": "5차시",
      "lesson_title": "지구본과 지도로 보는 세계 — 위도와 위선의 의미 알아보기",
      "title_query": "지구본과 지도로 보는 세계 — 위도와 위선의 의미 알아보기",
      "pdf_pages": [
        83
      ]
    },
    {
      "relation": "next",
      "section_key": "___7차시__지구본과_지도로_보는_세계___위도와_경도를_이용해_위치를_표현하는_방법_살_펴보기",
      "sheet_name": "7차시",
      "lesson_title": "지구본과 지도로 보는 세계 — 위도와 경도를 이용해 위치를 표현하는 방법 살 펴보기",
      "title_query": "지구본과 지도로 보는 세계 — 위도와 경도를 이용해 위치를 표현하는 방법 살 펴보기",
      "pdf_pages": [
        110
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
