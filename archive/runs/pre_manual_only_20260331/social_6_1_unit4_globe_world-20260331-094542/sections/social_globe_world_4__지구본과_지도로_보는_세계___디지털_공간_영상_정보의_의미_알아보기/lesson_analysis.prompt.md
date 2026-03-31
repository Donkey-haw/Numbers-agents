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
  "sheet_name": "4차시",
  "card_file": "social_globe_world_4",
  "title": "지구본과 지도로 보는 세계 — 디지털 공간 영상 정보의 의미 알아보기",
  "badge": "4차시",
  "pdf_pages": [
    116
  ],
  "textbook_source": {
    "resource_id": "main",
    "title_query": "디지털 공간 영상 정보의 의미 알아보기",
    "start_page": 116,
    "end_page": 116,
    "confidence": 0.45,
    "status": "matched"
  }
}

Baseline lesson analysis:
{
  "lesson_id": "4차시",
  "sheet_name": "4차시",
  "lesson_title": "지구본과 지도로 보는 세계 — 디지털 공간 영상 정보의 의미 알아보기",
  "lesson_type": "core",
  "pdf_pages": [
    116
  ],
  "essential_question": "지구본과 지도로 보는 세계 — 디지털 공간 영상 정보의 의미 알아보기",
  "learning_goals": [
    "지구본과 지도로 보는 세계 — 디지털 공간 영상 정보의 의미 알아보기의 핵심 내용을 설명할 수 있다."
  ],
  "key_concepts": [
    "지구본",
    "지도",
    "보는",
    "세계",
    "디지털"
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
      "chunk_id": "4차시-chunk-1",
      "label": "학습 덩어리 1",
      "knowledge_type": "concept",
      "summary": "아시아 대한 민국 대한 민국 아시아 태 평 양 동해 황해 남해 3D 레이어 역사적인 이미지 지구의 과거 모습을 담은 이미지를 확인해 보세요.",
      "source_pages": [
        116
      ]
    }
  ],
  "source_page_refs": [
    116
  ],
  "analysis_confidence": 0.75,
  "notes": "자동 생성 초안. lesson title, key concepts, chunks를 검토 후 승인 필요."
}

Schedule draft:
{
  "schema_version": "1.0.0",
  "generated_at": "2026-03-31T00:45:48.010650+00:00",
  "sections": [
    {
      "sheet_name": "2-3차시",
      "lesson_title": "지구본과 지도로 보는 세계 — 지구본의 특징 살펴보기",
      "title_query": "지구본의 특징 살펴보기"
    },
    {
      "sheet_name": "4차시",
      "lesson_title": "지구본과 지도로 보는 세계 — 디지털 공간 영상 정보의 의미 알아보기",
      "title_query": "디지털 공간 영상 정보의 의미 알아보기"
    },
    {
      "sheet_name": "5차시",
      "lesson_title": "지구본과 지도로 보는 세계 — 위도와 위선의 의미 알아보기",
      "title_query": "위도와 위선의 의미 알아보기"
    }
  ]
}

Section context:
{
  "schema_version": "1.0.0",
  "generated_at": "2026-03-31T00:45:51.057099+00:00",
  "pdf_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/textbook/사회/[사회]6_1_교과서.pdf",
  "current_section": {
    "section_key": "social_globe_world_4__지구본과_지도로_보는_세계___디지털_공간_영상_정보의_의미_알아보기",
    "sheet_name": "4차시",
    "lesson_title": "지구본과 지도로 보는 세계 — 디지털 공간 영상 정보의 의미 알아보기",
    "title_query": "디지털 공간 영상 정보의 의미 알아보기",
    "pdf_pages": [
      116
    ],
    "baseline_analysis_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/artifacts/runs/social_6_1_unit4_globe_world-20260331-094542/source/local_baseline/social_globe_world_4__지구본과_지도로_보는_세계___디지털_공간_영상_정보의_의미_알아보기.lesson_analysis.json",
    "extracted_text": "아시아\n대한\n민국\n대한\n민국\n아시아\n태 평 양\n동해\n황해\n남해\n3D\n레이어\n역사적인 이미지\n지구의 과거 모습을 담은\n이미지를 확인해 보세요.\n사진\n전 세계의 사진을 둘러보세요.\n검색\n디지털 공간 영상 정보로 세계를 \n살펴볼까요?\n둘\n아린이가 내게 가 보고 싶은 나라가 어디냐고 물었어. 난 프랑스라고 대답했지. \n 그러자 아린이가 프랑스 파리에 있는 에펠 탑 주변에 무엇이 있는지 아주 자세히 설명해 \n줬어. 그런데 알고 보니 아린이는 파리에 가 본 적이 없대. 아린이는 어떻게 가 보지도 않은 곳\n을 자세히 아는 걸까?\n생각 깨우기\n디지\n털 지\n구본\n거리·면적 재기\n두 지점 사이의 거리\n나 지역의 면적을 잴 \n수 있다.\n지구본처럼 \n입체적으로 \n살펴볼 수 있어.\n시간의 흐름에 따른 변화 보기\n시간의 흐름에 따라 장소\n를 살펴볼 수 있다.\n추가 레이어를 이용하면 전 세계의 \n과거 모습, 실제 사진 등을 볼 수 있다.\n다음 기능은 디지털 지구본과 디지털 \n세계지도에서 모두 이용할 수 있어!\n찾고 싶은 장소를 입력하면 위치를 표시하고, 관련 정보를 알려 준다.\n실제 길 위를 지나는 것처럼 장소의 모습을 볼 수 있다.\n확대하거나 축소하며 축척을 다르게 할 수 있다.\n현재 나의 위치를 표시해 준다.\n검색하기\n거리 보기\n확대와 축소\n위치 확인\n입체 영상 보기\n  장소의 모습\n을 입체 영상\n으로 볼 수 \n있다.\n지도 위 정보 표시하기\n지도에 나타날 정보를 선택하는 \n기능으로, 경계선, 장소, 도로 등\n을 표시할 수 있다.\n애니메이션\n116\n3 지구, 대륙 그리고 국가들",
    "extracted_text_truncated": false
  },
  "neighbor_sections": [
    {
      "relation": "previous",
      "section_key": "social_globe_world_2_3__지구본과_지도로_보는_세계___지구본의_특징_살펴보기",
      "sheet_name": "2-3차시",
      "lesson_title": "지구본과 지도로 보는 세계 — 지구본의 특징 살펴보기",
      "title_query": "지구본의 특징 살펴보기",
      "pdf_pages": [
        112,
        113,
        114,
        115
      ]
    },
    {
      "relation": "next",
      "section_key": "social_globe_world_5__지구본과_지도로_보는_세계___위도와_위선의_의미_알아보기",
      "sheet_name": "5차시",
      "lesson_title": "지구본과 지도로 보는 세계 — 위도와 위선의 의미 알아보기",
      "title_query": "위도와 위선의 의미 알아보기",
      "pdf_pages": [
        83
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
