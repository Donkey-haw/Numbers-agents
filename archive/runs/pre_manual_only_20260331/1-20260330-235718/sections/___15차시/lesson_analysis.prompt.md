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
  "sheet_name": "15차시",
  "card_file": "___15차시",
  "title": "3단원 정리 — [단원 마무리] 나만의 누리집 완성하기 / 창의·융 합 사고력 쑥쑥",
  "badge": "15차시",
  "accent": [
    "#1d4ed8",
    "#3b82f6"
  ],
  "sources": [
    {
      "resource_id": "main",
      "role": "textbook",
      "title_query": "3단원 정리 — [단원 마무리] 나만의 누리집 완성하기 / 창의·융 합 사고력 쑥쑥",
      "_inference": {
        "status": "matched",
        "start_page": 49,
        "end_page": 49,
        "start_query": "3단원 정리 — [단원 마무리] 나만의 누리집 완성하기 / 창의·융 합 사고력 쑥쑥",
        "start_match_pages": [
          49,
          50,
          105,
          152,
          178
        ],
        "start_match_count": 5,
        "end_strategy": "boundary_decision_agent",
        "end_reference_query": null,
        "intro_boundary_page": null,
        "reason": "Transitional heuristic: choose highest-ranked candidate and cut before next lesson candidate",
        "confidence": 0.45
      },
      "pdf_pages": [
        49
      ]
    }
  ],
  "source_ranges": [
    {
      "resource_id": "main",
      "role": "textbook",
      "pdf_pages": [
        49
      ]
    }
  ],
  "pdf_pages": [
    49
  ]
}

Baseline lesson analysis:
{
  "schema_version": "1.0.0",
  "generated_at": "2026-03-30T14:58:00.392697+00:00",
  "lesson_id": "15차시",
  "sheet_name": "15차시",
  "lesson_title": "3단원 정리 — [단원 마무리] 나만의 누리집 완성하기 / 창의·융 합 사고력 쑥쑥",
  "lesson_type": "core",
  "pdf_pages": [
    49
  ],
  "essential_question": "3단원 정리 — [단원 마무리] 나만의 누리집 완성하기 / 창의·융 합 사고력 쑥쑥",
  "learning_goals": [
    "3단원 정리 — [단원 마무리] 나만의 누리집 완성하기의 핵심 내용을 설명할 수 있다."
  ],
  "key_concepts": [
    "마무리",
    "나만",
    "누리집",
    "완성하기",
    "창의"
  ],
  "vocabulary": [
    "마무리",
    "나만",
    "누리집"
  ],
  "misconceptions": [
    "선거를 단순히 사람을 뽑는 행사로만 이해할 수 있다."
  ],
  "difficulty_band": "on-level",
  "content_chunks": [
    {
      "chunk_id": "15차시-chunk-1",
      "label": "학습 덩어리 1",
      "content_type": "mixed",
      "knowledge_type": "procedure",
      "summary": "산업화 카드 뉴스로 보는 인기 영상 이 단원의 독재 정권에 맞서 민주화 운동이 일어나다.",
      "source_pages": [
        49
      ],
      "suggested_activity_types": [
        "see_think_wonder",
        "learning_note",
        "worksheet"
      ]
    }
  ],
  "source_page_refs": [
    49
  ],
  "analysis_confidence": 0.75,
  "review_status": "draft",
  "notes": "자동 생성 초안. lesson title, key concepts, chunks를 검토 후 승인 필요."
}

Schedule draft:
{
  "schema_version": "1.0.0",
  "generated_at": "2026-03-30T14:57:25.043936+00:00",
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
    },
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
    },
    {
      "sheet_name": "8-9차시",
      "lesson_title": "민주화와 산업화로 달라진 생활 문화 — 4·19 혁명 이해하기",
      "title_query": "민주화와 산업화로 달라진 생활 문화 — 4·19 혁명 이해하기"
    },
    {
      "sheet_name": "10차시",
      "lesson_title": "민주화와 산업화로 달라진 생활 문화 — 대통령 직선제와 지방 자치제의 부활 이해하기",
      "title_query": "민주화와 산업화로 달라진 생활 문화 — 대통령 직선제와 지방 자치제의 부활 이해하기"
    },
    {
      "sheet_name": "11차시",
      "lesson_title": "민주화와 산업화로 달라진 생활 문화 — 산업화 과정 이해하기",
      "title_query": "민주화와 산업화로 달라진 생활 문화 — 산업화 과정 이해하기"
    },
    {
      "sheet_name": "12-13차시",
      "lesson_title": "민주화와 산업화로 달라진 생활 문화 — 산업화로 달라진 사회와 생활 문화 이해하기",
      "title_query": "민주화와 산업화로 달라진 생활 문화 — 산업화로 달라진 사회와 생활 문화 이해하기"
    },
    {
      "sheet_name": "14차시",
      "lesson_title": "1단원 정리 — [단원 마무리] 나만의 누리집 완성하기 / 창의·융 합 사고력 쑥쑥",
      "title_query": "1단원 정리 — [단원 마무리] 나만의 누리집 완성하기 / 창의·융 합 사고력 쑥쑥"
    },
    {
      "sheet_name": "1차시",
      "lesson_title": "2단원 도입 — [단원 도입] 우리 친구는 누구?",
      "title_query": "2단원 도입 — [단원 도입] 우리 친구는 누구?"
    },
    {
      "sheet_name": "2차시",
      "lesson_title": "민주주의와 선거 — 선거의 의미와 중요성 파악하기",
      "title_query": "민주주의와 선거 — 선거의 의미와 중요성 파악하기"
    },
    {
      "sheet_name": "3차시",
      "lesson_title": "민주주의와 선거 — 민주주의에서 선거의 역할 파악하기",
      "title_query": "민주주의와 선거 — 민주주의에서 선거의 역할 파악하기"
    },
    {
      "sheet_name": "4-5차시",
      "lesson_title": "민주주의와 선거 — 우리나라의 선거 과정 살펴보기",
      "title_query": "민주주의와 선거 — 우리나라의 선거 과정 살펴보기"
    },
    {
      "sheet_name": "6-7차시",
      "lesson_title": "민주주의와 선거 — 선거에 적극적으로 참여해야 하는 까닭 알아보기",
      "title_query": "민주주의와 선거 — 선거에 적극적으로 참여해야 하는 까닭 알아보기"
    },
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
    },
    {
      "sheet_name": "14차시",
      "lesson_title": "민주주의와 미디어 — [주제 도입] 열려라 이야기 / 외쳐라 빙고",
      "title_query": "민주주의와 미디어 — [주제 도입] 열려라 이야기 / 외쳐라 빙고"
    },
    {
      "sheet_name": "15차시",
      "lesson_title": "민주주의와 미디어 — 미디어의 정보 제공 역할 알아보기",
      "title_query": "민주주의와 미디어 — 미디어의 정보 제공 역할 알아보기"
    },
    {
      "sheet_name": "16차시",
      "lesson_title": "민주주의와 미디어 — 미디어의 내용을 비판적으로 분석해야 하는 까 닭 알아보기",
      "title_query": "민주주의와 미디어 — 미디어의 내용을 비판적으로 분석해야 하는 까 닭 알아보기"
    },
    {
      "sheet_name": "17-18차시",
      "lesson_title": "민주주의와 미디어 — 미디어를 올바르게 이용하는 방법 알아보기",
      "title_query": "민주주의와 미디어 — 미디어를 올바르게 이용하는 방법 알아보기"
    },
    {
      "sheet_name": "19차시",
      "lesson_title": "2단원 정리 — [단원 마무리] 나만의 누리집 완성하기 / 창의·융 합 사고력 쑥쑥",
      "title_query": "2단원 정리 — [단원 마무리] 나만의 누리집 완성하기 / 창의·융 합 사고력 쑥쑥"
    },
    {
      "sheet_name": "1차시",
      "lesson_title": "3단원 도입 — [단원 도입] 우리 친구는 누구?",
      "title_query": "3단원 도입 — [단원 도입] 우리 친구는 누구?"
    },
    {
      "sheet_name": "2-3차시",
      "lesson_title": "지구본과 지도로 보는 세계 — 지구본의 특징 살펴보기",
      "title_query": "지구본과 지도로 보는 세계 — 지구본의 특징 살펴보기"
    },
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
    },
    {
      "sheet_name": "7차시",
      "lesson_title": "지구본과 지도로 보는 세계 — 위도와 경도를 이용해 위치를 표현하는 방법 살 펴보기",
      "title_query": "지구본과 지도로 보는 세계 — 위도와 경도를 이용해 위치를 표현하는 방법 살 펴보기"
    },
    {
      "sheet_name": "8차시",
      "lesson_title": "세계의 대륙, 대양, 나라 — [주제 도입] 열려라 이야기 / 외쳐라 빙고",
      "title_query": "세계의 대륙, 대양, 나라 — [주제 도입] 열려라 이야기 / 외쳐라 빙고"
    },
    {
      "sheet_name": "9차시",
      "lesson_title": "세계의 대륙, 대양, 나라 — 우리나라의 위치 특징 파악하기",
      "title_query": "세계의 대륙, 대양, 나라 — 우리나라의 위치 특징 파악하기"
    },
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
    },
    {
      "sheet_name": "13차시",
      "lesson_title": "세계의 대륙, 대양, 나라 — 아프리카 주요 나라들의 위치 알아보기",
      "title_query": "세계의 대륙, 대양, 나라 — 아프리카 주요 나라들의 위치 알아보기"
    },
    {
      "sheet_name": "14차시",
      "lesson_title": "세계의 대륙, 대양, 나라 — 오세아니아 주요 나라들의 위치 알아보기",
      "title_query": "세계의 대륙, 대양, 나라 — 오세아니아 주요 나라들의 위치 알아보기"
    },
    {
      "sheet_name": "15차시",
      "lesson_title": "3단원 정리 — [단원 마무리] 나만의 누리집 완성하기 / 창의·융 합 사고력 쑥쑥",
      "title_query": "3단원 정리 — [단원 마무리] 나만의 누리집 완성하기 / 창의·융 합 사고력 쑥쑥"
    }
  ]
}

Section context:
{
  "schema_version": "1.0.0",
  "generated_at": "2026-03-30T15:25:34.734131+00:00",
  "pdf_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/textbook/사회/[사회]6_1_교과서.pdf",
  "current_section": {
    "sheet_name": "15차시",
    "lesson_title": "민주주의와 미디어 — 미디어의 정보 제공 역할 알아보기",
    "title_query": "민주주의와 미디어 — 미디어의 정보 제공 역할 알아보기",
    "pdf_pages": [
      83,
      84,
      85,
      86,
      87,
      88,
      89
    ],
    "baseline_analysis_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/artifacts/runs/1-20260330-235718/source/local_baseline/___15차시.lesson_analysis.json",
    "extracted_text": "증인\n비판적 사고력\n 위 재판 모습을 보고, 물음에 답해 봅시다.\n재판을 통해 법원의 역할 알아보기\n스스로\n해 보기\n문제 해결력 및\n의사 결정력\n법을 어긴 사람을 \n처벌하는 재판\n5  ‌\u0007피고인이 나물의 원산지를 속여 \n부당한 이득을 얻었지만, 초범 \n이고 죄를 뉘우치고 있는 점을 \n고려해 징역 1년을 선고합니다.\n4  ‌\u0007판사님, 피고인은 비록 원산지\n를 속인 잘못을 저질렀으나, 깊이 \n반성하고 있습니다. 이 점을 \n헤아려 주시기 바랍니다.\n2  ‌\u0007피고인이 외국산 나물을 국산 \n나물 자루에 몰래 옮겨 담는 \n것을 목격했습니다.\n3  ‌\u0007많이 반성하고 있습니다. \n정말 죄송합니다.\n2\t ‌\u0007판사의 판결을 통해 문제가 어떻게 해결되었는지 이야기해 봅시다.\n1\t \u0007가~ 라에 들어갈 역할을 아래 표에서 골라 써 봅시다.\n판사\n재판을 진행하고 판결을 내리는 \n사람\n변호인\n피고인을 대신해 권리를 주장하는 \n사람\n검사\n범죄 사건을 수사하고, 피고인의 \n처벌을 요구하는 사람\n피고인\n범죄를 저지른 것으로 의심되어 \n재판을 받는 사람\n초범  처음으로 죄를 \n저지름.\n선고  판사가 판결을 \n알리는 일\n1  ‌\u0007피고인은 나물의 원산지를 \n속여 학교에 납품해 부당한 \n이득을 얻었습니다. 이에 대해 \n징역 2년을 구형합니다. \n가\n나\n다\n라\n83\n2   국가기관이 하는 일\n\n공정한 재판을 위한 노력\n우리나라는 공정한 재판을 통해 국민의 자유와 권리를 보장하고자 한다. \n이를 위해 법원은 특별한 경우를 제외하고 재판 과정과 결과를 일반인들\n에게 공개하고 있다. 또한 잘못된 재판으로 피해를 보는 사례를 줄이고자 \n서로 다른 법원에서 세 번까지 재판을 받을 수 있는 3심 제도를 운영하고 \n있다.\n법원은 법에 따라 \nㅈ\nㅍ\n 을/를 하는 기관이다.\n한 문장 정리\n1심\n2심\n3심\n원고  개인 간의 다툼을 해결\n하는 재판에서 재판을 요청\n한 사람\n피고  개인 간의 다툼을 해결\n하는 재판에서 원고에게 피해\n를 주었다고 지목된 사람\n만화를 보고 3심 제도를 통해 \n시민의 자유와 권리가 어떻게 \n보장됐는지 이야기해 봅시다.\n스스로\n해 보기\n공사장의 소음이 기준치를 \n넘지 않았습니다. 따라서 \n법적으로 문제가 없습니다.\n소음 기준을 넘지 않았다고 해서 \n피해를 보지 않은 것은 아니에요. \n다시 재판을 요청해야겠어요.\n공사장에서 소음이\n발생했음에도 불구하고\n피고 측이 소음을 줄이려고 노력\n하지 않아 원고가 피해를 입은 \n점을 인정합니다.\n이 판결은 받아들이기 \n어렵습니다.\n공사장의 소음으로 \n원고가 피해를 입었다는 \n주장은 근거가 부족합니다.\n자료를 보충해서 다시\n재판을 받아 봅시다.\n원고 측\n변호사\n배움 확인\n84\n2 민주주의와 시민 참여\n\n국민 참여 재판은 일반 국민이 배심원으로서 재판에 참여하는 제도로, 재판의 공정성\n과 투명성을 높이고자 도입되었다. 배심원이 된 국민은 재판 과정에 참여해 판결에 관한 \n의견을 제시하고, 재판부는 이를 참고해 판결을 내린다.\n국민의 참여로 완성되는\n\t\n국민 참여 재판\n우\n사이\n리\n들\n \n우\n리\n가\n \n들\n려\n주\n는\n \n사\n회\n \n이\n야\n기\n국민 참여 재판을 받으면 어떤 점이 좋을지 이야기해 봅시다.\n재판부  판결을 내리기 위해 판사 한 사람 혹은 두 사람 \n이상으로 구성되는 재판 부서\n법정에 제출된 증거를 바탕으로 \n피고인의 유·무죄를 판단해요. 재판 \n과정을 지켜보며 궁금한 점이 있다면 \n판사를 통해 질문할 수도 있어요.\n 사건 설명을 듣고 있는 배심원들\n배심원은 무슨 \n일을 하나요?\n20세 이상 국민은 누구나 배심원이 \n될 수 있지만, 변호사, 경찰 등 특정한 \n직업을 가진 사람들은 배심원이 될 \n수 없어요. 재판부는 배심원의 의견을 \n존중하지만, 배심원의 의견과 다른 판결\n을 내릴 수도 있어요.\n ‌\u0007국민 참여 재판에 참여하기 전 선서를 하는 \n배심원들\n배심원에는 누가 선정되나요? \n그리고 판사는 배심원의 의견을 \n반드시 따라야 하나요?\n국민참여재판 누리집\n85\n2   국가기관이 하는 일\n\n비판적 사고력\n문제 해결력 및\n의사 결정력\n국가 권력이 어느 한 국가기관에 집중되면 국가의 중요한 일을 마음대로 \n처리할 수 있다. 또한 국가기관이 국민의 의견과 다르게 권력을 행사한다면 \n국민의 자유와 권리가 침해될 수 있다. \n국가의 권력을 왜 나누어야 할까요?\n다섯\n정부 세종 청사에서 일하시는 분이 이야기를 들려주셨어. 과거 우리나라의 \n어떤 대통령은 국회를 해산하고 자기 마음대로 법을 바꾼 적이 있다고 해. 심지어 식당에서 \n나라에 대한 불만을 이야기한 사람들을 처벌하기도 했다고 말씀하셨어. 이런 일이 다시는 \n일어나지 않도록 하려면 어떻게 해야 할까?\n생각 깨우기\n해산  집단, 조직, 단체 등을 \n흩어지게 함.\n국가 권력이 한곳에 집중되면 어떤 일이 벌어질지 탐구하기\n스스로\n해 보기\n1\t \u0007위 그림에 나타난 문제점을 이야기해 봅시다.\n2\t \u0007위 그림을 참고해 권력이 한 사람이나 어떤 기관에 집중되면 어떤 문제가 생길지 써  \n봅시다.\n시위가 많이 일어나는 대학교를 \n폐쇄하도록 하겠습니다.\n국회를 해산하고\n헌법을 바꾸겠습니다.\n앞으로 국회의원과 판사를 \n대통령이 직접 임명하겠습니다.\n애니메이션\n대통령\n86\n2 민주주의와 시민 참여\n\n민주 국가에서 국가 권력을 서로 독립된 기관이 나누어 맡도록 하는 것을 \n권력 분립이라고 한다. 우리나라는 국회, 행정부, 법원이 권력을 나누어 행사 \n하는데, 이를  삼권 분립이라고 한다. 삼권 분립을 통해 국가의 권력이 한 기관\n에 집중되지 않도록 하고, 각 기관이 서로 균형을 이루게 함으로써 국민의 \n자유와 권리를 보장한다.\n삼권 분립\n국회\n국민의 뜻에 따라 법을 만들고 \n고치는 일을 한다.\n행정부\n법에 따라 나라 살림을\n맡아 한다.\n법원\n법에 따라 재판을 한다.\n서\n로 \n견제\n하며\n 균\n형을\n 이\n루고\n 있\n는 국\n가기\n관\n국회는 예산안 심의, 국정 \n감사 등을 통해 행정부를 \n견제한다.\n대통령은 국회에서 통과한 \n법률안에 대해 거부권을 \n행사한다.\n국회는 대통령이 대법원장\n을 임명할 때 동의권을 행사\n한다.\n법원은 행정부가 만든 \n명령과 규칙을 심사한다.\n대통령은 대법원장을 \n임명한다.\n법원은 국회가 만든 법률\n이 헌법에 어긋나는지 헌법\n재판소에 심사를 요청한다.\n87\n2   국가기관이 하는 일\n\n비판적 사고력\n정보 활용 능력\n  ‌\u0007가 ~ 다 기사를 보고 각 국가기관이 서로를 어떻게 견제하고 있는지 빈칸에 알맞은 기관을 \n써 봅시다.\n국가기관의 견제 사례 알아보기\n스스로\n해 보기\n민주 국가는 \nㄱ\nㄹ\n  분립을 통해 국민의 자유와 권리를 보장한다.\n한 문장 정리\n국회, 20△△년도 국정 감사 실시\n국회는 10월 10일부터 27일까지 18일간 20△△\n년도 국정 감사를 실시한다고 밝혔다. \n대통령, 법률안 거부권 행사\n대통령은 지난달 국회 본회의에서 통과한  \n관련 법률안에 대해 거부권을 행사했다. \n법원, □□ 관련 법 심사 요청\n법원은 지난달 국회에서 만들었던  \n관련 법이 헌법에 어긋나는지 확인하기 위해 \n헌법재판소에 심사를 요청했다.\n가\n나\n 헌법재판소\n다\n가는 국회가 \n을/를 견제하는 모습이다.\n나는 행정부가 \n을/를 견제하는 모습이다.\n다는 법원이 \n을/를 견제하는 모습이다.\n국가기관의 \n견제 사례에는 \n또 어떤 것들이 있을까?\n배움 확인\n88\n2 민주주의와 시민 참여\n\n아래 게시판의 문제를 풀어 누리가 체험 학습을 갈 장소를 찾아봅시다.\n이번 주제에서 배운 내용을 정리하며 우리가 행복이를 만날 수 있는 길을 찾아봅시다.\n주제마무리\n되돌아가기를 만나면 교과서를 살펴본 후 처음부터 시작합니다.\n72~73쪽\n74~85쪽\n86~88쪽\n1.\t\u0007민주 국가의 국가기관을 설명할 수 있나요?\n\t\n예 \n \n\t\n아니요 \n \n2.\t\u0007민주 국가에서 국회, 행정부, 법원이 하는 일을 설명\n할 수 있나요?\n\t\n예 \n \n\t\n아니요 \n \n3.\t\u0007국가기관이 권력을 나누어 갖는 까닭을 설명할 수 \n있나요?\n\t\n예 \n \n\t\n아니요 \n \n1  ‌\u0007민주 국가에서 법에 따라 나랏일을 하는 \n기관을 (\n)(이)라고 한다.\n2  ‌\u0007국회는 (\n)을/를 만들거나 고치는 일을 \n한다.\n3  ‌\u0007행정부의 최고 책임자는 (\n)(이)다.\n4  ‌\u0007법원은 법에 따라 (\n)을/를 하는 국가 \n기관이다.\n5  ‌\u0007국가기관은 서로 (\n)하여 국가 권력이 \n한 기관에 집중되지 않도록 한다.\n목적지가\n어디일까?\n정답:\n정답\n국가\n기관\n선거\n운동\n국\n정\n건물\n법\n준\n회\n대통령\n국무\n총리\n의\n성\n재판\n국정\n감사\n사\n주\n방관\n견제\n박\n당\n요약 정리\n89\n2   국가기관이 하는 일"
  },
  "neighbor_sections": [
    {
      "relation": "previous",
      "sheet_name": "14차시",
      "lesson_title": "민주주의와 미디어 — [주제 도입] 열려라 이야기 / 외쳐라 빙고",
      "title_query": "민주주의와 미디어 — [주제 도입] 열려라 이야기 / 외쳐라 빙고",
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
        73,
        74,
        75,
        76,
        77,
        78,
        79,
        80,
        81,
        82
      ]
    },
    {
      "relation": "next",
      "sheet_name": "16차시",
      "lesson_title": "민주주의와 미디어 — 미디어의 내용을 비판적으로 분석해야 하는 까 닭 알아보기",
      "title_query": "민주주의와 미디어 — 미디어의 내용을 비판적으로 분석해야 하는 까 닭 알아보기",
      "pdf_pages": [
        90
      ]
    }
  ]
}

Target schema:
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://numbersauto.local/schemas/lesson_analysis.schema.json",
  "title": "Lesson Analysis",
  "type": "object",
  "required": [
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
  "properties": {
    "schema_version": {
      "type": "string"
    },
    "generated_at": {
      "type": "string",
      "format": "date-time"
    },
    "lesson_id": {
      "type": "string"
    },
    "sheet_name": {
      "type": "string"
    },
    "lesson_title": {
      "type": "string"
    },
    "lesson_type": {
      "type": "string",
      "enum": ["intro", "core", "review", "summary", "mixed"]
    },
    "pdf_pages": {
      "type": "array",
      "items": {
        "type": "integer",
        "minimum": 1
      },
      "minItems": 1
    },
    "essential_question": {
      "type": "string"
    },
    "learning_goals": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "minItems": 1
    },
    "key_concepts": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "minItems": 1
    },
    "vocabulary": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "misconceptions": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "difficulty_band": {
      "type": "string",
      "enum": ["core", "on-level", "extension", "mixed"]
    },
    "content_chunks": {
      "type": "array",
      "items": {
        "type": "object",
        "required": [
          "chunk_id",
          "label",
          "content_type",
          "knowledge_type",
          "summary",
          "source_pages"
        ],
        "properties": {
          "chunk_id": {
            "type": "string"
          },
          "label": {
            "type": "string"
          },
          "content_type": {
            "type": "string",
            "enum": ["text", "image", "diagram", "map", "activity", "summary", "mixed"]
          },
          "knowledge_type": {
            "type": "string",
            "enum": ["fact", "concept", "procedure", "comparison", "cause-effect", "opinion", "application", "mixed"]
          },
          "summary": {
            "type": "string"
          },
          "source_pages": {
            "type": "array",
            "items": {
              "type": "integer",
              "minimum": 1
            },
            "minItems": 1
          },
          "suggested_activity_types": {
            "type": "array",
            "items": {
              "type": "string"
            }
          }
        },
        "additionalProperties": false
      }
    },
    "source_page_refs": {
      "type": "array",
      "items": {
        "type": "integer",
        "minimum": 1
      },
      "minItems": 1
    },
    "analysis_confidence": {
      "type": "number",
      "minimum": 0,
      "maximum": 1
    },
    "review_status": {
      "type": "string",
      "enum": ["draft", "reviewed", "approved", "rejected"]
    },
    "notes": {
      "type": "string"
    }
  },
  "additionalProperties": false
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
