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
  "sheet_name": "9-10차시",
  "card_file": "___9-10차시",
  "title": "국가기관이 하는 일 — 국회의 구성과 하는 일 파악하기",
  "badge": "9-10차시",
  "pdf_pages": [
    74
  ],
  "textbook_source": {
    "resource_id": "main",
    "title_query": "국가기관이 하는 일 — 국회의 구성과 하는 일 파악하기",
    "start_page": 74,
    "end_page": 74,
    "confidence": 0.45,
    "status": "matched"
  }
}

Baseline lesson analysis:
{
  "lesson_id": "9-10차시",
  "sheet_name": "9-10차시",
  "lesson_title": "국가기관이 하는 일 — 국회의 구성과 하는 일 파악하기",
  "lesson_type": "core",
  "pdf_pages": [
    74
  ],
  "essential_question": "국가기관이 하는 일 — 국회의 구성과 하는 일 파악하기",
  "learning_goals": [
    "국가기관이 하는 일 — 국회의 구성과 하는 일 파악하기의 핵심 내용을 설명할 수 있다."
  ],
  "key_concepts": [
    "국가기관",
    "하는",
    "국회",
    "구성",
    "파악하기"
  ],
  "vocabulary": [
    "국가기관",
    "하는",
    "국회"
  ],
  "misconceptions": [
    "선거를 단순히 사람을 뽑는 행사로만 이해할 수 있다.",
    "민주주의의 핵심이 참여보다 결과에만 있다고 오해할 수 있다."
  ],
  "difficulty_band": "on-level",
  "content_chunks": [
    {
      "chunk_id": "9-10차시-chunk-1",
      "label": "학습 덩어리 1",
      "knowledge_type": "concept",
      "summary": "국회의 구성과 하는 일 국회는 국회의원들로 구성된 국민의 대표 기관이다.",
      "source_pages": [
        74
      ]
    }
  ],
  "source_page_refs": [
    74
  ],
  "analysis_confidence": 0.75,
  "notes": "자동 생성 초안. lesson title, key concepts, chunks를 검토 후 승인 필요."
}

Schedule draft:
{
  "schema_version": "1.0.0",
  "generated_at": "2026-03-30T15:16:59.267020+00:00",
  "sections": [
    {
      "sheet_name": "8차시",
      "lesson_title": "국가기관이 하는 일 — [주제 도입] 열려라 이야기 / 외쳐라 빙고",
      "title_query": "국가기관이 하는 일 — [주제 도입] 열려라 이야기 / 외쳐라 빙고"
    },
    {
      "sheet_name": "9-10차시",
      "lesson_title": "국가기관이 하는 일 — 국회의 구성과 하는 일 파악하기",
      "title_query": "국가기관이 하는 일 — 국회의 구성과 하는 일 파악하기"
    },
    {
      "sheet_name": "11차시",
      "lesson_title": "국가기관이 하는 일 — 행정부의 구성과 하는 일 파악하기",
      "title_query": "국가기관이 하는 일 — 행정부의 구성과 하는 일 파악하기"
    }
  ]
}

Section context:
{
  "schema_version": "1.0.0",
  "generated_at": "2026-03-30T15:26:22.024041+00:00",
  "pdf_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/textbook/사회/[사회]6_1_교과서.pdf",
  "current_section": {
    "section_key": "___9-10차시__국가기관이_하는_일___국회의_구성과_하는_일_파악하기",
    "sheet_name": "9-10차시",
    "lesson_title": "국가기관이 하는 일 — 국회의 구성과 하는 일 파악하기",
    "title_query": "국가기관이 하는 일 — 국회의 구성과 하는 일 파악하기",
    "pdf_pages": [
      74
    ],
    "baseline_analysis_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/artifacts/runs/1-20260331-001652/source/local_baseline/___9-10차시__국가기관이_하는_일___국회의_구성과_하는_일_파악하기.lesson_analysis.json",
    "extracted_text": "국회의 구성과 하는 일\n국회는 국회의원들로 구성된 국민의 대표 기관이다. 국회의원은 선거로 \n선출된 국민의 대표로, 임기는 4년이다.\n국회는 법을 만들고 고치는 일을 한다. 민주 국가에서 법은 국가가 권력을 \n행사하는 근거가 되기 때문에 국민의 뜻에 따라 만들어져야 한다. 따라서 \n법을 만들고 고치는 일은 국회가 하는 일 중 가장 중요하다.\n국회는 어떤 일을 할까요?\n둘\n어린이 기자단 활동을 하려고 녹음기를 샀어. 그런데 선생님께서 녹음기 구석\n구석을 살펴보시는 거야. 궁금해서 여쭤보니, 우리나라에서 검증된 안전한 물건에는  표시를 \n붙이는 법이 있대. 다행히 내가 산 녹음기에도 그 표시가 있어서 마음이 놓였어. 그런데 이런 \n법은 누가, 어떻게 만드는 걸까?\n생각 깨우기\n발언대\n국회의원이 본회의에서 \n공식 발언을 하는 자리이다.\n대형 전광판\n국회의원들의 투표 결과나 \n발언대에서 발언하는 사람 \n등을 보여 준다.\n국회의원석\n국회의원들이 책상에 있는 컴퓨터\n로 전자 투표를 하는 곳이다.\n국회 의사당의 본회의장은 \n국회의원들이 모여 회의를 하거나 \n투표를 하는 곳이야.\n본회의  국회의 의사를 최종\n적으로 결정하는 회의\n국\n회 \n의\n사\n당\n의 \n본회\n의장\n애니메이션\n74\n2 민주주의와 시민 참여",
    "extracted_text_truncated": false
  },
  "neighbor_sections": [
    {
      "relation": "previous",
      "section_key": "___8차시__국가기관이_하는_일____주제_도입__열려라_이야기___외쳐라_빙고",
      "sheet_name": "8차시",
      "lesson_title": "국가기관이 하는 일 — [주제 도입] 열려라 이야기 / 외쳐라 빙고",
      "title_query": "국가기관이 하는 일 — [주제 도입] 열려라 이야기 / 외쳐라 빙고",
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
        73
      ]
    },
    {
      "relation": "next",
      "section_key": "___11차시__국가기관이_하는_일___행정부의_구성과_하는_일_파악하기",
      "sheet_name": "11차시",
      "lesson_title": "국가기관이 하는 일 — 행정부의 구성과 하는 일 파악하기",
      "title_query": "국가기관이 하는 일 — 행정부의 구성과 하는 일 파악하기",
      "pdf_pages": [
        74
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
