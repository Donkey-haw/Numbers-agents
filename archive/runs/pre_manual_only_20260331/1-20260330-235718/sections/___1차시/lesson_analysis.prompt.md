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
  "sheet_name": "1차시",
  "card_file": "___1차시",
  "title": "3단원 도입 — [단원 도입] 우리 친구는 누구?",
  "badge": "1차시",
  "accent": [
    "#0f766e",
    "#14b8a6"
  ],
  "sources": [
    {
      "resource_id": "main",
      "role": "textbook",
      "title_query": "3단원 도입 — [단원 도입] 우리 친구는 누구?",
      "_inference": {
        "status": "matched",
        "start_page": 4,
        "end_page": 111,
        "start_query": "3단원 도입 — [단원 도입] 우리 친구는 누구?",
        "start_match_pages": [
          4,
          6,
          62,
          66,
          72
        ],
        "start_match_count": 5,
        "end_strategy": "boundary_decision_agent",
        "end_reference_query": null,
        "intro_boundary_page": null,
        "reason": "Transitional heuristic: choose highest-ranked candidate and cut before next lesson candidate",
        "confidence": 0.55
      },
      "pdf_pages": [
        4,
        5,
        6,
        7,
        8,
        9,
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
        109,
        110,
        111
      ]
    }
  ],
  "source_ranges": [
    {
      "resource_id": "main",
      "role": "textbook",
      "pdf_pages": [
        4,
        5,
        6,
        7,
        8,
        9,
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
        109,
        110,
        111
      ]
    }
  ],
  "pdf_pages": [
    4,
    5,
    6,
    7,
    8,
    9,
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
    109,
    110,
    111
  ]
}

Baseline lesson analysis:
{
  "schema_version": "1.0.0",
  "generated_at": "2026-03-30T14:57:45.144874+00:00",
  "lesson_id": "1차시",
  "sheet_name": "1차시",
  "lesson_title": "3단원 도입 — [단원 도입] 우리 친구는 누구?",
  "lesson_type": "core",
  "pdf_pages": [
    4,
    5,
    6,
    7,
    8,
    9,
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
    109,
    110,
    111
  ],
  "essential_question": "3단원 도입 — [단원 도입] 우리 친구는 누구?",
  "learning_goals": [
    "3단원 도입 — [단원 도입] 우리 친구는 누구의 핵심 내용을 설명할 수 있다."
  ],
  "key_concepts": [
    "도입",
    "친구",
    "누구",
    "선거",
    "평화"
  ],
  "vocabulary": [
    "도입",
    "친구",
    "누구"
  ],
  "misconceptions": [
    "선거를 단순히 사람을 뽑는 행사로만 이해할 수 있다.",
    "민주주의의 핵심이 참여보다 결과에만 있다고 오해할 수 있다."
  ],
  "difficulty_band": "on-level",
  "content_chunks": [
    {
      "chunk_id": "1차시-chunk-1",
      "label": "학습 덩어리 1",
      "content_type": "mixed",
      "knowledge_type": "procedure",
      "summary": "안녕, 친구들!",
      "source_pages": [
        4,
        5,
        6,
        7,
        8,
        9,
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
        57
      ],
      "suggested_activity_types": [
        "see_think_wonder",
        "learning_note",
        "worksheet"
      ]
    },
    {
      "chunk_id": "1차시-chunk-2",
      "label": "학습 덩어리 2",
      "content_type": "mixed",
      "knowledge_type": "procedure",
      "summary": "선거의 가장 기본적인 역할은 공동체의 대표자를 선출하는 것이다.",
      "source_pages": [
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
        109,
        110,
        111
      ],
      "suggested_activity_types": [
        "learning_note",
        "worksheet"
      ]
    }
  ],
  "source_page_refs": [
    4,
    5,
    6,
    7,
    8,
    9,
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
    109,
    110,
    111
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
  "generated_at": "2026-03-30T15:15:02.410174+00:00",
  "pdf_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/textbook/사회/[사회]6_1_교과서.pdf",
  "current_section": {
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
    ],
    "baseline_analysis_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/artifacts/runs/1-20260330-235718/source/local_baseline/___1차시.lesson_analysis.json",
    "extracted_text": "안녕, 친구들! 나는 ‘우리’야.\n너희들은 ‘사회’라는 단어를 들으면 어떤 모습이 떠오르니?\n ‘사회’는 우리가 살아가는 일상 속에서 일어나는 \n여러 사건과 현상을 이해하고, \n더 나은 세상을 만들어 가는 데 중요한 역할을 하는 과목이야.\n교과서를 펼칠 준비가 됐니? \n이제 나와 함께 배움 여행을 떠나 보자!\n이 책의구성과 \n  특징\n1\n평화 통일을 위한 노력\n1\n민주화와 산업화로 달라진 생활 문화\n2\n  \n   \n    \n    \n     \n    \n 분\n단  \n평화\n 통\n일 \n 민\n주화\n  \n산업\n화  \n평화 통일을 위한 \n노력, 민주화와 \n산업화\n애니메이션\n사람들의 이야기를 듣고, 나와 함께 이 단원을 공부할 \n내 친구 하나를 찾아 줘.\n평화 통일 캠페인 전시관에서 받은 한반도기를 \n들고 있어. \n전시회에서 다양한 자료를 받아 간다며 큰 배낭\n을 메고 왔던데?\n나와 가발 만들기 체험을 하고, 또 다른 체험을 \n경험해 보고 싶다고 했어. \n1\n평화 통일을 \n위한 노력\n 분단으로 생겨난 문제점과 평화 통일의 필요성을 설명할 수 있어요.\n 분단과 관련된 장소를 평화의 장소로 만들려는 노력을 찾아볼 수 있어요.\n 평화 통일을 위해 우리가 할 수 있는 일을 탐색할 수 있어요.\n이 주제를 배우면 나는\n이 산책로에 있는\n푯말은 무엇을 의미할까?\n1\n10\n1 평화 통일을 위한 노력, 민주화와 산업화\n1  낱말 구름을 보고, 이 주제에서 배울 내용이 무엇인지 생각해 봅시다.\n2  낱말 구름에 있는 낱말 9개를 골라서 빙고 놀이를 해 봅시다.\n평화 통일\n분단\n협력\n화해\n전쟁\n남한\n북한\n비무장 지대\n교류\n대립\n이산가족\n남북 정상 회담\n휴전선\n북한 이탈 주민\n문화 차이\n이 사람들이 들고 있는\n깃발은 무엇을\n상징할까?\n2\n11\n1  평화 통일을 위한 노력\n이 주제에서 배울 낱말들로 \n재미있는 빙고 놀이도 해 보자! \n준비됐니? \n대단원 도입\n이 단원의 내용을 그림으로 간단히 소개하고 \n있어. 대화창에 있는 힌트를 보며 우리와 함께 \n공부할 새로운 친구도 찾아보자!\n주제 도입\n주제와 관련한 사진을 보며 떠오르는 생각\n이나 경험을 자유롭게 나눠 볼까?\n나는 우리 친구\n행복이!\n\n본문\n주요 개념을 생활 속 다양한 장면이 담긴 사진과 \n그림으로 제시해 더 쉽게 이해할 수 있을 거야. \n스스로 / 함께해 보기\n혼자 또는 친구들과 함께하는 다양한 활동과 탐구\n를 통해 사회 과목의 역량을 키워 갈 수 있어. \n우리봇이 알려 주는 사회\n궁금하지만 잘 몰랐던 내용은 ‘우리봇’이 친절하게 \n설명해 줄 거야. \n비판적 사고력\n문제 해결력 및\n의사 결정력\n선거에 참여하는 바람직한 태도는 \n무엇일까요?\n넷\n민주 시민으로서 주권을 행사하려면 선거에 적극적으로 참여하는 것이 \n매우 중요하다. 선거에 관심이 부족하거나 참여하는 사람이 적으면 시민\n들의 의견을 충분히 반영할 수 있는 적합한 대표를 선출하기 어렵다. 또한 \n자신의 선택이 사회와 공동체에 끼치는 영향을 고려하고, 자신의 가치관과 \n신념을 바탕으로 책임감 있게 선거 과정에 참여하는 태도가 필요하다.\n2   ◯◯ 지역 주민들의 의견을 충분히 반영할 수 있는 대표를 선출하려면 어떻게 해야 할지 이\n야기해 봅시다.\n1   위 대화에서 밑줄 친 부분과 같은 걱정을 하는 까닭이 무엇일지 이야기해 봅시다. \n선거에 적극적으로 참여해야 하는 까닭 알아보기\n스스로\n해 보기\n이번  지역 선거는 \n투표율이 낮았습니다. 선거권이 \n있는 총 100명의 주민 중 단 35명만 \n투표에 참여했습니다.\n그렇습니다. 그중 3번 후보가 \n13표를 얻어 지역 대표로 당선\n되었습니다. 100명 중 13표를 얻은 \n대표자가 과연 지역 주민들의 의견을 잘 \n대변할 수 있을지 우려가 큽니다.\n투표가 끝난 후 텔레비전에서 지역별 투표율을 알려 주는 방송을 봤어. 투표율이 \n높은 지역과 낮은 지역의 차이가 꽤 크더라고. 난 투표를 하고 싶어도 못하는데, 투표하지 않는 \n사람도 있다니……. 투표하지 않는 사람이 많아지면 어떻게 될까?\n생각 깨우기\n신념  굳게 믿는 마음\n당선\n애니메이션\n64\n2 민주주의와 시민 참여\n후보자의 능력과 \n도덕성 등을 \n확인해야 해.\n후보자의 공약과 \n자질을 분석하는 방법을 \n알아볼까?\n후보자가 우리 지역이나 \n나라에 실제로 필요한 \n공약을 제시하는지 따져 \n봐야 해.\n후보자의 공약이 \n실천 가능한 것인지\n분석해 봐야 해.\n선거 과정에서 후보자의 공약과 자질을 꼼꼼히 분석하는 태도도 중요하다. \n공약과 자질을 분석해 보면 후보자가 시민들의 의견을 얼마나 잘 반영할 \n수 있을지 판단할 수 있기 때문이다.\n도덕성  옳은 일을 하려고 \n하는 마음과 행동\n자질  어떤 분야의 일에 대한 \n능력이나 실력의 정도\n후보자를 선택할 때\n또 어떤 점을 고려해야 \n할지 생각해 보자.\n우리나라는 원래 19세부터 선거에 참여할 수 있었지만, \n2020년에 실시한 제21대 국회의원 선거부터 18세도 선거 \n에 참여할 수 있게 되었다. 선거관리위원회에서는 18세 청소\n년들을 대상으로 선거 교육을 실시해 청소년들이 첫 선거에 \n참여할 수 있도록 도왔다. 선거에 참여할 수 있는 나이가 \n낮아지면서 청소년들도 우리 사회와 미래를 위해 소중한 한 \n표를 행사할 수 있게 되었다.\n청소년도 선거에 참여할 수 있을까?\n우리봇이 알려 주는 사회\n65\n1  민주주의와 선거\n생각 깨우기\n우리들의 이야기로 수업을 활기차게 시작해 볼까? \n사회과 교과 역량 \n창의적 사고력\n비판적 사고력\n정보 활용 능력\n의사소통 및\n협업 능력\n문제 해결력 및\n의사 결정력\n색칠한 원이 한 개면 한 차시 학습\n색칠한 원이 두 개면 두 차시 학습\n\n우\n리\n가\n \n들\n려\n주\n는\n \n사\n회\n \n이\n야\n기\n우\n사이\n들\n리\n우리나라에서는 18세 이상 대한민국 국민이라면 누구나 자유롭게 투표에 참여할 수 \n있지만, 투표에 참여하지 않는 사람들도 있다. 반면에 벨기에, 오스트레일리아, 볼리비아 등 \n일부 나라에서는 의무 투표제를 시행해 투표권이 있는 모든 사람이 반드시 투표에 참여하도\n록 하고 있다. 그중 몇몇 나라들은 투표에 참여하지 않는 사람들에게 벌금을 내게 하거나, \n정치 참여를 제한하는 등의 불이익을 주기도 한다. 그 결과, 의무 투표제를 시행하는 나라들\n에서는 투표율이 높게 나타나는 편이다.\n투표하지 않으면\n \n내 권리가 제한된다고요? \n우리나라에서 의무 투표제를 시행한다면 어떤 장점과 단점이 있을지 이야기해 봅시다.\n전 세계에서 처음으로 의무 투표\n제를 도입한 벨기에는 정당한 이유 \n없이 15년 동안 4번 이상 투표에 \n참여하지 않으면 10년 동안의 투표권\n을 박탈해.\n오스트레일리아에서는 \n정당한 이유 없이 투표에 \n참여하지 않은 사람들에게 \n벌금을 내게 해.\n볼리비아에서는 투표에 \n참여하지 않은 사람의 은행 \n거래를 제한하고, 여권 발급\n을 막는 등의 불이익을 줘.\n68\n2 민주주의와 시민 참여\n함께 그리는 평화로운 미래,  \n \n남북 어린이 교류 현장 속으로!\n우\n친\n소\n   \n  \n  \n  \n  \n  \n  \n  \n \n \n우\n리\n \n친\n구\n들\n의\n \n이\n야\n기\n를\n \n소\n개\n합\n니\n다\n \n  \n   \n남북\n 어\n린이\n 평\n화 그\n림전\n 북한 어린이가 쓴 편지\n2023년, 경기도 파주시 교하 도서관에서 남북 어린이 \n평화 그림전 ‘피스 갤러리ʼ가 열렸다. 이 행사에서는 \n2000년대 남북 어린이들이 주고받은 편지와 사진 등이 \n전시되었다. 전시회를 관람한 어린이들은 평화 통일의 \n내용을 담은 그림 편지를 쓰며, 앞으로 남북한 어린이들\n의 교류가 더욱 활발히 이루어지길 소망했다.\n평화 통일의 숲\n가꾸기 대회\n2006년, 서울의 한 초등학교 학생들은 \n설레는 마음으로 개성 땅을 밟았다. ‘개성 \n청소년 평화 통일의 숲 가꾸기’ 대회에 참여\n하기 위해서였다. 이 행사는 개성 송악산을 \n푸르게 가꾸며 한반도에 평화의 숲을 조성\n하고, 평화 통일을 기원하는 의미를 담고 \n있었다. 학생들은 평화와 통일을 상징하는 \n나무를 심으며 평화 통일을 기원했다.\n남북 어린이들이 참여할 수 있는 교류 사례를 더 찾아봅시다. \n24\n1 평화 통일을 위한 노력, 민주화와 산업화\n우친소\n자신의 일을 주도적으로 이끌어 간 멋진 \n친구들의 이야기도 들려줄게.\n우리들 사이\n우리 주변에서 일어나는 흥미로운 이야기\n들이 가득 담겨 있어. \n우행시\n우리, 행복이와 \n과거 여행을 \n떠나 볼까?\n  4·19 혁명 표지석\n4·19 혁명 당시 첫 발포가 있었던 곳에 놓인 표지석을 보며 \n고귀한 희생과 민주주의 정신을 기억할 수 있다.\n  주먹밥 만들기 행사\n5·18 민주화 운동 기념일에는 주먹밥을 만들어 나눠 먹는 \n행사를 하며 공동체 정신을 배운다.\n민주화 이후 과거의 역사를 바로 세우고, 민주화 운동을 기억하며 기념하려는 노력이 \n이어졌다. 이러한 노력 덕분에 우리는 안타까운 희생을 기억하고 민주주의, 인권, 공동체 \n정신, 배려 등의 소중한 가치를 되새길 수 있게 되었다. \n우\n행\n시\n  \n \n우\n리\n와\n \n행\n복\n이\n의\n \n시\n간\n \n여\n행\n발포  총이나 대포를 쏨. \n34\n1 평화 통일을 위한 노력, 민주화와 산업화\n2025-04-24   오후 3:27\n\n다음 내용이 옳으면 ◯표를, 틀리면 ×표를 선택해 오늘의 점심 식단을 찾아봅시다. \n미디어를 올바르게 이용하려는 \n노력은 국가만 하면 된다.\n미디어에서는 잘못된 정보가 \n무분별하게 퍼지기도 한다. \n미디어의 내용은 비판적으로 \n받아들여야 한다.\n미디어의 정보는 모두 믿어도 \n된다. \n정보를 전달하는 매체를 미디어\n라고 한다.\n이번 주제에서 배운 내용을 정리하며 우리가 행복이를 만날 수 있는 길을 찾아봅시다.\no\n김치찌개\nx\n된장찌개\no\n떡갈비\nx\n떡볶이\no\n탕수육\nx\n돈가스\no\n배추김치\nx\n깍두기\no\n달걀말이\nx\n두부구이\n주제마무리\n되돌아가기를 만나면 교과서를 살펴본 후 처음부터 시작합니다.\n98~101쪽\n92~96쪽\n102쪽\n1.  민주주의에서 미디어의 의미와 역할을 이해했나요?\n \n예 \n \n \n아니요 \n \n2.  미디어의 내용을 비판적으로 분석하고 평가할 수 있나요?\n \n예 \n \n \n아니요 \n \n3.  미디어를 올바르게 이용하는 태도를 지니게 되었나요?\n \n예 \n \n \n아니요 \n \n1\n3\n2\n4\n5\n요약 정리\n103\n3  민주주의와 미디어\n사고력\n쑥쑥 \n창의ㆍ융합\n단원마무리\n1  내가 만들고 싶은 세계지도의 주제를 정해 봅시다.\n나만의 세계지도 만들기\n2  세계지도를 만드는 데 필요한 자료를 조사해 봅시다.\n \n          지도에 자료를 골고루 나타낼 수 있도록 대륙별로 한 나라씩 조사합니다.\n도움말\n나는 세계 여러 나라의 \n축구 대표 팀 유니폼을 알려 \n주는 지도를 만들래.\n나는 세계의 전통 음식을 \n지도에 표현해 볼 거야.\n나는 세계의 유명 건축물이 \n나타난 지도를 만들래.\n대륙\n나라\n주제: \n건축물\n대륙\n나라\n주제: \n북아메리카\n미국\n자유의 여신상\n아시아\n중국\n만리장성\n예시\n152\n3 지구, 대륙 그리고 국가들\n3. 지구, 대륙 그리고 국가들\n3  조사한 내용을 바탕으로 활동 자료13  을 활용해 ‘나만의 세계지도’를 만들어 봅시다.\n4  친구들이 만든 지도를 보고, 가장 기억에 남는 세계지도를 이야기해 봅시다.\n5  나만의 세계지도 만들기 활동을 하고 난 후 스스로 평가해 봅시다.\n지도의 주제가 잘 \n드러나도록 대륙별\n로 알맞은 나라를 \n선정했나요?\n다양한 조사 방법\n을 활용해 주제에 \n관한 자료를 수집\n했나요?\n지도 만들기 활동\n에 성실하게 참여\n했나요?\n예시\n153\n단원 마무리\n단원마무리\n용어 콕!\n이 단원의\n물어보세요\n우리에게\n민주 선거의 기본 원칙에는 무엇\n이 있을까요?\n민주 시민으로서 선거에 참여하는 \n바람직한 태도를 알려 주세요.\n선거에 적극적으로 참여하는 모습\n을 보여 주세요.\n선거의 역할은 무엇일까요?\n선거를 하는 까닭은 무엇일까요?\n모든 사람이 한자리에 모여 공동체의 \n중요한 일을 결정하는 것이 어렵기 때문\n이에요.\n선거는 대표자를 선출하고, 선출된 대표자\n의 권력을 견제해 대표자가 책임 있는 \n정치를 하게 해요.\n후보자의 \n2  \n \n과/와 자질을 꼼꼼히 \n분석하는 태도도 중요해요.\n선거에 관심을 가지고 적극적으로 참여\n하는 태도를 가져야 해요. \n보통 선거, 평등 선거, 직접 선거, 비밀 \n선거가 있어요.\n  선거에 참여해 첫 \n투표를 한 학생들\n  선거에 참여하자는 \n캠페인 활동\n민주주의\n1  \n \n이/가 국민\n에게 있는 정치 형태\n선거\n공동체의 대표를 선출\n하는 과정\n국가기관\n법에 따라 나랏일을 \n하는 기관\n정보를 전달하는 매체\n미디어\n 안에 알맞은 말을 쓰거나 활동 자료1 의 붙임딱지를 붙여 봅시다.\n붙임딱지 \n붙임딱지 \n104\n2 민주주의와 시민 참여\n2. 민주주의와 시민 참여\n나만의 누리집 완성하기\n민주주의와 미디어\n카드 뉴스로 보는\n인기 영상\n이 단원의\n국회의원들로 구성된 국민의 \n대표 기관으로, \n3 \n을/를 만들고 \n고치는 일을 함.\n국가기관을 가다 \n- 국회 편\n민주주의에서 미디어의 역할\n•\u0001선거\u0001후보자의\u0001공약,\u0001정책이나\u0001중요한\u0001사회\u0001\n문제에\u0001관한\u0001\n6 \n \n을/를\u0001제공함.\u0001\n•\u0001사회\u0001문제에\u0001대한\u0001사람들의\u0001관심과\u0001참여를\u0001\n이끌고,\u0001여론을\u0001형성함.\n01\n미디어의 비판적 분석\n•정보의\u0001출처,\u0001저자,\u0001날짜\u0001확인하기\n•\n7  \n \n\u0001과/와\u0001의견\u0001구분하기\n•근거와\u0001자료의\u0001타당성\u0001확인하기\n•관련된\u0001사실\u0001더\u0001찾아보기\n국가기관을 가다 \n- 법원 편\n법에 따라 \n5  \n \n을/를 \n하는 기관으로, 개인 간의 다툼\n을 해결하는 역할을 함.\n국가기관을 가다 \n- 행정부 편\n법에 따라 나라 살림을 맡아 \n하는 기관으로, \n4  \n \n \n을/를 중심으로 구성됨.\n02\n단원 게임\n105\n단원 마무리\n단원 마무리\n이번 단원에서 배운 내용들을 모아, \n나만의 특별한 누리집을 만들어 \n보자. 그리고 창의력과 사고력을 \n키울 수 있는 창의・융합 활동으로 \n이번 단원을 마무리할 거야. \n주제 마무리\n재미있는 놀이로 배운 내용을 복습하고, \n코딩을 활용해 얼마나 잘 이해했는지 \n점검해 보자.\n\n1\n  \n \n평\n화\n 통\n일\n을\n \n위\n한\n \n노\n력\n,\n민\n주\n화\n와\n \n산\n업\n화\n10쪽\n1\n 평\n화\n 통\n일\n을 \n위\n한\n \n노\n력\n2\n 민\n주\n화\n와 \n산\n업\n화로\n \n달\n라\n진\n \n생\n활 \n문\n화\n26쪽\n6학년 1학기 사회 수업 시간에는\n어떤 내용이 우리를 기다리고 있을까?\n이 책의차례\n\n2\n54쪽\n3  \n민주\n주의\n와 미\n디어\n90쪽\n2\n \n국\n가\n기\n관\n이 \n하\n는\n \n일\n70쪽\n \n  \n  \n \n민\n주\n주\n의\n와\n \n시\n민\n \n참\n여\n3\n   \n지\n구\n, \n대\n륙 \n그\n리\n고\n \n국\n가\n들\n60°\n90°\n30°\n0°\n30°\n구경: 320 mm\n축척: 1:40,000,000\n60°\n90°\n30°\n0°\n30°\n인 도 양\n북극해\n대서양\n동해\n60°\n60°\n90°\n90°\n120°\n150°\n150°\n180°\n30°\n30°\n0°\n60°\n60°\n90°\n90°\n120°\n150°\n150°\n180°\n30°\n30°\n0°\n110쪽\n1\n \n지\n구\n본\n과\n 지\n도\n로\n 보\n는\n \n세\n계\n2  \n세\n계\n의 \n대\n륙\n, \n대\n양\n, \n나\n라\n132쪽\n1\n 민\n주\n주\n의\n와\n 선\n거\n\n1\n평화 통일을 위한 노력\n1\n민주화와 산업화로 달라진 생활 문화\n2\n  \n   \n    \n    \n     \n    \n 분\n단  \n평화\n 통\n일 \n 민\n주화\n  \n산업\n화  \n평화 통일을 위한 \n노력, 민주화와 \n산업화\n애니메이션\n\n사람들의 이야기를 듣고, 나와 함께 이 단원을 공부할 \n내 친구 하나를 찾아 줘.\n평화 통일 캠페인 전시관에서 받은 한반도기를 \n들고 있어. \n전시회에서 다양한 자료를 받아 간다며 큰 배낭\n을 메고 왔던데?\n나와 가발 만들기 체험을 하고, 또 다른 체험을 \n경험해 보고 싶다고 했어."
  },
  "neighbor_sections": [
    {
      "relation": "next",
      "sheet_name": "2차시",
      "lesson_title": "평화 통일을 위한 노력 — 분단으로 나타난 문제점과 분단이 사회와 생활 에 끼친 영향 알아보기",
      "title_query": "평화 통일을 위한 노력 — 분단으로 나타난 문제점과 분단이 사회와 생활 에 끼친 영향 알아보기",
      "pdf_pages": [
        12,
        13,
        14,
        15
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
