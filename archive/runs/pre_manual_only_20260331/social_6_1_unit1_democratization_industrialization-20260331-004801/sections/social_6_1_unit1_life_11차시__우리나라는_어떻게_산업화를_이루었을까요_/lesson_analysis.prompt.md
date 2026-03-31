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
  "card_file": "social_6_1_unit1_life_11차시",
  "title": "우리나라는 어떻게 산업화를 이루었을까요?",
  "badge": "11차시",
  "pdf_pages": [
    41
  ],
  "textbook_source": {
    "resource_id": "main",
    "title_query": "우리나라는 어떻게 산업화를 이루었을까요?",
    "start_page": 41,
    "end_page": 41,
    "confidence": 0.45,
    "status": "matched"
  }
}

Baseline lesson analysis:
{
  "lesson_id": "11차시",
  "sheet_name": "11차시",
  "lesson_title": "우리나라는 어떻게 산업화를 이루었을까요?",
  "lesson_type": "core",
  "pdf_pages": [
    41
  ],
  "essential_question": "우리나라는 어떻게 산업화를 이루었을까요?",
  "learning_goals": [
    "우리나라는 어떻게 산업화를 이루었을까요의 핵심 내용을 설명할 수 있다."
  ],
  "key_concepts": [
    "우리나라",
    "어떻게",
    "산업화",
    "이루었을까요",
    "년대"
  ],
  "vocabulary": [
    "우리나라",
    "어떻게",
    "산업화"
  ],
  "misconceptions": [],
  "difficulty_band": "on-level",
  "content_chunks": [
    {
      "chunk_id": "11차시-chunk-1",
      "label": "학습 덩어리 1",
      "knowledge_type": "procedure",
      "summary": "2000년대 이후 우리나라는 1996년 경제협력개발기구 (OECD)에 가입하는 등 1990년대에도 경제가 꾸준히 성장했다.",
      "source_pages": [
        41
      ]
    }
  ],
  "source_page_refs": [
    41
  ],
  "analysis_confidence": 0.75,
  "notes": "자동 생성 초안. lesson title, key concepts, chunks를 검토 후 승인 필요."
}

Schedule draft:
{
  "schema_version": "1.0.0",
  "generated_at": "2026-03-30T15:48:07.189328+00:00",
  "sections": [
    {
      "sheet_name": "10차시",
      "lesson_title": "민주화 이후 우리 사회는 어떻게 달라졌을까요?",
      "title_query": "민주화 이후 우리 사회는 어떻게 달라졌을까요?"
    },
    {
      "sheet_name": "11차시",
      "lesson_title": "우리나라는 어떻게 산업화를 이루었을까요?",
      "title_query": "우리나라는 어떻게 산업화를 이루었을까요?"
    },
    {
      "sheet_name": "12-13차시",
      "lesson_title": "산업화로 사람들의 생활은 어떻게 달라졌을까요? / 주제 마무리",
      "title_query": "산업화로 사람들의 생활은 어떻게 달라졌을까요?"
    }
  ]
}

Section context:
{
  "schema_version": "1.0.0",
  "generated_at": "2026-03-30T15:48:23.488439+00:00",
  "pdf_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/textbook/사회/[사회]6_1_교과서.pdf",
  "current_section": {
    "section_key": "social_6_1_unit1_life_11차시__우리나라는_어떻게_산업화를_이루었을까요_",
    "sheet_name": "11차시",
    "lesson_title": "우리나라는 어떻게 산업화를 이루었을까요?",
    "title_query": "우리나라는 어떻게 산업화를 이루었을까요?",
    "pdf_pages": [
      41
    ],
    "baseline_analysis_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/artifacts/runs/social_6_1_unit1_democratization_industrialization-20260331-004801/source/local_baseline/social_6_1_unit1_life_11차시__우리나라는_어떻게_산업화를_이루었을까요_.lesson_analysis.json",
    "extracted_text": "2000년대\n이후\n우리나라는 1996년 경제협력개발기구\n(OECD)에 가입하는 등 1990년대에도 경제가 \n꾸준히 성장했다. 그러나 일부 대기업들이 무리\n하게 사업을 확장하고, 국가도 경제를 제대로 \n관리하지 못해 수출이 어려워졌다. 결국 외환 \n(달러)이 부족해져 위기가 발생했다. 이에 정부는 \n국제통화기금(IMF)의 도움을 받았고, 정부, 기업, \n시민들이 함께 외환 위기를 극복하려고 노력했다. \nIMF 구제 금융 공식 요청\n1997년 11월 22일\n제○○호\n억\n \n달\n러\n \n수\n준\n \n될\n \n것\n“\n“\n200\n이\n르\n면\n \n내\n달\n \n중\n \n지\n원\n \n시\n작\n캉\n드\n쉬\n \n총\n재\n \n적\n극\n \n지\n원\n \n밝\n혀\n林부총리, 어젯밤 긴급 회견\n                        김영삼 대통령이 21일 저녁 각 당 정치 지도자들을 청와대로\n                        초청, 금융 위기 타개 방안을 논의하고 있다.\n경제 회담\n ‌\u00071997년 국제통화기금 구제 금융 공식 \n요청\n2000년대 이후에는 과학 기술의 발달로 우주 항공, 생명 공학, 인공지능(AI) \n산업 등 첨단 산업이 성장하면서, 사람을 대신해 기계나 인공지능 로봇을 이용 \n하는 사례가 늘어났다. 또 소득 수준이 높아지면서 의료 서비스업, 관광 산업, 문화 \n콘텐츠 산업 등 삶의 질을 높여 주는 서비스 \n관련 산업도 발달했다.\n1970년대에 정부는 중화학 공업을 일으키는 데 힘썼다. 이 시기에는 \n제철소, 조선소, 정유 공장 등을 세우고 철강, 선박 등을 수출하며 경제가 \n크게 성장했다. \n1980년대에는 전자, 자동차 산업을 중심으로 경제가 \n더욱 발전했다. 주로 텔레비전과 자동차를 수출했으며, \n세계에서 그 기술력을 인정받았다.\n1990년대부터 자동차와 전자 제품의 \n생산이 더욱 증가했다. 특히 개인용 \n컴퓨터 생산이 늘면서 우리 기술로 \n개발한 반도체가 중요한 수출 상품이 \n되었다. \n1970년대\n중화학 공업  자동차, 배, 철강 \n등 무거운 제품과 석유 화학, \n시멘트, 합성 고무 제품 등을 \n생산하는 산업\n1990년대\n1980년대\n정부는 수출을 늘리기 위해\n수출 기업들에 \n많은 지원을 했어.\n1980년대 들어\n경공업 제품보다 중화학\n공업 제품의 수출 비중이\n더 커졌어.\n각 시기별 산업화 과정\n의 특징을 이야기해 \n봅시다. \n스스로\n해 보기\n우리나라 경제는 정부, 기업, \nㄴ\nㄷ\nㅈ\n의 노력으로 성장했다. \n한 문장 정리\n정부, 기업, 노동자가\n함께 노력해 산업화를\n이루어 냈어.\n 100억 달러 수출의 날 기념우표(위)와\n기념 조형물(아래)\n 1980년대에 수출한 자동차\n 1990년대 반도체 생산\n 1970년대에 세운 포항 제철소\n 2020년대 공장에서 일하는 인공지능 로봇\n 한국 관광을 즐기는 관광객\n외환 위기\n우리봇이 알려 주는 역사\n배움 확인\n39\n1 평화 통일을 위한 노력, 민주화와 산업화\n40\n2   민주화와 산업화로 달라진 생활 문화",
    "extracted_text_truncated": false
  },
  "neighbor_sections": [
    {
      "relation": "previous",
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
      ]
    },
    {
      "relation": "next",
      "section_key": "social_6_1_unit1_life_12-13차시__산업화로_사람들의_생활은_어떻게_달라졌을까요____주제_마무리",
      "sheet_name": "12-13차시",
      "lesson_title": "산업화로 사람들의 생활은 어떻게 달라졌을까요? / 주제 마무리",
      "title_query": "산업화로 사람들의 생활은 어떻게 달라졌을까요?",
      "pdf_pages": [
        20
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
