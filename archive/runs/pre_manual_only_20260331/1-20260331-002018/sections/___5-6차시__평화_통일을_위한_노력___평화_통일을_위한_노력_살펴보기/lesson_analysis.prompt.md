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
  "sheet_name": "5-6차시",
  "card_file": "___5-6차시",
  "title": "평화 통일을 위한 노력 — 평화 통일을 위한 노력 살펴보기",
  "badge": "5-6차시",
  "pdf_pages": [
    10,
    11,
    12
  ],
  "textbook_source": {
    "resource_id": "main",
    "title_query": "평화 통일을 위한 노력 — 평화 통일을 위한 노력 살펴보기",
    "start_page": 10,
    "end_page": 12,
    "confidence": 0.55,
    "status": "matched"
  }
}

Baseline lesson analysis:
{
  "lesson_id": "5-6차시",
  "sheet_name": "5-6차시",
  "lesson_title": "평화 통일을 위한 노력 — 평화 통일을 위한 노력 살펴보기",
  "lesson_type": "core",
  "pdf_pages": [
    10,
    11,
    12
  ],
  "essential_question": "평화 통일을 위한 노력 — 평화 통일을 위한 노력 살펴보기",
  "learning_goals": [
    "평화 통일을 위한 노력 — 평화 통일을 위한 노력 살펴보기의 핵심 내용을 설명할 수 있다."
  ],
  "key_concepts": [
    "평화",
    "통일",
    "위한",
    "노력",
    "살펴보기"
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
      "chunk_id": "5-6차시-chunk-1",
      "label": "학습 덩어리 1",
      "knowledge_type": "concept",
      "summary": "1 평화 통일을 위한 노력 1 민주화와 산업화로 달라진 생활 문화 2 분 단 평화 통 일 민 주화 산업 화 평화 통일을 위한 노력, 민주화와 산업화 애니메이션",
      "source_pages": [
        10
      ]
    },
    {
      "chunk_id": "5-6차시-chunk-2",
      "label": "학습 덩어리 2",
      "knowledge_type": "concept",
      "summary": "사람들의 이야기를 듣고, 나와 함께 이 단원을 공부할 내 친구 하나를 찾아 줘.",
      "source_pages": [
        11,
        12
      ]
    }
  ],
  "source_page_refs": [
    10,
    11,
    12
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
      "sheet_name": "4차시",
      "lesson_title": "평화 통일을 위한 노력 — 분단의 장소가 평화의 장소로 바뀐 사례 알아보기",
      "title_query": "평화 통일을 위한 노력 — 분단의 장소가 평화의 장소로 바뀐 사례 알아보기"
    },
    {
      "sheet_name": "5-6차시",
      "lesson_title": "평화 통일을 위한 노력 — 평화 통일을 위한 노력 살펴보기",
      "title_query": "평화 통일을 위한 노력 — 평화 통일을 위한 노력 살펴보기"
    },
    {
      "sheet_name": "7차시",
      "lesson_title": "민주화와 산업화로 달라진 생활 문화 — [주제 도입] 열려라 이야기 / 외쳐라 빙고",
      "title_query": "민주화와 산업화로 달라진 생활 문화 — [주제 도입] 열려라 이야기 / 외쳐라 빙고"
    }
  ]
}

Section context:
{
  "schema_version": "1.0.0",
  "generated_at": "2026-03-30T15:22:55.019731+00:00",
  "pdf_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/textbook/사회/[사회]6_1_교과서.pdf",
  "current_section": {
    "section_key": "___5-6차시__평화_통일을_위한_노력___평화_통일을_위한_노력_살펴보기",
    "sheet_name": "5-6차시",
    "lesson_title": "평화 통일을 위한 노력 — 평화 통일을 위한 노력 살펴보기",
    "title_query": "평화 통일을 위한 노력 — 평화 통일을 위한 노력 살펴보기",
    "pdf_pages": [
      10,
      11,
      12
    ],
    "baseline_analysis_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/artifacts/runs/1-20260331-002018/source/local_baseline/___5-6차시__평화_통일을_위한_노력___평화_통일을_위한_노력_살펴보기.lesson_analysis.json",
    "extracted_text": "1\n평화 통일을 위한 노력\n1\n민주화와 산업화로 달라진 생활 문화\n2\n  \n   \n    \n    \n     \n    \n 분\n단  \n평화\n 통\n일 \n 민\n주화\n  \n산업\n화  \n평화 통일을 위한 \n노력, 민주화와 \n산업화\n애니메이션\n\n사람들의 이야기를 듣고, 나와 함께 이 단원을 공부할 \n내 친구 하나를 찾아 줘.\n평화 통일 캠페인 전시관에서 받은 한반도기를 \n들고 있어. \n전시회에서 다양한 자료를 받아 간다며 큰 배낭\n을 메고 왔던데?\n나와 가발 만들기 체험을 하고, 또 다른 체험을 \n경험해 보고 싶다고 했어.\n\n1\n평화 통일을 \n위한 노력\n 분단으로 생겨난 문제점과 평화 통일의 필요성을 설명할 수 있어요.\n 분단과 관련된 장소를 평화의 장소로 만들려는 노력을 찾아볼 수 있어요.\n 평화 통일을 위해 우리가 할 수 있는 일을 탐색할 수 있어요.\n이 주제를 배우면 나는\n이 산책로에 있는\n푯말은 무엇을 의미할까?\n1\n10\n1 평화 통일을 위한 노력, 민주화와 산업화",
    "extracted_text_truncated": false
  },
  "neighbor_sections": [
    {
      "relation": "previous",
      "section_key": "___4차시__평화_통일을_위한_노력___분단의_장소가_평화의_장소로_바뀐_사례_알아보기",
      "sheet_name": "4차시",
      "lesson_title": "평화 통일을 위한 노력 — 분단의 장소가 평화의 장소로 바뀐 사례 알아보기",
      "title_query": "평화 통일을 위한 노력 — 분단의 장소가 평화의 장소로 바뀐 사례 알아보기",
      "pdf_pages": [
        12
      ]
    },
    {
      "relation": "next",
      "section_key": "___7차시__민주화와_산업화로_달라진_생활_문화____주제_도입__열려라_이야기___외쳐라_빙고",
      "sheet_name": "7차시",
      "lesson_title": "민주화와 산업화로 달라진 생활 문화 — [주제 도입] 열려라 이야기 / 외쳐라 빙고",
      "title_query": "민주화와 산업화로 달라진 생활 문화 — [주제 도입] 열려라 이야기 / 외쳐라 빙고",
      "pdf_pages": [
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
