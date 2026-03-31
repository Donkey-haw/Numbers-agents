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
  "sheet_name": "12차시",
  "card_file": "___12차시",
  "title": "국가기관이 하는 일 — 법원의 구성과 하는 일 파악하기",
  "badge": "12차시",
  "pdf_pages": [
    73
  ],
  "textbook_source": {
    "resource_id": "main",
    "title_query": "국가기관이 하는 일 — 법원의 구성과 하는 일 파악하기",
    "start_page": 73,
    "end_page": 73,
    "confidence": 0.45,
    "status": "matched"
  }
}

Baseline lesson analysis:
{
  "lesson_id": "12차시",
  "sheet_name": "12차시",
  "lesson_title": "국가기관이 하는 일 — 법원의 구성과 하는 일 파악하기",
  "lesson_type": "core",
  "pdf_pages": [
    73
  ],
  "essential_question": "국가기관이 하는 일 — 법원의 구성과 하는 일 파악하기",
  "learning_goals": [
    "국가기관이 하는 일 — 법원의 구성과 하는 일 파악하기의 핵심 내용을 설명할 수 있다."
  ],
  "key_concepts": [
    "국가기관",
    "하는",
    "법원",
    "구성",
    "파악하기"
  ],
  "vocabulary": [
    "국가기관",
    "하는",
    "법원"
  ],
  "misconceptions": [],
  "difficulty_band": "on-level",
  "content_chunks": [
    {
      "chunk_id": "12차시-chunk-1",
      "label": "학습 덩어리 1",
      "knowledge_type": "cause-effect",
      "summary": "민주 국가에서 나랏일을 하는 ㄱ ㅎ , ㅎ ㅈ ㅂ , ㅂ ㅇ 을/를 국가기관이라고 한다.",
      "source_pages": [
        73
      ]
    }
  ],
  "source_page_refs": [
    73
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
      "sheet_name": "11차시",
      "lesson_title": "국가기관이 하는 일 — 행정부의 구성과 하는 일 파악하기",
      "title_query": "국가기관이 하는 일 — 행정부의 구성과 하는 일 파악하기"
    },
    {
      "sheet_name": "12차시",
      "lesson_title": "국가기관이 하는 일 — 법원의 구성과 하는 일 파악하기",
      "title_query": "국가기관이 하는 일 — 법원의 구성과 하는 일 파악하기"
    },
    {
      "sheet_name": "13차시",
      "lesson_title": "국가기관이 하는 일 — 권력 분립의 의미와 중요성 탐구하기",
      "title_query": "국가기관이 하는 일 — 권력 분립의 의미와 중요성 탐구하기"
    }
  ]
}

Section context:
{
  "schema_version": "1.0.0",
  "generated_at": "2026-03-30T15:26:31.356266+00:00",
  "pdf_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/textbook/사회/[사회]6_1_교과서.pdf",
  "current_section": {
    "section_key": "___12차시__국가기관이_하는_일___법원의_구성과_하는_일_파악하기",
    "sheet_name": "12차시",
    "lesson_title": "국가기관이 하는 일 — 법원의 구성과 하는 일 파악하기",
    "title_query": "국가기관이 하는 일 — 법원의 구성과 하는 일 파악하기",
    "pdf_pages": [
      73
    ],
    "baseline_analysis_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/artifacts/runs/1-20260331-001435/source/local_baseline/___12차시__국가기관이_하는_일___법원의_구성과_하는_일_파악하기.lesson_analysis.json",
    "extracted_text": "민주 국가에서 나랏일을 하는 \nㄱ\nㅎ\n , \nㅎ\nㅈ\nㅂ\n , \nㅂ\nㅇ\n 을/를 국가기관이라고 한다.\n한 문장 정리\n법원\n3\n이곳은 우리나라 최고 법원인 \n대법원이야. 가운데 건물은 법원의 \n독립을, 양옆의 건물은 정의와 \n형평을 상징해.\n이곳은 행정부 기관들이 \n자리한 정부 세종 청사야. 하늘로 \n오르는 용의 모습을 본떠 만들었어.\n행정부\n2\n형평  균형이 맞음.\n대법원 입구에는 법원이 \n지키고 보호하고자 하는 가치인 \n자유, 평등, 정의를 적어 두어 \n사람들이 오갈 때마다 볼 수 \n있도록 했어.\n배움 확인\n73\n2   국가기관이 하는 일",
    "extracted_text_truncated": false
  },
  "neighbor_sections": [
    {
      "relation": "previous",
      "section_key": "___11차시__국가기관이_하는_일___행정부의_구성과_하는_일_파악하기",
      "sheet_name": "11차시",
      "lesson_title": "국가기관이 하는 일 — 행정부의 구성과 하는 일 파악하기",
      "title_query": "국가기관이 하는 일 — 행정부의 구성과 하는 일 파악하기",
      "pdf_pages": [
        74
      ]
    },
    {
      "relation": "next",
      "section_key": "___13차시__국가기관이_하는_일___권력_분립의_의미와_중요성_탐구하기",
      "sheet_name": "13차시",
      "lesson_title": "국가기관이 하는 일 — 권력 분립의 의미와 중요성 탐구하기",
      "title_query": "국가기관이 하는 일 — 권력 분립의 의미와 중요성 탐구하기",
      "pdf_pages": [
        54
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
