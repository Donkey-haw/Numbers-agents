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
  "sheet_name": "5차시",
  "card_file": "___5차시",
  "title": "지구본과 지도로 보는 세계 — 위도와 위선의 의미 알아보기",
  "badge": "5차시",
  "pdf_pages": [
    83
  ],
  "textbook_source": {
    "resource_id": "main",
    "title_query": "지구본과 지도로 보는 세계 — 위도와 위선의 의미 알아보기",
    "start_page": 83,
    "end_page": 83,
    "confidence": 0.45,
    "status": "matched"
  }
}

Baseline lesson analysis:
{
  "lesson_id": "5차시",
  "sheet_name": "5차시",
  "lesson_title": "지구본과 지도로 보는 세계 — 위도와 위선의 의미 알아보기",
  "lesson_type": "core",
  "pdf_pages": [
    83
  ],
  "essential_question": "지구본과 지도로 보는 세계 — 위도와 위선의 의미 알아보기",
  "learning_goals": [
    "지구본과 지도로 보는 세계 — 위도와 위선의 의미 알아보기의 핵심 내용을 설명할 수 있다."
  ],
  "key_concepts": [
    "지구본",
    "지도",
    "보는",
    "세계",
    "위도"
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
      "chunk_id": "5차시-chunk-1",
      "label": "학습 덩어리 1",
      "knowledge_type": "concept",
      "summary": "증인 비판적 사고력 위 재판 모습을 보고, 물음에 답해 봅시다.",
      "source_pages": [
        83
      ]
    }
  ],
  "source_page_refs": [
    83
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
      "sheet_name": "4차시",
      "lesson_title": "지구본과 지도로 보는 세계 — 디지털 공간 영상 정보의 의미 알아보기",
      "title_query": "지구본과 지도로 보는 세계 — 디지털 공간 영상 정보의 의미 알아보기"
    },
    {
      "sheet_name": "5차시",
      "lesson_title": "지구본과 지도로 보는 세계 — 위도와 위선의 의미 알아보기",
      "title_query": "지구본과 지도로 보는 세계 — 위도와 위선의 의미 알아보기"
    },
    {
      "sheet_name": "6차시",
      "lesson_title": "지구본과 지도로 보는 세계 — 경도와 경선의 의미 알아보기",
      "title_query": "지구본과 지도로 보는 세계 — 경도와 경선의 의미 알아보기"
    }
  ]
}

Section context:
{
  "schema_version": "1.0.0",
  "generated_at": "2026-03-30T15:32:45.319028+00:00",
  "pdf_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/textbook/사회/[사회]6_1_교과서.pdf",
  "current_section": {
    "section_key": "___5차시__지구본과_지도로_보는_세계___위도와_위선의_의미_알아보기",
    "sheet_name": "5차시",
    "lesson_title": "지구본과 지도로 보는 세계 — 위도와 위선의 의미 알아보기",
    "title_query": "지구본과 지도로 보는 세계 — 위도와 위선의 의미 알아보기",
    "pdf_pages": [
      83
    ],
    "baseline_analysis_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/artifacts/runs/1-20260331-001435/source/local_baseline/___5차시__지구본과_지도로_보는_세계___위도와_위선의_의미_알아보기.lesson_analysis.json",
    "extracted_text": "증인\n비판적 사고력\n 위 재판 모습을 보고, 물음에 답해 봅시다.\n재판을 통해 법원의 역할 알아보기\n스스로\n해 보기\n문제 해결력 및\n의사 결정력\n법을 어긴 사람을 \n처벌하는 재판\n5  ‌\u0007피고인이 나물의 원산지를 속여 \n부당한 이득을 얻었지만, 초범 \n이고 죄를 뉘우치고 있는 점을 \n고려해 징역 1년을 선고합니다.\n4  ‌\u0007판사님, 피고인은 비록 원산지\n를 속인 잘못을 저질렀으나, 깊이 \n반성하고 있습니다. 이 점을 \n헤아려 주시기 바랍니다.\n2  ‌\u0007피고인이 외국산 나물을 국산 \n나물 자루에 몰래 옮겨 담는 \n것을 목격했습니다.\n3  ‌\u0007많이 반성하고 있습니다. \n정말 죄송합니다.\n2\t ‌\u0007판사의 판결을 통해 문제가 어떻게 해결되었는지 이야기해 봅시다.\n1\t \u0007가~ 라에 들어갈 역할을 아래 표에서 골라 써 봅시다.\n판사\n재판을 진행하고 판결을 내리는 \n사람\n변호인\n피고인을 대신해 권리를 주장하는 \n사람\n검사\n범죄 사건을 수사하고, 피고인의 \n처벌을 요구하는 사람\n피고인\n범죄를 저지른 것으로 의심되어 \n재판을 받는 사람\n초범  처음으로 죄를 \n저지름.\n선고  판사가 판결을 \n알리는 일\n1  ‌\u0007피고인은 나물의 원산지를 \n속여 학교에 납품해 부당한 \n이득을 얻었습니다. 이에 대해 \n징역 2년을 구형합니다. \n가\n나\n다\n라\n83\n2   국가기관이 하는 일",
    "extracted_text_truncated": false
  },
  "neighbor_sections": [
    {
      "relation": "previous",
      "section_key": "___4차시__지구본과_지도로_보는_세계___디지털_공간_영상_정보의_의미_알아보기",
      "sheet_name": "4차시",
      "lesson_title": "지구본과 지도로 보는 세계 — 디지털 공간 영상 정보의 의미 알아보기",
      "title_query": "지구본과 지도로 보는 세계 — 디지털 공간 영상 정보의 의미 알아보기",
      "pdf_pages": [
        116
      ]
    },
    {
      "relation": "next",
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
