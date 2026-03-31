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
  "sheet_name": "10차시",
  "card_file": "social_6_1_unit1_life_10차시",
  "title": "민주화 이후 우리 사회는 어떻게 달라졌을까요?",
  "badge": "10차시",
  "pdf_pages": [
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
    40
  ],
  "textbook_source": {
    "resource_id": "main",
    "title_query": "민주화 이후 우리 사회는 어떻게 달라졌을까요?",
    "start_page": 28,
    "end_page": 40,
    "confidence": 0.55,
    "status": "matched"
  }
}

Baseline lesson analysis:
{
  "lesson_id": "10차시",
  "sheet_name": "10차시",
  "lesson_title": "민주화 이후 우리 사회는 어떻게 달라졌을까요?",
  "lesson_type": "core",
  "pdf_pages": [
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
    40
  ],
  "essential_question": "민주화 이후 우리 사회는 어떻게 달라졌을까요?",
  "learning_goals": [
    "민주화 이후 우리 사회는 어떻게 달라졌을까요의 핵심 내용을 설명할 수 있다."
  ],
  "key_concepts": [
    "민주화",
    "이후",
    "어떻게",
    "달라졌을까요",
    "운동"
  ],
  "vocabulary": [
    "민주화",
    "이후",
    "어떻게"
  ],
  "misconceptions": [
    "선거를 단순히 사람을 뽑는 행사로만 이해할 수 있다.",
    "민주주의의 핵심이 참여보다 결과에만 있다고 오해할 수 있다."
  ],
  "difficulty_band": "on-level",
  "content_chunks": [
    {
      "chunk_id": "10차시-chunk-1",
      "label": "학습 덩어리 1",
      "knowledge_type": "procedure",
      "summary": "2 민주화와 산업화로 달라진 생활 문화 민주화를 이루려는 다양한 분야 사람들의 노력을 설명할 수 있어요.",
      "source_pages": [
        28,
        29,
        30,
        31,
        32,
        33
      ]
    },
    {
      "chunk_id": "10차시-chunk-2",
      "label": "학습 덩어리 2",
      "knowledge_type": "procedure",
      "summary": "동해 6월 민주 항쟁 전두환 정부가 들어선 이후에도 국민의 자유와 권리를 억압하는 독재 정치가 계속됐다.",
      "source_pages": [
        34,
        35,
        36,
        37,
        38,
        39,
        40
      ]
    }
  ],
  "source_page_refs": [
    28,
    29,
    30,
    31,
    32,
    33,
    34,
    35
  ],
  "analysis_confidence": 0.75,
  "notes": "자동 생성 초안. lesson title, key concepts, chunks를 검토 후 승인 필요."
}

Schedule draft:
{
  "schema_version": "1.0.0",
  "generated_at": "2026-03-30T15:46:27.669237+00:00",
  "sections": [
    {
      "sheet_name": "8-9차시",
      "lesson_title": "민주화를 위한 노력을 살펴볼까요?",
      "title_query": "민주화를 위한 노력을 살펴볼까요?"
    },
    {
      "sheet_name": "10차시",
      "lesson_title": "민주화 이후 우리 사회는 어떻게 달라졌을까요?",
      "title_query": "민주화 이후 우리 사회는 어떻게 달라졌을까요?"
    },
    {
      "sheet_name": "11차시",
      "lesson_title": "우리나라는 어떻게 산업화를 이루었을까요?",
      "title_query": "우리나라는 어떻게 산업화를 이루었을까요?"
    }
  ]
}

Section context:
{
  "schema_version": "1.0.0",
  "generated_at": "2026-03-30T15:46:44.050141+00:00",
  "pdf_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/textbook/사회/[사회]6_1_교과서.pdf",
  "current_section": {
    "section_key": "social_6_1_unit1_life_10차시__민주화_이후_우리_사회는_어떻게_달라졌을까요_",
    "sheet_name": "10차시",
    "lesson_title": "민주화 이후 우리 사회는 어떻게 달라졌을까요?",
    "title_query": "민주화 이후 우리 사회는 어떻게 달라졌을까요?",
    "pdf_pages": [
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
      40
    ],
    "baseline_analysis_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/artifacts/runs/social_6_1_unit1_democratization_industrialization-20260331-004621/source/local_baseline/social_6_1_unit1_life_10차시__민주화_이후_우리_사회는_어떻게_달라졌을까요_.lesson_analysis.json",
    "extracted_text": "2\n민주화와 산업화로 \n달라진 생활 문화\n 민주화를 이루려는 다양한 분야 사람들의 노력을 설명할 수 있어요.\n 우리나라 산업화의 성과와 한계를 파악할 수 있어요.\n 민주화와 산업화로 달라진 사람들의 생활 모습과 문화를 이해할 수 있어요. \n이 주제를 배우면 나는\n사람들이 왜 촛불을 들고 \n광장에 모여 있을까?\n1\n26\n1 평화 통일을 위한 노력, 민주화와 산업화\n\n민주화\n산업화\n생활 문화\n4.19 혁명\n5.18 민주화 운동\n6월 민주 항쟁\n  지방 자치제\n시민 의식\n중화학 공업\n생태환경\n경제성장\n시민운동\n직선제\n독재\n경공업\n1  낱말 구름을 보고, 이 주제에서 배울 내용이 무엇인지 생각해 봅시다.\n2  낱말 구름에 있는 낱말 9개를 골라서 빙고 놀이를 해 봅시다.\n우리나라에 \n본격적으로 컴퓨터가\n보급된 시기는 언제일까?\n2\n27\n2   민주화와 산업화로 달라진 생활 문화\n\n독재 정치\n대한민국 정부 수립 후 한동안 독재 정치가 이어졌다. 대통령들은 권력을 \n유지하려고 국민의 자유와 권리를 억압했다. 이승만 대통령과 박정희 대통령은 \n헌법을 바꿔 자신의 임기를 연장했으며, 국민의 기본 권리를 무시하는 법을 \n만들고, 독재 정치에 반대하는 사람들을 감옥에 가두기도 했다.\n민주화 운동은 왜 일어났을까요?\n하나\n유신 헌법은 박정희 대통령이 \n장기 집권을 위해 바꾼 헌법이야.\n억압  자유롭게 행동하지 \n못하도록 권력을 이용해 \n억누름.\n임기  일을 맡아서 하는 일정\n한 기간 \n할아버지께서 젊으셨을 때 약 2,500명의 사람들이 체육관에 모여 대통령을 \n뽑은 적이 있다고 하셨어. 대통령을 선출하는 중요한 일이 체육관에서 이루어졌다는 게 정말 \n놀라웠어. 왜 몇몇 사람들만 한곳에 모여 대통령을 뽑았을까?\n생각 깨우기\n유권자  선거할 권리를 가진 사람\n정권  정치 권력 \n ‌\u0007다양한 방법을 동원한 부정 선거\n유권자들에게 돈이나 물건을 제공하며 특정 후보에게 투표\n하게 하는 등 부정한 방법으로 선거를 치러 정권을 유지하려고 \n했다.\n ‌\u0007유신 헌법 공포식\n박정희 정부 시기에 유신 헌법이 공포되어 대통령의 권한이 \n이전보다 훨씬 강화되었다. 유신 헌법은 통일 주체 국민 회의\n에서 간선제로 대통령을 선출하도록 했다.\n \n \n독\n재 \n정치\n를 이\n어 가\n기 위\n한 방\n법\n애니메이션\n28\n1 평화 통일을 위한 노력, 민주화와 산업화\n\n박정희 대통령과 전두환 대통령은 군인 신분으로 군대를 동원해 권력을 \n잡았다. 유신 헌법이 공포된 이후엔 국민들이 직접 투표로 대통령을 선출할 수 \n없었고, 정부는 방송과 신문에서 독재 정치를 비판하는 기사가 나가지 못하 \n도록 막았다. 이에 학생과 시민들은 국민의 자유와 권리를 억압하는 독재 \n정치를 무너뜨리고자 민주화 운동을 일으켰다.\n내가 자유와 권리를 \n억압당한다면 어떤 \n행동을 할지 이야기\n해 봅시다.\n스스로\n해 보기\n국민의 \nㅈ\nㅇ\n과/와 \nㄱ\nㄹ\n을/를 억압하는 독재 정치를 무너뜨리기 위해 민주화 운동이 일어났다.\n한 문장 정리\n붉은색으로 표시된\n부분을 삭제하고\n기사를 내보내야\n했어.\n ‌\u0007시위를 막는 경찰들\n전두환 정부 시기에는 대학교에 전투 경찰이 들어와 학생\n들을 감시하고, 시위하는 학생들을 잡아갔다.\n ‌\u0007장발과 복장 단속\n박정희 정부 시기에는 경찰이 가위를 들고 긴 머리를 한 \n남성의 머리카락을 자르기도 했다. 또한 미니스커트를 입은 \n여성을 단속해 치마 길이가 짧으면 입지 못하게 했다.\n ‌\u0007언론 통폐합과 언론 통제\n 전두환 정부는 신문사와 방송사를 없애거나 통합해 언론을 통제했으며, 자신들에게 유리한 기사만 보도하도록 했다.\n \n \n국\n민의\n 자\n유와\n 권리\n를 억\n압한 \n사례\n광주\n십자가\n배움 확인\n29\n2   민주화와 산업화로 달라진 생활 문화\n\n4·19 혁명\n이승만 정부는 권력을 이어 나가려고 부정한 방법으로 선거에서 승리 \n했다(3·15 부정 선거). 이에 학생과 시민들이 부정 선거에 항의하며 거리에서 \n시위를 벌였다. 경찰이 시위하는 사람들을 향해 총을 쏘면서 많은 사람이 \n죽거나 다쳤다. 그러나 시위는 더욱 거세졌고, 초등학생까지 시위에 참여 \n했다. 결국 이승만은 대통령 자리에서 물러났다. 이를 4·19 혁명이라고 한다. \n민주화를 위한 노력을 살펴볼까요?\n둘\n4 ·19 혁명\n5 ·18 민주화 운동\n6월 민주 항쟁\n1960년\n1980년\n1987년\n잊을 수 없는 4월 19일\n학교에서 파하는 길에\n총알은 날아오고\n피는 길을 덮는데\n외로이 남은 책가방\n무겁기도 하더군요.\n나는 알아요. 우리는 알아요.\n엄마, 아빠 아무 말 안 해도\n오빠와 언니들이\n왜 피를 흘렸는지를\n- 강명희, 〈나는 알아요>의 일부분, \n민주화 운동 기념사업회 누리집, 2025. -\n아빠와 함께 서울특별시 강북구 수유동에 있는 국립 4 · 19 민주 묘지에 다녀 \n왔어. 그곳에서 무덤과 영정 사진을 살펴보다가 민주주의를 지키려다 희생된 사람들 중에 \n초등학생도 있다는 걸 알게 되었어. 왜 이런 슬픈 일이 벌어진 걸까?\n생각 깨우기\n누가 쓴 시일지 생각\n해 보고, 시를 읽고 \n느낀 점을 이야기해 \n봅시다. \n스스로\n해 보기\n애니메이션\n ‌\u0007시위에 참여한 초등학생들과 여성들\n30\n1 평화 통일을 위한 노력, 민주화와 산업화\n국립 4 · 19 민주 묘지\n누리집\n\n5·18 민주화 운동 \n18년간 대통령의 자리에 있던 박정희 대통령이 부하에게 죽임을 당한 \n후, 전두환을 중심으로 한 군인들이 정변을 일으켜 권력을 잡았다. 이에 \n학생과 시민들은 민주주의를 되찾기 위해 거리로 나서 시위를 벌였다.\n광주에서도 시위가 일어나자, 군인들이 시위대를 향해 총을 쏘았다. \n광주 시민들은 스스로를 지키며, 신군부에게 물러나라고 요구하는 시위를 \n이어 갔다. 군인들이 시위대를 무리하게 진압하는 과정에서 또다시 많은 \n시민이 죽거나 다쳤다. 이를 5·18 민주화 운동이라고 한다.\n정변  정권을 차지하기 위해 \n불법적이고 폭력적인 방법\n을 동원하는 것\n신군부  전두환을 중심으로 \n정변을 일으키고, 전두환 \n정부를 세우는 데에 중요한 \n역할을 했던 군인 세력\n ‌\u0007광주 금남로\n31\n2   민주화와 산업화로 달라진 생활 문화\n 우리는 왜 시민군이 되어 \n군인들과 싸울 수밖에 없었는가? \n그 대",
    "extracted_text_truncated": true
  },
  "neighbor_sections": [
    {
      "relation": "previous",
      "section_key": "social_6_1_unit1_life_8-9차시__민주화를_위한_노력을_살펴볼까요_",
      "sheet_name": "8-9차시",
      "lesson_title": "민주화를 위한 노력을 살펴볼까요?",
      "title_query": "민주화를 위한 노력을 살펴볼까요?",
      "pdf_pages": [
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
      "relation": "next",
      "section_key": "social_6_1_unit1_life_11차시__우리나라는_어떻게_산업화를_이루었을까요_",
      "sheet_name": "11차시",
      "lesson_title": "우리나라는 어떻게 산업화를 이루었을까요?",
      "title_query": "우리나라는 어떻게 산업화를 이루었을까요?",
      "pdf_pages": [
        41
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
