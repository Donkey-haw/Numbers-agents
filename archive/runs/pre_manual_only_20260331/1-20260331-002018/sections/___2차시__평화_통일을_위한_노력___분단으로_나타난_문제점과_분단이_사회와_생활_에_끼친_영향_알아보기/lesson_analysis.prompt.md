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
  "sheet_name": "2차시",
  "card_file": "___2차시",
  "title": "평화 통일을 위한 노력 — 분단으로 나타난 문제점과 분단이 사회와 생활 에 끼친 영향 알아보기",
  "badge": "2차시",
  "pdf_pages": [
    12,
    13,
    14,
    15
  ],
  "textbook_source": {
    "resource_id": "main",
    "title_query": "평화 통일을 위한 노력 — 분단으로 나타난 문제점과 분단이 사회와 생활 에 끼친 영향 알아보기",
    "start_page": 12,
    "end_page": 15,
    "confidence": 0.55,
    "status": "matched"
  }
}

Baseline lesson analysis:
{
  "lesson_id": "2차시",
  "sheet_name": "2차시",
  "lesson_title": "평화 통일을 위한 노력 — 분단으로 나타난 문제점과 분단이 사회와 생활 에 끼친 영향 알아보기",
  "lesson_type": "core",
  "pdf_pages": [
    12,
    13,
    14,
    15
  ],
  "essential_question": "평화 통일을 위한 노력 — 분단으로 나타난 문제점과 분단이 사회와 생활 에 끼친 영향 알아보기",
  "learning_goals": [
    "평화 통일을 위한 노력 — 분단으로 나타난 문제점과 분단이 사회와 생활 에 끼친 영향 알아보기의 핵심 내용을 설명할 수 있다."
  ],
  "key_concepts": [
    "평화",
    "통일",
    "위한",
    "노력",
    "분단"
  ],
  "vocabulary": [
    "평화",
    "통일",
    "위한"
  ],
  "misconceptions": [],
  "difficulty_band": "on-level",
  "content_chunks": [
    {
      "chunk_id": "2차시-chunk-1",
      "label": "학습 덩어리 1",
      "knowledge_type": "concept",
      "summary": "1 평화 통일을 위한 노력 분단으로 생겨난 문제점과 평화 통일의 필요성을 설명할 수 있어요.",
      "source_pages": [
        12,
        13
      ]
    },
    {
      "chunk_id": "2차시-chunk-2",
      "label": "학습 덩어리 2",
      "knowledge_type": "procedure",
      "summary": "북한의 핵 실험과 미사일 발사 등 군사적 위협이 지속되면서 한반도는 항상 군사적 충돌 위험에 놓여 있으며, 이 때문에 남북한 모두 막대한 국방비를 지출 하고 있다.",
      "source_pages": [
        14,
        15
      ]
    }
  ],
  "source_page_refs": [
    12,
    13,
    14,
    15
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
      "lesson_title": "1단원 도입 — [단원 도입] 우리 친구는 누구?",
      "title_query": "1단원 도입 — [단원 도입] 우리 친구는 누구?"
    },
    {
      "sheet_name": "2차시",
      "lesson_title": "평화 통일을 위한 노력 — 분단으로 나타난 문제점과 분단이 사회와 생활 에 끼친 영향 알아보기",
      "title_query": "평화 통일을 위한 노력 — 분단으로 나타난 문제점과 분단이 사회와 생활 에 끼친 영향 알아보기"
    },
    {
      "sheet_name": "3차시",
      "lesson_title": "평화 통일을 위한 노력 — 분단의 흔적이 남아 있는 장소 알아보기",
      "title_query": "평화 통일을 위한 노력 — 분단의 흔적이 남아 있는 장소 알아보기"
    }
  ]
}

Section context:
{
  "schema_version": "1.0.0",
  "generated_at": "2026-03-30T15:20:56.722289+00:00",
  "pdf_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/textbook/사회/[사회]6_1_교과서.pdf",
  "current_section": {
    "section_key": "___2차시__평화_통일을_위한_노력___분단으로_나타난_문제점과_분단이_사회와_생활_에_끼친_영향_알아보기",
    "sheet_name": "2차시",
    "lesson_title": "평화 통일을 위한 노력 — 분단으로 나타난 문제점과 분단이 사회와 생활 에 끼친 영향 알아보기",
    "title_query": "평화 통일을 위한 노력 — 분단으로 나타난 문제점과 분단이 사회와 생활 에 끼친 영향 알아보기",
    "pdf_pages": [
      12,
      13,
      14,
      15
    ],
    "baseline_analysis_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/artifacts/runs/1-20260331-002018/source/local_baseline/___2차시__평화_통일을_위한_노력___분단으로_나타난_문제점과_분단이_사회와_생활_에_끼친_영향_알아보기.lesson_analysis.json",
    "extracted_text": "1\n평화 통일을 \n위한 노력\n 분단으로 생겨난 문제점과 평화 통일의 필요성을 설명할 수 있어요.\n 분단과 관련된 장소를 평화의 장소로 만들려는 노력을 찾아볼 수 있어요.\n 평화 통일을 위해 우리가 할 수 있는 일을 탐색할 수 있어요.\n이 주제를 배우면 나는\n이 산책로에 있는\n푯말은 무엇을 의미할까?\n1\n10\n1 평화 통일을 위한 노력, 민주화와 산업화\n\n1  낱말 구름을 보고, 이 주제에서 배울 내용이 무엇인지 생각해 봅시다.\n2  낱말 구름에 있는 낱말 9개를 골라서 빙고 놀이를 해 봅시다.\n평화 통일\n분단\n협력\n화해\n전쟁\n남한\n북한\n비무장 지대\n교류\n대립\n이산가족\n남북 정상 회담\n휴전선\n북한 이탈 주민\n문화 차이\n이 사람들이 들고 있는\n깃발은 무엇을\n상징할까?\n2\n11\n1   평화 통일을 위한 노력\n\n북한의 핵 실험과 미사일 발사 등 군사적 위협이 \n지속되면서 한반도는 항상 군사적 충돌 위험에 놓여 \n있으며, 이 때문에 남북한 모두 막대한 국방비를 지출\n하고 있다. 남북 간 군사적 대립은 전쟁 발생에 대한 \n불안감을 일으키며, 동아시아와 세계 평화\n에도 심각한 위협이 되고 있다.\n군사적 긴장\n분단으로 어떤 문제가 발생했을까요?\n하나\n한반도는 광복 후 분단되었고, 6·25 전쟁 이후 분단 상황이 굳어졌다. \n70년이 넘는 긴 세월 동안 남북 간 적대 관계가 지속되었으며, 사회·문화적 \n차이가 커지는 등 여러 가지 문제점이 나타났다.\n북한 이탈 주민들이 출연하는 방송을 보고 있었는데, 출연자 중 한 사람이 “일 \n없습니다.”라고 하는 거야. ‘할 일이 없다.’라는 뜻인지 궁금해서 고개를 갸웃했더니, 아빠 \n께서 ‘괜찮다.’라는 뜻이라고 알려 주셨어. 남북한 사람들은 같은 민족인데, 왜 서로 다른 말이 \n있는 걸까?\n생각 깨우기\n  \n   \n   \n   \n분단\n으로\n 생\n긴 문\n제점\n(년)\n0\n10\n20\n30\n40\n50\n60\n(조 원)\n59\n50\n29\n20\n14\n2000\n2024\n2020\n2015\n2010\n2005\n37\n(국방부, 2024.)\n속보, 북한 미사일 발사\n 남북한 대립으로 인한 국방비 증가\n애니메이션\n12\n1 평화 통일을 위한 노력, 민주화와 산업화\n\n남북한 사람들은 오랫동안 서로 다른 \n체제 속에서 살아오면서 언어와 생활 방식에 \n차이가 생겼다. 북한 이탈 주민들도 남한 \n사회에 적응하는 과정에서 문화 차이로 여러 \n가지 어려움을 겪고 있다.\n문화 차이\n빙수\n단얼음\n도\n시\n락\n곽\n밥\n단얼음?\n도시락?\n곽밥?\n빙수?\n분단으로 생겨난 문제점을 살펴\n보고 평화 통일이 필요한 이유를 \n활동 자료2  에 써 봅시다. \n스스로\n해 보기\n분단으로 군사적 긴장, 자유 왕래의 어려움, 남북한 \nㅁ\nㅎ\n 차이 등 다양한 문제가 생겼다. \n한 문장 정리\n남북 분단으로 헤어진 이산가족들은 오랜 \n세월 서로 만나지 못한 채 지내 왔고, 많은 \n사람이 결국 가족들을 만나지 못하고 세상을 \n떠났다. 북한 이탈 주민들도 고향에 있는 \n가족들을 자유롭게 만날 수 없다.\n자유 왕래의 어려움\n \u00072007년 북에서 출발해 남으로 시범 운행\n되었지만, 지금은 중단된 동해선 열차\n ‌\u0007북쪽에 고향을 둔 실향민과 이산가족이 \n명절에 합동 차례를 지내는 망배단\n고향에 있는 가족들을 \n자유롭게 만날 수 있으면 \n좋을 텐데…….\n배움 확인\n13\n1   평화 통일을 위한 노력",
    "extracted_text_truncated": false
  },
  "neighbor_sections": [
    {
      "relation": "previous",
      "section_key": "___1차시__1단원_도입____단원_도입__우리_친구는_누구_",
      "sheet_name": "1차시",
      "lesson_title": "1단원 도입 — [단원 도입] 우리 친구는 누구?",
      "title_query": "1단원 도입 — [단원 도입] 우리 친구는 누구?",
      "pdf_pages": [
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11
      ]
    },
    {
      "relation": "next",
      "section_key": "___3차시__평화_통일을_위한_노력___분단의_흔적이_남아_있는_장소_알아보기",
      "sheet_name": "3차시",
      "lesson_title": "평화 통일을 위한 노력 — 분단의 흔적이 남아 있는 장소 알아보기",
      "title_query": "평화 통일을 위한 노력 — 분단의 흔적이 남아 있는 장소 알아보기",
      "pdf_pages": [
        16
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
