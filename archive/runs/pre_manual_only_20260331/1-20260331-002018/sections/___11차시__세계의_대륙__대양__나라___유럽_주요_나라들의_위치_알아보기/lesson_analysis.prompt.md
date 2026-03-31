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
  "sheet_name": "11차시",
  "card_file": "___11차시",
  "title": "세계의 대륙, 대양, 나라 — 유럽 주요 나라들의 위치 알아보기",
  "badge": "11차시",
  "pdf_pages": [
    128,
    129,
    130
  ],
  "textbook_source": {
    "resource_id": "main",
    "title_query": "세계의 대륙, 대양, 나라 — 유럽 주요 나라들의 위치 알아보기",
    "start_page": 128,
    "end_page": 130,
    "confidence": 0.55,
    "status": "matched"
  }
}

Baseline lesson analysis:
{
  "lesson_id": "11차시",
  "sheet_name": "11차시",
  "lesson_title": "세계의 대륙, 대양, 나라 — 유럽 주요 나라들의 위치 알아보기",
  "lesson_type": "core",
  "pdf_pages": [
    128,
    129,
    130
  ],
  "essential_question": "세계의 대륙, 대양, 나라 — 유럽 주요 나라들의 위치 알아보기",
  "learning_goals": [
    "세계의 대륙, 대양, 나라 — 유럽 주요 나라들의 위치 알아보기의 핵심 내용을 설명할 수 있다."
  ],
  "key_concepts": [
    "세계",
    "대륙",
    "대양",
    "유럽",
    "주요"
  ],
  "vocabulary": [
    "세계",
    "대륙",
    "대양"
  ],
  "misconceptions": [],
  "difficulty_band": "on-level",
  "content_chunks": [
    {
      "chunk_id": "11차시-chunk-1",
      "label": "학습 덩어리 1",
      "knowledge_type": "concept",
      "summary": "세계 여러 나라의 위치는 위도와 경도를 이용해 보다",
      "source_pages": [
        128
      ]
    },
    {
      "chunk_id": "11차시-chunk-2",
      "label": "학습 덩어리 2",
      "knowledge_type": "comparison",
      "summary": "정보 활용 능력 위도와 경도를 이용해 위치 표현하기 스스로 해 보기 위도와 경도를 이용하면 지구상에서의 ㅇ ㅊ 을/를 알 수 있다.",
      "source_pages": [
        129,
        130
      ]
    }
  ],
  "source_page_refs": [
    128,
    129,
    130
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
      "sheet_name": "10차시",
      "lesson_title": "세계의 대륙, 대양, 나라 — 아시아 주요 나라들의 위치 알아보기",
      "title_query": "세계의 대륙, 대양, 나라 — 아시아 주요 나라들의 위치 알아보기"
    },
    {
      "sheet_name": "11차시",
      "lesson_title": "세계의 대륙, 대양, 나라 — 유럽 주요 나라들의 위치 알아보기",
      "title_query": "세계의 대륙, 대양, 나라 — 유럽 주요 나라들의 위치 알아보기"
    },
    {
      "sheet_name": "12차시",
      "lesson_title": "세계의 대륙, 대양, 나라 — 북아메리카와 남아메리카 주요 나라들의 위치 알아보기",
      "title_query": "세계의 대륙, 대양, 나라 — 북아메리카와 남아메리카 주요 나라들의 위치 알아보기"
    }
  ]
}

Section context:
{
  "schema_version": "1.0.0",
  "generated_at": "2026-03-30T15:37:37.530466+00:00",
  "pdf_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/textbook/사회/[사회]6_1_교과서.pdf",
  "current_section": {
    "section_key": "___11차시__세계의_대륙__대양__나라___유럽_주요_나라들의_위치_알아보기",
    "sheet_name": "11차시",
    "lesson_title": "세계의 대륙, 대양, 나라 — 유럽 주요 나라들의 위치 알아보기",
    "title_query": "세계의 대륙, 대양, 나라 — 유럽 주요 나라들의 위치 알아보기",
    "pdf_pages": [
      128,
      129,
      130
    ],
    "baseline_analysis_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/artifacts/runs/1-20260331-002018/source/local_baseline/___11차시__세계의_대륙__대양__나라___유럽_주요_나라들의_위치_알아보기.lesson_analysis.json",
    "extracted_text": "세계 여러 나라의 위치는 위도와 경도를 이용해 보다 정확하게 나타낼 \n수 있다. 위도와 경도로 표현된 위치를 알면 그 나라가 지구상에서 어디에 \n있는지 알 수 있고, 그 나라의 시간대도 파악할 수 있다.\n위도와 경도로 위치를 표현해 \n볼까요?\n다섯\n비행기 조종사가 꿈인 나는 오늘도 열심히 비행기와 관련된 자료를 찾아보고 \n있어. 그런데 말이야, 궁금한 게 생겼어. 하늘에는 길이 없는데, 비행기는 어떻게 길을 잃지 \n않고 목적지를 찾아가는 걸까?\n생각 깨우기\n 지\n구본과\n 세계지\n도에서 위\n치 찾기\n \n디지\n털 공간 \n영상 정보\n에서 위치\n 찾기\n \n지구본과 세계지도에서 위선과 경선을 찾아 대략\n적인 위치를 확인한다.\n동경 10°\n동경 20°\n남위 20°\n남위 30°\n앙골라\n남아프리카\n공화국\n잠비아\n나미비아\n보츠와나\n0\n400km\n위치를 알고 싶은 곳에 마우스를 올려놓고 \n오른쪽 단추를 눌러 위도와 경도를 확인한다.\n동경 10°\n동경 20°\n남위 20°\n남위 30°\n앙골라\n남아프리카\n공화국\n나미비아\n보츠와나\n잠비아\n-17, 25\n위치 측정\n0\n400km\n       나미비아의 \n         남쪽 끝은 남위 30° \n            가까이에 있어. \n             그러니까 남위 29° \n               정도 되겠구나.\n나미비아의 동쪽 \n끝은 동경 25°에\n있어.\n디지털 공간 영상 정보의 \n숫자 앞에 ‘-’ 표시는 \n남위 또는 서경을 뜻해.\n애니메이션\n128\n3 지구, 대륙 그리고 국가들\n\n정보 활용 능력\n위도와 경도를 이용해 위치 표현하기\n스스로\n해 보기\n위도와 경도를 이용하면 지구상에서의 \nㅇ\nㅊ\n 을/를 알 수 있다.\n한 문장 정리\n  다양한 공간 자료를 이용해 여러 나라의 위치를 알아봅시다.\n1\t \u0007다음 조건에 위치하는 나라를 찾아 써 봅시다.\n북위 30°, 동경 60° \n이란\n북위 60°, 서경 120° \n남위 30°, 동경 20° \n2\t \u0007위도와 경도를 이용해 나라의 위치를 설명해 봅시다. \n0\n200km\n독일\n프랑스\n에스파냐\n1  ‌\u0007위치를 나타내고 싶은 나라를 \n선택합니다.\n2  ‌\u00071  에서 선택한 나라의 동, 서, \n남, 북 끝 지점을 찾습니다.\n3  ‌\u0007남쪽과 북쪽 끝의 위도를 읽습\n니다.\n4  ‌\u0007동쪽과 서쪽 끝의 경도를 읽습\n니다.\n5  ‌\u0007위도와 경도로 위치를 표현 \n합니다. \n활동 방법\n프랑스는 대략 북위 41°~51°, 서경 5°~동경 10° 사이에 있습니다.\n예시\n내가 선택한 나라\n선택한 나라의 위치\n동쪽 끝\n남쪽 끝\n북쪽 끝\n서쪽 끝\n배움 확인\n129\n1   지구본과 지도로 보는 세계\n\n표준시는 본초 자오선(경도 0°)을 기준으로 동쪽으로 15°씩 이동할 때마다 한 시간씩 \n빨라지고, 서쪽으로 15°씩 이동할 때마다 한 시간씩 느려진다. 영토가 동서로 긴 나라들은 \n한 나라 안에서 여러 개의 표준시를 사용하거나, 편의에 따라 표준시를 조정하기도 한다.\n과거 중국은 지역별로 5개의 시간대가 있었는데, 편의를 위해 수도인 베이징을 기준으로 \n하나의 표준시를 정했다. 현재 중국은 지역의 위치와 상관없이 시간이 동일하다. 그러나 \n중국 내에서 베이징은 동쪽에 위치해 있어, 베이징과 멀리 떨어진 서쪽 지역은 표준시와 \n실제 시간이 3시간 정도 차이가 난다. 같은 오전 7시 30분일지라도 베이징에서는 아침 \n해가 떠 있지만, 서쪽 지역은 여전히 어두운 새벽이다. 이러한 시간 차이를 고려해 중국은 \n지역별로 학생들의 등교 시간을 다르게 운영하고 있다.\n중국에서는 학생들이 등교하는 시간이\n\t\n지역마다 다르다고요?\n \n우\n리\n가\n \n들\n려\n주\n는\n \n사\n회\n \n이\n야\n기\n우\n사이\n들\n리\n한 나라 안에서 지역에 따라 시간이 다르면 어떤 장단점이 있을지 이야기해 봅시다.\n 표준시 조정 후 지역별 등교 시간\n우루무치\n베이징\n우린 등교 시간이\n9시 15분이야.\n우린 등교 시간이\n7시 30분이야.\n하얼빈은 등교 \n시간이 7시야.\n충칭은 등교 시간이\n8시야.\n130\n3 지구, 대륙 그리고 국가들",
    "extracted_text_truncated": false
  },
  "neighbor_sections": [
    {
      "relation": "previous",
      "section_key": "___10차시__세계의_대륙__대양__나라___아시아_주요_나라들의_위치_알아보기",
      "sheet_name": "10차시",
      "lesson_title": "세계의 대륙, 대양, 나라 — 아시아 주요 나라들의 위치 알아보기",
      "title_query": "세계의 대륙, 대양, 나라 — 아시아 주요 나라들의 위치 알아보기",
      "pdf_pages": [
        131
      ]
    },
    {
      "relation": "next",
      "section_key": "___12차시__세계의_대륙__대양__나라___북아메리카와_남아메리카_주요_나라들의_위치_알아보기",
      "sheet_name": "12차시",
      "lesson_title": "세계의 대륙, 대양, 나라 — 북아메리카와 남아메리카 주요 나라들의 위치 알아보기",
      "title_query": "세계의 대륙, 대양, 나라 — 북아메리카와 남아메리카 주요 나라들의 위치 알아보기",
      "pdf_pages": [
        131
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
