# Runtime Agent Spec: source_validation_agent

아래 AGENT.md는 이 단계의 역할과 경계를 정의한다.
문서에 적힌 역할만 수행하고, 하지 말아야 할 일은 넘지 마라.
출력 형식 요구가 있으면 반드시 지켜라.

# source_validation_agent

## identity
- status: active
- layer: verification
- implementation: `scripts/source_validation_agent.py`

## responsibility
- source boundary 결과를 검토한다.
- 구조 문제, 경계 모호성, 보조자료 매칭 여부를 기록한다.

## inputs
- required:
  - `configs/<config>.json`
  - `source/runtime_config.json`

## outputs
- `source/config_quality_review.json`
- `source/boundary_review.json`
- `source/supplement_review.json`
- `source/source_ai_review.json`
- `source/source_validation.status.json`

## allowed_tools
- local:
  - local JSON inspection
  - deterministic review rules
- model:
  - Gemini sidecar review

## allowed_actions
- source config 품질 검토
- boundary ambiguity 검토
- supplement matching 검토
- source review 요약 생성

## forbidden_actions
- source range 재계산
- lesson/activity 생성
- render/output 변경

## rules
- source consistency validation은 반드시 이 Agent를 통해서만 수행한다.

## hook_contract
- trigger_if_missing:
  - `source/config_quality_review.json`
  - `source/boundary_review.json`
- unlocks:
  - `lesson_analysis_agent`

## success_criteria
- 세 종류의 review JSON이 생성된다.
- blocking issue가 없으면 `source_validation.status.json`이 `succeeded` 또는 `succeeded_with_warning`다.

## failure_modes
- runtime config 누락
- review build 실패
- blocking issue 존재


# Execution Task

너의 역할은 source parsing 결과를 사후 검토하는 review-only agent다.
페이지 경계나 source_ranges를 다시 계산하거나 수정하지 마라.
아래 deterministic review 결과를 종합해 최종 review_result JSON 하나만 반환하라.
마크다운, 설명문, 코드블록, 접두어 없이 JSON object 하나만 반환하라.
최상단 문자와 마지막 문자는 반드시 중괄호여야 한다.
결정은 pass, pass_with_warning, needs_revision, blocked 중 하나여야 한다.
stage는 review_source_ai_agent로 써라.
status는 succeeded, succeeded_with_warning, blocked 중 하나로 맞춰라.
findings의 각 항목은 severity, message, evidence_refs만 가져야 한다.
불필요한 설명 없이 JSON만 반환하라.

Runtime config summary:
{
  "selected_unit": "사회_1_평화 통일을 위한 노력, 민주화와 산업화",
  "resources": [
    {
      "resource_id": "main",
      "label": "교과서",
      "kind": "textbook",
      "pdf_path": "/Users/jonyeock/Desktop/Tool/NumbersAuto/textbook/사회/[사회]6_1_교과서.pdf"
    }
  ],
  "sections": [
    {
      "sheet_name": "1차시",
      "title": "1단원 도입 — [단원 도입] 우리 친구는 누구?",
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
            11
          ]
        }
      ]
    },
    {
      "sheet_name": "2차시",
      "title": "평화 통일을 위한 노력 — 분단으로 나타난 문제점과 분단이 사회와 생활 에 끼친 영향 알아보기",
      "source_ranges": [
        {
          "resource_id": "main",
          "role": "textbook",
          "pdf_pages": [
            12,
            13,
            14,
            15
          ]
        }
      ]
    },
    {
      "sheet_name": "3차시",
      "title": "평화 통일을 위한 노력 — 분단의 흔적이 남아 있는 장소 알아보기",
      "source_ranges": [
        {
          "resource_id": "main",
          "role": "textbook",
          "pdf_pages": [
            16
          ]
        }
      ]
    },
    {
      "sheet_name": "4차시",
      "title": "평화 통일을 위한 노력 — 분단의 장소가 평화의 장소로 바뀐 사례 알아보기",
      "source_ranges": [
        {
          "resource_id": "main",
          "role": "textbook",
          "pdf_pages": [
            12
          ]
        }
      ]
    },
    {
      "sheet_name": "5-6차시",
      "title": "평화 통일을 위한 노력 — 평화 통일을 위한 노력 살펴보기",
      "source_ranges": [
        {
          "resource_id": "main",
          "role": "textbook",
          "pdf_pages": [
            10,
            11,
            12
          ]
        }
      ]
    },
    {
      "sheet_name": "7차시",
      "title": "민주화와 산업화로 달라진 생활 문화 — [주제 도입] 열려라 이야기 / 외쳐라 빙고",
      "source_ranges": [
        {
          "resource_id": "main",
          "role": "textbook",
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
    },
    {
      "sheet_name": "8-9차시",
      "title": "민주화와 산업화로 달라진 생활 문화 — 4·19 혁명 이해하기",
      "source_ranges": [
        {
          "resource_id": "main",
          "role": "textbook",
          "pdf_pages": [
            29
          ]
        }
      ]
    },
    {
      "sheet_name": "10차시",
      "title": "민주화와 산업화로 달라진 생활 문화 — 대통령 직선제와 지방 자치제의 부활 이해하기",
      "source_ranges": [
        {
          "resource_id": "main",
          "role": "textbook",
          "pdf_pages": [
            29
          ]
        }
      ]
    },
    {
      "sheet_name": "11차시",
      "title": "민주화와 산업화로 달라진 생활 문화 — 산업화 과정 이해하기",
      "source_ranges": [
        {
          "resource_id": "main",
          "role": "textbook",
          "pdf_pages": [
            10
          ]
        }
      ]
    },
    {
      "sheet_name": "12-13차시",
      "title": "민주화와 산업화로 달라진 생활 문화 — 산업화로 달라진 사회와 생활 문화 이해하기",
      "source_ranges": [
        {
          "resource_id": "main",
          "role": "textbook",
          "pdf_pages": [
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
            48
          ]
        }
      ]
    },
    {
      "sheet_name": "14차시",
      "title": "1단원 정리 — [단원 마무리] 나만의 누리집 완성하기 / 창의·융 합 사고력 쑥쑥",
      "source_ranges": [
        {
          "resource_id": "main",
          "role": "textbook",
          "pdf_pages": [
            49
          ]
        }
      ]
    },
    {
      "sheet_name": "1차시",
      "title": "2단원 도입 — [단원 도입] 우리 친구는 누구?",
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
            53
          ]
        }
      ]
    },
    {
      "sheet_name": "2차시",
      "title": "민주주의와 선거 — 선거의 의미와 중요성 파악하기",
      "source_ranges": [
        {
          "resource_id": "main",
          "role": "textbook",
          "pdf_pages": [
            54
          ]
        }
      ]
    },
    {
      "sheet_name": "3차시",
      "title": "민주주의와 선거 — 민주주의에서 선거의 역할 파악하기",
      "source_ranges": [
        {
          "resource_id": "main",
          "role": "textbook",
          "pdf_pages": [
            54
          ]
        }
      ]
    },
    {
      "sheet_name": "4-5차시",
      "title": "민주주의와 선거 — 우리나라의 선거 과정 살펴보기",
      "source_ranges": [
        {
          "resource_id": "main",
          "role": "textbook",
          "pdf_pages": [
            54
          ]
        }
      ]
    },
    {
      "sheet_name": "6-7차시",
      "title": "민주주의와 선거 — 선거에 적극적으로 참여해야 하는 까닭 알아보기",
      "source_ranges": [
        {
          "resource_id": "main",
          "role": "textbook",
          "pdf_pages": [
            32
          ]
        }
      ]
    },
    {
      "sheet_name": "8차시",
      "title": "국가기관이 하는 일 — [주제 도입] 열려라 이야기 / 외쳐라 빙고",
      "source_ranges": [
        {
          "resource_id": "main",
          "role": "textbook",
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
        }
      ]
    },
    {
      "sheet_name": "9-10차시",
      "title": "국가기관이 하는 일 — 국회의 구성과 하는 일 파악하기",
      "source_ranges": [
        {
          "resource_id": "main",
          "role": "textbook",
          "pdf_pages": [
            74
          ]
        }
      ]
    },
    {
      "sheet_name": "11차시",
      "title": "국가기관이 하는 일 — 행정부의 구성과 하는 일 파악하기",
      "source_ranges": [
        {
          "resource_id": "main",
          "role": "textbook",
          "pdf_pages": [
            74
          ]
        }
      ]
    },
    {
      "sheet_name": "12차시",
      "title": "국가기관이 하는 일 — 법원의 구성과 하는 일 파악하기",
      "source_ranges": [
        {
          "resource_id": "main",
          "role": "textbook",
          "pdf_pages": [
            73
          ]
        }
      ]
    },
    {
      "sheet_name": "13차시",
      "title": "국가기관이 하는 일 — 권력 분립의 의미와 중요성 탐구하기",
      "source_ranges": [
        {
          "resource_id": "main",
          "role": "textbook",
          "pdf_pages": [
            54
          ]
        }
      ]
    },
    {
      "sheet_name": "14차시",
      "title": "민주주의와 미디어 — [주제 도입] 열려라 이야기 / 외쳐라 빙고",
      "source_ranges": [
        {
          "resource_id": "main",
          "role": "textbook",
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
        }
      ]
    },
    {
      "sheet_name": "15차시",
      "title": "민주주의와 미디어 — 미디어의 정보 제공 역할 알아보기",
      "source_ranges": [
        {
          "resource_id": "main",
          "role": "textbook",
          "pdf_pages": [
            83,
            84,
            85,
            86,
            87,
            88,
            89
          ]
        }
      ]
    },
    {
      "sheet_name": "16차시",
      "title": "민주주의와 미디어 — 미디어의 내용을 비판적으로 분석해야 하는 까 닭 알아보기",
      "source_ranges": [
        {
          "resource_id": "main",
          "role": "textbook",
          "pdf_pages": [
            90
          ]
        }
      ]
    },
    {
      "sheet_name": "17-18차시",
      "title": "민주주의와 미디어 — 미디어를 올바르게 이용하는 방법 알아보기",
      "source_ranges": [
        {
          "resource_id": "main",
          "role": "textbook",
          "pdf_pages": [
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
            48
          ]
        }
      ]
    },
    {
      "sheet_name": "19차시",
      "title": "2단원 정리 — [단원 마무리] 나만의 누리집 완성하기 / 창의·융 합 사고력 쑥쑥",
      "source_ranges": [
        {
          "resource_id": "main",
          "role": "textbook",
          "pdf_pages": [
            49
          ]
        }
      ]
    },
    {
      "sheet_name": "1차시",
      "title": "3단원 도입 — [단원 도입] 우리 친구는 누구?",
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
      ]
    },
    {
      "sheet_name": "2-3차시",
      "title": "지구본과 지도로 보는 세계 — 지구본의 특징 살펴보기",
      "source_ranges": [
        {
          "resource_id": "main",
          "role": "textbook",
          "pdf_pages": [
            112,
            113,
            114,
            115
          ]
        }
      ]
    },
    {
      "sheet_name": "4차시",
      "title": "지구본과 지도로 보는 세계 — 디지털 공간 영상 정보의 의미 알아보기",
      "source_ranges": [
        {
          "resource_id": "main",
          "role": "textbook",
          "pdf_pages": [
            116
          ]
        }
      ]
    },
    {
      "sheet_name": "5차시",
      "title": "지구본과 지도로 보는 세계 — 위도와 위선의 의미 알아보기",
      "source_ranges": [
        {
          "resource_id": "main",
          "role": "textbook",
          "pdf_pages": [
            83
          ]
        }
      ]
    },
    {
      "sheet_name": "6차시",
      "title": "지구본과 지도로 보는 세계 — 경도와 경선의 의미 알아보기",
      "source_ranges": [
        {
          "resource_id": "main",
          "role": "textbook",
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
    },
    {
      "sheet_name": "7차시",
      "title": "지구본과 지도로 보는 세계 — 위도와 경도를 이용해 위치를 표현하는 방법 살 펴보기",
      "source_ranges": [
        {
          "resource_id": "main",
          "role": "textbook",
          "pdf_pages": [
            110
          ]
        }
      ]
    },
    {
      "sheet_name": "8차시",
      "title": "세계의 대륙, 대양, 나라 — [주제 도입] 열려라 이야기 / 외쳐라 빙고",
      "source_ranges": [
        {
          "resource_id": "main",
          "role": "textbook",
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
            111,
            112,
            113,
            114,
            115,
            116,
            117,
            118,
            119,
            120,
            121,
            122,
            123,
            124,
            125,
            126,
            127
          ]
        }
      ]
    },
    {
      "sheet_name": "9차시",
      "title": "세계의 대륙, 대양, 나라 — 우리나라의 위치 특징 파악하기",
      "source_ranges": [
        {
          "resource_id": "main",
          "role": "textbook",
          "pdf_pages": [
            128,
            129,
            130
          ]
        }
      ]
    },
    {
      "sheet_name": "10차시",
      "title": "세계의 대륙, 대양, 나라 — 아시아 주요 나라들의 위치 알아보기",
      "source_ranges": [
        {
          "resource_id": "main",
          "role": "textbook",
          "pdf_pages": [
            131
          ]
        }
      ]
    },
    {
      "sheet_name": "11차시",
      "title": "세계의 대륙, 대양, 나라 — 유럽 주요 나라들의 위치 알아보기",
      "source_ranges": [
        {
          "resource_id": "main",
          "role": "textbook",
          "pdf_pages": [
            128,
            129,
            130
          ]
        }
      ]
    },
    {
      "sheet_name": "12차시",
      "title": "세계의 대륙, 대양, 나라 — 북아메리카와 남아메리카 주요 나라들의 위치 알아보기",
      "source_ranges": [
        {
          "resource_id": "main",
          "role": "textbook",
          "pdf_pages": [
            131
          ]
        }
      ]
    },
    {
      "sheet_name": "13차시",
      "title": "세계의 대륙, 대양, 나라 — 아프리카 주요 나라들의 위치 알아보기",
      "source_ranges": [
        {
          "resource_id": "main",
          "role": "textbook",
          "pdf_pages": [
            131
          ]
        }
      ]
    },
    {
      "sheet_name": "14차시",
      "title": "세계의 대륙, 대양, 나라 — 오세아니아 주요 나라들의 위치 알아보기",
      "source_ranges": [
        {
          "resource_id": "main",
          "role": "textbook",
          "pdf_pages": [
            131
          ]
        }
      ]
    },
    {
      "sheet_name": "15차시",
      "title": "3단원 정리 — [단원 마무리] 나만의 누리집 완성하기 / 창의·융 합 사고력 쑥쑥",
      "source_ranges": [
        {
          "resource_id": "main",
          "role": "textbook",
          "pdf_pages": [
            49
          ]
        }
      ]
    }
  ]
}

Config quality review:
{
  "schema_version": "1.0.0",
  "stage": "review_source_config",
  "lesson_id": null,
  "status": "succeeded_with_warning",
  "decision": "pass_with_warning",
  "findings": [
    {
      "severity": "warning",
      "message": "1차시의 시작 쿼리가 여러 페이지에 매칭됩니다.",
      "evidence_refs": [
        "1단원 도입 — [단원 도입] 우리 친구는 누구?"
      ]
    },
    {
      "severity": "warning",
      "message": "2차시의 시작 쿼리가 여러 페이지에 매칭됩니다.",
      "evidence_refs": [
        "평화 통일을 위한 노력 — 분단으로 나타난 문제점과 분단이 사회와 생활 에 끼친 영향 알아보기"
      ]
    },
    {
      "severity": "warning",
      "message": "3차시의 시작 쿼리가 여러 페이지에 매칭됩니다.",
      "evidence_refs": [
        "평화 통일을 위한 노력 — 분단의 흔적이 남아 있는 장소 알아보기"
      ]
    },
    {
      "severity": "warning",
      "message": "4차시의 시작 쿼리가 여러 페이지에 매칭됩니다.",
      "evidence_refs": [
        "평화 통일을 위한 노력 — 분단의 장소가 평화의 장소로 바뀐 사례 알아보기"
      ]
    },
    {
      "severity": "warning",
      "message": "5-6차시의 시작 쿼리가 여러 페이지에 매칭됩니다.",
      "evidence_refs": [
        "평화 통일을 위한 노력 — 평화 통일을 위한 노력 살펴보기"
      ]
    },
    {
      "severity": "warning",
      "message": "7차시의 시작 쿼리가 여러 페이지에 매칭됩니다.",
      "evidence_refs": [
        "민주화와 산업화로 달라진 생활 문화 — [주제 도입] 열려라 이야기 / 외쳐라 빙고"
      ]
    },
    {
      "severity": "warning",
      "message": "8-9차시의 시작 쿼리가 여러 페이지에 매칭됩니다.",
      "evidence_refs": [
        "민주화와 산업화로 달라진 생활 문화 — 4·19 혁명 이해하기"
      ]
    },
    {
      "severity": "warning",
      "message": "10차시의 시작 쿼리가 여러 페이지에 매칭됩니다.",
      "evidence_refs": [
        "민주화와 산업화로 달라진 생활 문화 — 대통령 직선제와 지방 자치제의 부활 이해하기"
      ]
    },
    {
      "severity": "warning",
      "message": "11차시의 시작 쿼리가 여러 페이지에 매칭됩니다.",
      "evidence_refs": [
        "민주화와 산업화로 달라진 생활 문화 — 산업화 과정 이해하기"
      ]
    },
    {
      "severity": "warning",
      "message": "12-13차시의 시작 쿼리가 여러 페이지에 매칭됩니다.",
      "evidence_refs": [
        "민주화와 산업화로 달라진 생활 문화 — 산업화로 달라진 사회와 생활 문화 이해하기"
      ]
    },
    {
      "severity": "warning",
      "message": "14차시의 시작 쿼리가 여러 페이지에 매칭됩니다.",
      "evidence_refs": [
        "1단원 정리 — [단원 마무리] 나만의 누리집 완성하기 / 창의·융 합 사고력 쑥쑥"
      ]
    },
    {
      "severity": "warning",
      "message": "1차시의 시작 쿼리가 여러 페이지에 매칭됩니다.",
      "evidence_refs": [
        "2단원 도입 — [단원 도입] 우리 친구는 누구?"
      ]
    },
    {
      "severity": "warning",
      "message": "2차시의 시작 쿼리가 여러 페이지에 매칭됩니다.",
      "evidence_refs": [
        "민주주의와 선거 — 선거의 의미와 중요성 파악하기"
      ]
    },
    {
      "severity": "warning",
      "message": "3차시의 시작 쿼리가 여러 페이지에 매칭됩니다.",
      "evidence_refs": [
        "민주주의와 선거 — 민주주의에서 선거의 역할 파악하기"
      ]
    },
    {
      "severity": "warning",
      "message": "4-5차시의 시작 쿼리가 여러 페이지에 매칭됩니다.",
      "evidence_refs": [
        "민주주의와 선거 — 우리나라의 선거 과정 살펴보기"
      ]
    },
    {
      "severity": "warning",
      "message": "6-7차시의 시작 쿼리가 여러 페이지에 매칭됩니다.",
      "evidence_refs": [
        "민주주의와 선거 — 선거에 적극적으로 참여해야 하는 까닭 알아보기"
      ]
    },
    {
      "severity": "warning",
      "message": "8차시의 시작 쿼리가 여러 페이지에 매칭됩니다.",
      "evidence_refs": [
        "국가기관이 하는 일 — [주제 도입] 열려라 이야기 / 외쳐라 빙고"
      ]
    },
    {
      "severity": "warning",
      "message": "9-10차시의 시작 쿼리가 여러 페이지에 매칭됩니다.",
      "evidence_refs": [
        "국가기관이 하는 일 — 국회의 구성과 하는 일 파악하기"
      ]
    },
    {
      "severity": "warning",
      "message": "11차시의 시작 쿼리가 여러 페이지에 매칭됩니다.",
      "evidence_refs": [
        "국가기관이 하는 일 — 행정부의 구성과 하는 일 파악하기"
      ]
    },
    {
      "severity": "warning",
      "message": "12차시의 시작 쿼리가 여러 페이지에 매칭됩니다.",
      "evidence_refs": [
        "국가기관이 하는 일 — 법원의 구성과 하는 일 파악하기"
      ]
    },
    {
      "severity": "warning",
      "message": "13차시의 시작 쿼리가 여러 페이지에 매칭됩니다.",
      "evidence_refs": [
        "국가기관이 하는 일 — 권력 분립의 의미와 중요성 탐구하기"
      ]
    },
    {
      "severity": "warning",
      "message": "14차시의 시작 쿼리가 여러 페이지에 매칭됩니다.",
      "evidence_refs": [
        "민주주의와 미디어 — [주제 도입] 열려라 이야기 / 외쳐라 빙고"
      ]
    },
    {
      "severity": "warning",
      "message": "15차시의 시작 쿼리가 여러 페이지에 매칭됩니다.",
      "evidence_refs": [
        "민주주의와 미디어 — 미디어의 정보 제공 역할 알아보기"
      ]
    },
    {
      "severity": "warning",
      "message": "16차시의 시작 쿼리가 여러 페이지에 매칭됩니다.",
      "evidence_refs": [
        "민주주의와 미디어 — 미디어의 내용을 비판적으로 분석해야 하는 까 닭 알아보기"
      ]
    },
    {
      "severity": "warning",
      "message": "17-18차시의 시작 쿼리가 여러 페이지에 매칭됩니다.",
      "evidence_refs": [
        "민주주의와 미디어 — 미디어를 올바르게 이용하는 방법 알아보기"
      ]
    },
    {
      "severity": "warning",
      "message": "19차시의 시작 쿼리가 여러 페이지에 매칭됩니다.",
      "evidence_refs": [
        "2단원 정리 — [단원 마무리] 나만의 누리집 완성하기 / 창의·융 합 사고력 쑥쑥"
      ]
    },
    {
      "severity": "warning",
      "message": "1차시의 시작 쿼리가 여러 페이지에 매칭됩니다.",
      "evidence_refs": [
        "3단원 도입 — [단원 도입] 우리 친구는 누구?"
      ]
    },
    {
      "severity": "warning",
      "message": "2-3차시의 시작 쿼리가 여러 페이지에 매칭됩니다.",
      "evidence_refs": [
        "지구본과 지도로 보는 세계 — 지구본의 특징 살펴보기"
      ]
    },
    {
      "severity": "warning",
      "message": "4차시의 시작 쿼리가 여러 페이지에 매칭됩니다.",
      "evidence_refs": [
        "지구본과 지도로 보는 세계 — 디지털 공간 영상 정보의 의미 알아보기"
      ]
    },
    {
      "severity": "warning",
      "message": "5차시의 시작 쿼리가 여러 페이지에 매칭됩니다.",
      "evidence_refs": [
        "지구본과 지도로 보는 세계 — 위도와 위선의 의미 알아보기"
      ]
    },
    {
      "severity": "warning",
      "message": "6차시의 시작 쿼리가 여러 페이지에 매칭됩니다.",
      "evidence_refs": [
        "지구본과 지도로 보는 세계 — 경도와 경선의 의미 알아보기"
      ]
    },
    {
      "severity": "warning",
      "message": "7차시의 시작 쿼리가 여러 페이지에 매칭됩니다.",
      "evidence_refs": [
        "지구본과 지도로 보는 세계 — 위도와 경도를 이용해 위치를 표현하는 방법 살 펴보기"
      ]
    },
    {
      "severity": "warning",
      "message": "8차시의 시작 쿼리가 여러 페이지에 매칭됩니다.",
      "evidence_refs": [
        "세계의 대륙, 대양, 나라 — [주제 도입] 열려라 이야기 / 외쳐라 빙고"
      ]
    },
    {
      "severity": "warning",
      "message": "9차시의 시작 쿼리가 여러 페이지에 매칭됩니다.",
      "evidence_refs": [
        "세계의 대륙, 대양, 나라 — 우리나라의 위치 특징 파악하기"
      ]
    },
    {
      "severity": "warning",
      "message": "10차시의 시작 쿼리가 여러 페이지에 매칭됩니다.",
      "evidence_refs": [
        "세계의 대륙, 대양, 나라 — 아시아 주요 나라들의 위치 알아보기"
      ]
    },
    {
      "severity": "warning",
      "message": "11차시의 시작 쿼리가 여러 페이지에 매칭됩니다.",
      "evidence_refs": [
        "세계의 대륙, 대양, 나라 — 유럽 주요 나라들의 위치 알아보기"
      ]
    },
    {
      "severity": "warning",
      "message": "12차시의 시작 쿼리가 여러 페이지에 매칭됩니다.",
      "evidence_refs": [
        "세계의 대륙, 대양, 나라 — 북아메리카와 남아메리카 주요 나라들의 위치 알아보기"
      ]
    },
    {
      "severity": "warning",
      "message": "13차시의 시작 쿼리가 여러 페이지에 매칭됩니다.",
      "evidence_refs": [
        "세계의 대륙, 대양, 나라 — 아프리카 주요 나라들의 위치 알아보기"
      ]
    },
    {
      "severity": "warning",
      "message": "14차시의 시작 쿼리가 여러 페이지에 매칭됩니다.",
      "evidence_refs": [
        "세계의 대륙, 대양, 나라 — 오세아니아 주요 나라들의 위치 알아보기"
      ]
    },
    {
      "severity": "warning",
      "message": "15차시의 시작 쿼리가 여러 페이지에 매칭됩니다.",
      "evidence_refs": [
        "3단원 정리 — [단원 마무리] 나만의 누리집 완성하기 / 창의·융 합 사고력 쑥쑥"
      ]
    }
  ],
  "blocking_issues": [],
  "warnings": [
    "1차시: source 'main' title_query matched 5 pages",
    "2차시: source 'main' title_query matched 5 pages",
    "3차시: source 'main' title_query matched 5 pages",
    "4차시: source 'main' title_query matched 5 pages",
    "5-6차시: source 'main' title_query matched 5 pages",
    "7차시: source 'main' title_query matched 5 pages",
    "8-9차시: source 'main' title_query matched 4 pages",
    "10차시: source 'main' title_query matched 5 pages",
    "11차시: source 'main' title_query matched 5 pages",
    "12-13차시: source 'main' title_query matched 5 pages",
    "14차시: source 'main' title_query matched 5 pages",
    "1차시: source 'main' title_query matched 5 pages",
    "2차시: source 'main' title_query matched 5 pages",
    "3차시: source 'main' title_query matched 5 pages",
    "4-5차시: source 'main' title_query matched 5 pages",
    "6-7차시: source 'main' title_query matched 5 pages",
    "8차시: source 'main' title_query matched 5 pages",
    "9-10차시: source 'main' title_query matched 5 pages",
    "11차시: source 'main' title_query matched 5 pages",
    "12차시: source 'main' title_query matched 5 pages",
    "13차시: source 'main' title_query matched 5 pages",
    "14차시: source 'main' title_query matched 5 pages",
    "15차시: source 'main' title_query matched 5 pages",
    "16차시: source 'main' title_query matched 5 pages",
    "17-18차시: source 'main' title_query matched 5 pages",
    "19차시: source 'main' title_query matched 5 pages",
    "1차시: source 'main' title_query matched 5 pages",
    "2-3차시: source 'main' title_query matched 5 pages",
    "4차시: source 'main' title_query matched 5 pages",
    "5차시: source 'main' title_query matched 5 pages",
    "6차시: source 'main' title_query matched 5 pages",
    "7차시: source 'main' title_query matched 5 pages",
    "8차시: source 'main' title_query matched 5 pages",
    "9차시: source 'main' title_query matched 5 pages",
    "10차시: source 'main' title_query matched 5 pages",
    "11차시: source 'main' title_query matched 5 pages",
    "12차시: source 'main' title_query matched 5 pages",
    "13차시: source 'main' title_query matched 5 pages",
    "14차시: source 'main' title_query matched 5 pages",
    "15차시: source 'main' title_query matched 5 pages"
  ]
}

Boundary review:
{
  "schema_version": "1.0.0",
  "stage": "review_source_boundary",
  "lesson_id": null,
  "status": "succeeded_with_warning",
  "decision": "pass_with_warning",
  "findings": [
    {
      "severity": "warning",
      "message": "1차시의 경계 판정 신뢰도가 낮습니다.",
      "evidence_refs": [
        "lesson-001"
      ]
    },
    {
      "severity": "warning",
      "message": "2차시의 경계 판정 신뢰도가 낮습니다.",
      "evidence_refs": [
        "lesson-002"
      ]
    },
    {
      "severity": "warning",
      "message": "3차시의 경계 판정 신뢰도가 낮습니다.",
      "evidence_refs": [
        "lesson-003"
      ]
    },
    {
      "severity": "warning",
      "message": "4차시의 시작 페이지가 이전 차시와 겹칩니다.",
      "evidence_refs": [
        "lesson-004"
      ]
    },
    {
      "severity": "warning",
      "message": "4차시의 경계 판정 신뢰도가 낮습니다.",
      "evidence_refs": [
        "lesson-004"
      ]
    },
    {
      "severity": "warning",
      "message": "5-6차시의 시작 페이지가 이전 차시와 겹칩니다.",
      "evidence_refs": [
        "lesson-005"
      ]
    },
    {
      "severity": "warning",
      "message": "5-6차시의 경계 판정 신뢰도가 낮습니다.",
      "evidence_refs": [
        "lesson-005"
      ]
    },
    {
      "severity": "warning",
      "message": "7차시의 경계 판정 신뢰도가 낮습니다.",
      "evidence_refs": [
        "lesson-006"
      ]
    },
    {
      "severity": "warning",
      "message": "8-9차시의 경계 판정 신뢰도가 낮습니다.",
      "evidence_refs": [
        "lesson-007"
      ]
    },
    {
      "severity": "warning",
      "message": "10차시의 시작 페이지가 이전 차시와 겹칩니다.",
      "evidence_refs": [
        "lesson-008"
      ]
    },
    {
      "severity": "warning",
      "message": "10차시의 경계 판정 신뢰도가 낮습니다.",
      "evidence_refs": [
        "lesson-008"
      ]
    },
    {
      "severity": "warning",
      "message": "11차시의 시작 페이지가 이전 차시와 겹칩니다.",
      "evidence_refs": [
        "lesson-009"
      ]
    },
    {
      "severity": "warning",
      "message": "11차시의 경계 판정 신뢰도가 낮습니다.",
      "evidence_refs": [
        "lesson-009"
      ]
    },
    {
      "severity": "warning",
      "message": "12-13차시의 시작 페이지가 이전 차시와 겹칩니다.",
      "evidence_refs": [
        "lesson-010"
      ]
    },
    {
      "severity": "warning",
      "message": "12-13차시의 경계 판정 신뢰도가 낮습니다.",
      "evidence_refs": [
        "lesson-010"
      ]
    },
    {
      "severity": "warning",
      "message": "14차시의 경계 판정 신뢰도가 낮습니다.",
      "evidence_refs": [
        "lesson-011"
      ]
    },
    {
      "severity": "warning",
      "message": "1차시의 시작 페이지가 이전 차시와 겹칩니다.",
      "evidence_refs": [
        "lesson-012"
      ]
    },
    {
      "severity": "warning",
      "message": "1차시의 경계 판정 신뢰도가 낮습니다.",
      "evidence_refs": [
        "lesson-012"
      ]
    },
    {
      "severity": "warning",
      "message": "2차시의 경계 판정 신뢰도가 낮습니다.",
      "evidence_refs": [
        "lesson-013"
      ]
    },
    {
      "severity": "warning",
      "message": "3차시의 시작 페이지가 이전 차시와 겹칩니다.",
      "evidence_refs": [
        "lesson-014"
      ]
    },
    {
      "severity": "warning",
      "message": "3차시의 경계 판정 신뢰도가 낮습니다.",
      "evidence_refs": [
        "lesson-014"
      ]
    },
    {
      "severity": "warning",
      "message": "4-5차시의 시작 페이지가 이전 차시와 겹칩니다.",
      "evidence_refs": [
        "lesson-015"
      ]
    },
    {
      "severity": "warning",
      "message": "4-5차시의 경계 판정 신뢰도가 낮습니다.",
      "evidence_refs": [
        "lesson-015"
      ]
    },
    {
      "severity": "warning",
      "message": "6-7차시의 시작 페이지가 이전 차시와 겹칩니다.",
      "evidence_refs": [
        "lesson-016"
      ]
    },
    {
      "severity": "warning",
      "message": "6-7차시의 경계 판정 신뢰도가 낮습니다.",
      "evidence_refs": [
        "lesson-016"
      ]
    },
    {
      "severity": "warning",
      "message": "8차시의 시작 페이지가 이전 차시와 겹칩니다.",
      "evidence_refs": [
        "lesson-017"
      ]
    },
    {
      "severity": "warning",
      "message": "8차시의 경계 판정 신뢰도가 낮습니다.",
      "evidence_refs": [
        "lesson-017"
      ]
    },
    {
      "severity": "warning",
      "message": "9-10차시의 경계 판정 신뢰도가 낮습니다.",
      "evidence_refs": [
        "lesson-018"
      ]
    },
    {
      "severity": "warning",
      "message": "11차시의 시작 페이지가 이전 차시와 겹칩니다.",
      "evidence_refs": [
        "lesson-019"
      ]
    },
    {
      "severity": "warning",
      "message": "11차시의 경계 판정 신뢰도가 낮습니다.",
      "evidence_refs": [
        "lesson-019"
      ]
    },
    {
      "severity": "warning",
      "message": "12차시의 시작 페이지가 이전 차시와 겹칩니다.",
      "evidence_refs": [
        "lesson-020"
      ]
    },
    {
      "severity": "warning",
      "message": "12차시의 경계 판정 신뢰도가 낮습니다.",
      "evidence_refs": [
        "lesson-020"
      ]
    },
    {
      "severity": "warning",
      "message": "13차시의 시작 페이지가 이전 차시와 겹칩니다.",
      "evidence_refs": [
        "lesson-021"
      ]
    },
    {
      "severity": "warning",
      "message": "13차시의 경계 판정 신뢰도가 낮습니다.",
      "evidence_refs": [
        "lesson-021"
      ]
    },
    {
      "severity": "warning",
      "message": "14차시의 시작 페이지가 이전 차시와 겹칩니다.",
      "evidence_refs": [
        "lesson-022"
      ]
    },
    {
      "severity": "warning",
      "message": "14차시의 경계 판정 신뢰도가 낮습니다.",
      "evidence_refs": [
        "lesson-022"
      ]
    },
    {
      "severity": "warning",
      "message": "15차시의 경계 판정 신뢰도가 낮습니다.",
      "evidence_refs": [
        "lesson-023"
      ]
    },
    {
      "severity": "warning",
      "message": "16차시의 경계 판정 신뢰도가 낮습니다.",
      "evidence_refs": [
        "lesson-024"
      ]
    },
    {
      "severity": "warning",
      "message": "17-18차시의 시작 페이지가 이전 차시와 겹칩니다.",
      "evidence_refs": [
        "lesson-025"
      ]
    },
    {
      "severity": "warning",
      "message": "17-18차시의 경계 판정 신뢰도가 낮습니다.",
      "evidence_refs": [
        "lesson-025"
      ]
    },
    {
      "severity": "warning",
      "message": "19차시의 경계 판정 신뢰도가 낮습니다.",
      "evidence_refs": [
        "lesson-026"
      ]
    },
    {
      "severity": "warning",
      "message": "1차시의 시작 페이지가 이전 차시와 겹칩니다.",
      "evidence_refs": [
        "lesson-027"
      ]
    },
    {
      "severity": "warning",
      "message": "1차시의 경계 판정 신뢰도가 낮습니다.",
      "evidence_refs": [
        "lesson-027"
      ]
    },
    {
      "severity": "warning",
      "message": "2-3차시의 경계 판정 신뢰도가 낮습니다.",
      "evidence_refs": [
        "lesson-028"
      ]
    },
    {
      "severity": "warning",
      "message": "4차시의 경계 판정 신뢰도가 낮습니다.",
      "evidence_refs": [
        "lesson-029"
      ]
    },
    {
      "severity": "warning",
      "message": "5차시의 시작 페이지가 이전 차시와 겹칩니다.",
      "evidence_refs": [
        "lesson-030"
      ]
    },
    {
      "severity": "warning",
      "message": "5차시의 경계 판정 신뢰도가 낮습니다.",
      "evidence_refs": [
        "lesson-030"
      ]
    },
    {
      "severity": "warning",
      "message": "6차시의 시작 페이지가 이전 차시와 겹칩니다.",
      "evidence_refs": [
        "lesson-031"
      ]
    },
    {
      "severity": "warning",
      "message": "6차시의 경계 판정 신뢰도가 낮습니다.",
      "evidence_refs": [
        "lesson-031"
      ]
    },
    {
      "severity": "warning",
      "message": "7차시의 경계 판정 신뢰도가 낮습니다.",
      "evidence_refs": [
        "lesson-032"
      ]
    },
    {
      "severity": "warning",
      "message": "8차시의 시작 페이지가 이전 차시와 겹칩니다.",
      "evidence_refs": [
        "lesson-033"
      ]
    },
    {
      "severity": "warning",
      "message": "8차시의 경계 판정 신뢰도가 낮습니다.",
      "evidence_refs": [
        "lesson-033"
      ]
    },
    {
      "severity": "warning",
      "message": "9차시의 경계 판정 신뢰도가 낮습니다.",
      "evidence_refs": [
        "lesson-034"
      ]
    },
    {
      "severity": "warning",
      "message": "10차시의 경계 판정 신뢰도가 낮습니다.",
      "evidence_refs": [
        "lesson-035"
      ]
    },
    {
      "severity": "warning",
      "message": "11차시의 시작 페이지가 이전 차시와 겹칩니다.",
      "evidence_refs": [
        "lesson-036"
      ]
    },
    {
      "severity": "warning",
      "message": "11차시의 경계 판정 신뢰도가 낮습니다.",
      "evidence_refs": [
        "lesson-036"
      ]
    },
    {
      "severity": "warning",
      "message": "12차시의 경계 판정 신뢰도가 낮습니다.",
      "evidence_refs": [
        "lesson-037"
      ]
    },
    {
      "severity": "warning",
      "message": "13차시의 시작 페이지가 이전 차시와 겹칩니다.",
      "evidence_refs": [
        "lesson-038"
      ]
    },
    {
      "severity": "warning",
      "message": "13차시의 경계 판정 신뢰도가 낮습니다.",
      "evidence_refs": [
        "lesson-038"
      ]
    },
    {
      "severity": "warning",
      "message": "14차시의 시작 페이지가 이전 차시와 겹칩니다.",
      "evidence_refs": [
        "lesson-039"
      ]
    },
    {
      "severity": "warning",
      "message": "14차시의 경계 판정 신뢰도가 낮습니다.",
      "evidence_refs": [
        "lesson-039"
      ]
    },
    {
      "severity": "warning",
      "message": "15차시의 시작 페이지가 이전 차시와 겹칩니다.",
      "evidence_refs": [
        "lesson-040"
      ]
    },
    {
      "severity": "warning",
      "message": "15차시의 경계 판정 신뢰도가 낮습니다.",
      "evidence_refs": [
        "lesson-040"
      ]
    }
  ],
  "blocking_issues": [],
  "warnings": [
    "lesson-001: boundary is low_confidence",
    "lesson-002: boundary is low_confidence",
    "lesson-003: boundary is low_confidence",
    "lesson-004: start_page overlaps with previous lesson boundary",
    "lesson-004: boundary is low_confidence",
    "lesson-005: start_page overlaps with previous lesson boundary",
    "lesson-005: boundary is low_confidence",
    "lesson-006: boundary is low_confidence",
    "lesson-007: boundary is low_confidence",
    "lesson-008: start_page overlaps with previous lesson boundary",
    "lesson-008: boundary is low_confidence",
    "lesson-009: start_page overlaps with previous lesson boundary",
    "lesson-009: boundary is low_confidence",
    "lesson-010: start_page overlaps with previous lesson boundary",
    "lesson-010: boundary is low_confidence",
    "lesson-011: boundary is low_confidence",
    "lesson-012: start_page overlaps with previous lesson boundary",
    "lesson-012: boundary is low_confidence",
    "lesson-013: boundary is low_confidence",
    "lesson-014: start_page overlaps with previous lesson boundary",
    "lesson-014: boundary is low_confidence",
    "lesson-015: start_page overlaps with previous lesson boundary",
    "lesson-015: boundary is low_confidence",
    "lesson-016: start_page overlaps with previous lesson boundary",
    "lesson-016: boundary is low_confidence",
    "lesson-017: start_page overlaps with previous lesson boundary",
    "lesson-017: boundary is low_confidence",
    "lesson-018: boundary is low_confidence",
    "lesson-019: start_page overlaps with previous lesson boundary",
    "lesson-019: boundary is low_confidence",
    "lesson-020: start_page overlaps with previous lesson boundary",
    "lesson-020: boundary is low_confidence",
    "lesson-021: start_page overlaps with previous lesson boundary",
    "lesson-021: boundary is low_confidence",
    "lesson-022: start_page overlaps with previous lesson boundary",
    "lesson-022: boundary is low_confidence",
    "lesson-023: boundary is low_confidence",
    "lesson-024: boundary is low_confidence",
    "lesson-025: start_page overlaps with previous lesson boundary",
    "lesson-025: boundary is low_confidence",
    "lesson-026: boundary is low_confidence",
    "lesson-027: start_page overlaps with previous lesson boundary",
    "lesson-027: boundary is low_confidence",
    "lesson-028: boundary is low_confidence",
    "lesson-029: boundary is low_confidence",
    "lesson-030: start_page overlaps with previous lesson boundary",
    "lesson-030: boundary is low_confidence",
    "lesson-031: start_page overlaps with previous lesson boundary",
    "lesson-031: boundary is low_confidence",
    "lesson-032: boundary is low_confidence",
    "lesson-033: start_page overlaps with previous lesson boundary",
    "lesson-033: boundary is low_confidence",
    "lesson-034: boundary is low_confidence",
    "lesson-035: boundary is low_confidence",
    "lesson-036: start_page overlaps with previous lesson boundary",
    "lesson-036: boundary is low_confidence",
    "lesson-037: boundary is low_confidence",
    "lesson-038: start_page overlaps with previous lesson boundary",
    "lesson-038: boundary is low_confidence",
    "lesson-039: start_page overlaps with previous lesson boundary",
    "lesson-039: boundary is low_confidence",
    "lesson-040: start_page overlaps with previous lesson boundary",
    "lesson-040: boundary is low_confidence"
  ],
  "entries": [
    {
      "lesson_id": "lesson-001",
      "sheet_name": "1차시",
      "resource_id": "main",
      "role": "textbook",
      "title_query": "[단원 도입] 우리 친구는 누구?",
      "start_page": 4,
      "end_page": 11,
      "evidence_pages": [
        4,
        6,
        62,
        66,
        72
      ],
      "status": "low_confidence",
      "confidence": 0.55,
      "reason": "Transitional heuristic: choose highest-ranked candidate and cut before next lesson candidate"
    },
    {
      "lesson_id": "lesson-002",
      "sheet_name": "2차시",
      "resource_id": "main",
      "role": "textbook",
      "title_query": "분단으로 나타난 문제점과 분단이 사회와 생활 에 끼친 영향 알아보기",
      "start_page": 12,
      "end_page": 15,
      "evidence_pages": [
        12,
        15,
        42,
        123,
        126
      ],
      "status": "low_confidence",
      "confidence": 0.55,
      "reason": "Transitional heuristic: choose highest-ranked candidate and cut before next lesson candidate"
    },
    {
      "lesson_id": "lesson-003",
      "sheet_name": "3차시",
      "resource_id": "main",
      "role": "textbook",
      "title_query": "분단의 흔적이 남아 있는 장소 알아보기",
      "start_page": 16,
      "end_page": 16,
      "evidence_pages": [
        16,
        18,
        20,
        21,
        27
      ],
      "status": "low_confidence",
      "confidence": 0.45,
      "reason": "Transitional heuristic: choose highest-ranked candidate and cut before next lesson candidate"
    },
    {
      "lesson_id": "lesson-004",
      "sheet_name": "4차시",
      "resource_id": "main",
      "role": "textbook",
      "title_query": "분단의 장소가 평화의 장소로 바뀐 사례 알아보기",
      "start_page": 12,
      "end_page": 12,
      "evidence_pages": [
        12,
        18,
        19,
        21,
        27
      ],
      "status": "low_confidence",
      "confidence": 0.45,
      "reason": "Transitional heuristic: choose highest-ranked candidate and cut before next lesson candidate"
    },
    {
      "lesson_id": "lesson-005",
      "sheet_name": "5-6차시",
      "resource_id": "main",
      "role": "textbook",
      "title_query": "평화 통일을 위한 노력 살펴보기",
      "start_page": 10,
      "end_page": 12,
      "evidence_pages": [
        10,
        12,
        28,
        51,
        157
      ],
      "status": "low_confidence",
      "confidence": 0.55,
      "reason": "Transitional heuristic: choose highest-ranked candidate and cut before next lesson candidate"
    },
    {
      "lesson_id": "lesson-006",
      "sheet_name": "7차시",
      "resource_id": "main",
      "role": "textbook",
      "title_query": "[주제 도입] 열려라 이야기 / 외쳐라 빙고",
      "start_page": 13,
      "end_page": 28,
      "evidence_pages": [
        13,
        55,
        71,
        91,
        111
      ],
      "status": "low_confidence",
      "confidence": 0.55,
      "reason": "Transitional heuristic: choose highest-ranked candidate and cut before next lesson candidate"
    },
    {
      "lesson_id": "lesson-007",
      "sheet_name": "8-9차시",
      "resource_id": "main",
      "role": "textbook",
      "title_query": "4·19 혁명 이해하기",
      "start_page": 29,
      "end_page": 29,
      "evidence_pages": [
        29,
        32,
        36,
        49
      ],
      "status": "low_confidence",
      "confidence": 0.45,
      "reason": "Transitional heuristic: choose highest-ranked candidate and cut before next lesson candidate"
    },
    {
      "lesson_id": "lesson-008",
      "sheet_name": "10차시",
      "resource_id": "main",
      "role": "textbook",
      "title_query": "대통령 직선제와 지방 자치제의 부활 이해하기",
      "start_page": 29,
      "end_page": 29,
      "evidence_pages": [
        29,
        30,
        31,
        38,
        49
      ],
      "status": "low_confidence",
      "confidence": 0.45,
      "reason": "Transitional heuristic: choose highest-ranked candidate and cut before next lesson candidate"
    },
    {
      "lesson_id": "lesson-009",
      "sheet_name": "11차시",
      "resource_id": "main",
      "role": "textbook",
      "title_query": "산업화 과정 이해하기",
      "start_page": 10,
      "end_page": 10,
      "evidence_pages": [
        10,
        28,
        40,
        45,
        51
      ],
      "status": "low_confidence",
      "confidence": 0.45,
      "reason": "Transitional heuristic: choose highest-ranked candidate and cut before next lesson candidate"
    },
    {
      "lesson_id": "lesson-010",
      "sheet_name": "12-13차시",
      "resource_id": "main",
      "role": "textbook",
      "title_query": "산업화로 달라진 사회와 생활 문화 이해하기",
      "start_page": 10,
      "end_page": 48,
      "evidence_pages": [
        10,
        28,
        42,
        46,
        156
      ],
      "status": "low_confidence",
      "confidence": 0.55,
      "reason": "Transitional heuristic: choose highest-ranked candidate and cut before next lesson candidate"
    },
    {
      "lesson_id": "lesson-011",
      "sheet_name": "14차시",
      "resource_id": "main",
      "role": "textbook",
      "title_query": "[단원 마무리] 나만의 누리집 완성하기 / 창의·융 합 사고력 쑥쑥",
      "start_page": 49,
      "end_page": 49,
      "evidence_pages": [
        49,
        50,
        105,
        152,
        178
      ],
      "status": "low_confidence",
      "confidence": 0.45,
      "reason": "Transitional heuristic: choose highest-ranked candidate and cut before next lesson candidate"
    },
    {
      "lesson_id": "lesson-012",
      "sheet_name": "1차시",
      "resource_id": "main",
      "role": "textbook",
      "title_query": "[단원 도입] 우리 친구는 누구?",
      "start_page": 4,
      "end_page": 53,
      "evidence_pages": [
        4,
        6,
        62,
        66,
        72
      ],
      "status": "low_confidence",
      "confidence": 0.55,
      "reason": "Transitional heuristic: choose highest-ranked candidate and cut before next lesson candidate"
    },
    {
      "lesson_id": "lesson-013",
      "sheet_name": "2차시",
      "resource_id": "main",
      "role": "textbook",
      "title_query": "선거의 의미와 중요성 파악하기",
      "start_page": 54,
      "end_page": 54,
      "evidence_pages": [
        54,
        62,
        63,
        172,
        180
      ],
      "status": "low_confidence",
      "confidence": 0.45,
      "reason": "Transitional heuristic: choose highest-ranked candidate and cut before next lesson candidate"
    },
    {
      "lesson_id": "lesson-014",
      "sheet_name": "3차시",
      "resource_id": "main",
      "role": "textbook",
      "title_query": "민주주의에서 선거의 역할 파악하기",
      "start_page": 54,
      "end_page": 54,
      "evidence_pages": [
        54,
        58,
        90,
        94,
        172
      ],
      "status": "low_confidence",
      "confidence": 0.45,
      "reason": "Transitional heuristic: choose highest-ranked candidate and cut before next lesson candidate"
    },
    {
      "lesson_id": "lesson-015",
      "sheet_name": "4-5차시",
      "resource_id": "main",
      "role": "textbook",
      "title_query": "우리나라의 선거 과정 살펴보기",
      "start_page": 54,
      "end_page": 54,
      "evidence_pages": [
        54,
        55,
        56,
        57,
        62
      ],
      "status": "low_confidence",
      "confidence": 0.45,
      "reason": "Transitional heuristic: choose highest-ranked candidate and cut before next lesson candidate"
    },
    {
      "lesson_id": "lesson-016",
      "sheet_name": "6-7차시",
      "resource_id": "main",
      "role": "textbook",
      "title_query": "선거에 적극적으로 참여해야 하는 까닭 알아보기",
      "start_page": 32,
      "end_page": 32,
      "evidence_pages": [
        32,
        54,
        64,
        82,
        104
      ],
      "status": "low_confidence",
      "confidence": 0.45,
      "reason": "Transitional heuristic: choose highest-ranked candidate and cut before next lesson candidate"
    },
    {
      "lesson_id": "lesson-017",
      "sheet_name": "8차시",
      "resource_id": "main",
      "role": "textbook",
      "title_query": "[주제 도입] 열려라 이야기 / 외쳐라 빙고",
      "start_page": 13,
      "end_page": 73,
      "evidence_pages": [
        13,
        55,
        71,
        91,
        111
      ],
      "status": "low_confidence",
      "confidence": 0.55,
      "reason": "Transitional heuristic: choose highest-ranked candidate and cut before next lesson candidate"
    },
    {
      "lesson_id": "lesson-018",
      "sheet_name": "9-10차시",
      "resource_id": "main",
      "role": "textbook",
      "title_query": "국회의 구성과 하는 일 파악하기",
      "start_page": 74,
      "end_page": 74,
      "evidence_pages": [
        74,
        80,
        81,
        82,
        87
      ],
      "status": "low_confidence",
      "confidence": 0.45,
      "reason": "Transitional heuristic: choose highest-ranked candidate and cut before next lesson candidate"
    },
    {
      "lesson_id": "lesson-019",
      "sheet_name": "11차시",
      "resource_id": "main",
      "role": "textbook",
      "title_query": "행정부의 구성과 하는 일 파악하기",
      "start_page": 74,
      "end_page": 74,
      "evidence_pages": [
        74,
        80,
        81,
        82,
        87
      ],
      "status": "low_confidence",
      "confidence": 0.45,
      "reason": "Transitional heuristic: choose highest-ranked candidate and cut before next lesson candidate"
    },
    {
      "lesson_id": "lesson-020",
      "sheet_name": "12차시",
      "resource_id": "main",
      "role": "textbook",
      "title_query": "법원의 구성과 하는 일 파악하기",
      "start_page": 73,
      "end_page": 73,
      "evidence_pages": [
        73,
        74,
        80,
        81,
        82
      ],
      "status": "low_confidence",
      "confidence": 0.45,
      "reason": "Transitional heuristic: choose highest-ranked candidate and cut before next lesson candidate"
    },
    {
      "lesson_id": "lesson-021",
      "sheet_name": "13차시",
      "resource_id": "main",
      "role": "textbook",
      "title_query": "권력 분립의 의미와 중요성 탐구하기",
      "start_page": 54,
      "end_page": 54,
      "evidence_pages": [
        54,
        71,
        86,
        87,
        90
      ],
      "status": "low_confidence",
      "confidence": 0.45,
      "reason": "Transitional heuristic: choose highest-ranked candidate and cut before next lesson candidate"
    },
    {
      "lesson_id": "lesson-022",
      "sheet_name": "14차시",
      "resource_id": "main",
      "role": "textbook",
      "title_query": "[주제 도입] 열려라 이야기 / 외쳐라 빙고",
      "start_page": 13,
      "end_page": 82,
      "evidence_pages": [
        13,
        55,
        71,
        91,
        111
      ],
      "status": "low_confidence",
      "confidence": 0.55,
      "reason": "Transitional heuristic: choose highest-ranked candidate and cut before next lesson candidate"
    },
    {
      "lesson_id": "lesson-023",
      "sheet_name": "15차시",
      "resource_id": "main",
      "role": "textbook",
      "title_query": "미디어의 정보 제공 역할 알아보기",
      "start_page": 83,
      "end_page": 89,
      "evidence_pages": [
        83,
        88,
        101,
        114,
        118
      ],
      "status": "low_confidence",
      "confidence": 0.55,
      "reason": "Transitional heuristic: choose highest-ranked candidate and cut before next lesson candidate"
    },
    {
      "lesson_id": "lesson-024",
      "sheet_name": "16차시",
      "resource_id": "main",
      "role": "textbook",
      "title_query": "미디어의 내용을 비판적으로 분석해야 하는 까 닭 알아보기",
      "start_page": 90,
      "end_page": 90,
      "evidence_pages": [
        90,
        100,
        101,
        102,
        170
      ],
      "status": "low_confidence",
      "confidence": 0.45,
      "reason": "Transitional heuristic: choose highest-ranked candidate and cut before next lesson candidate"
    },
    {
      "lesson_id": "lesson-025",
      "sheet_name": "17-18차시",
      "resource_id": "main",
      "role": "textbook",
      "title_query": "미디어를 올바르게 이용하는 방법 알아보기",
      "start_page": 7,
      "end_page": 48,
      "evidence_pages": [
        7,
        90,
        100,
        102,
        103
      ],
      "status": "low_confidence",
      "confidence": 0.55,
      "reason": "Transitional heuristic: choose highest-ranked candidate and cut before next lesson candidate"
    },
    {
      "lesson_id": "lesson-026",
      "sheet_name": "19차시",
      "resource_id": "main",
      "role": "textbook",
      "title_query": "[단원 마무리] 나만의 누리집 완성하기 / 창의·융 합 사고력 쑥쑥",
      "start_page": 49,
      "end_page": 49,
      "evidence_pages": [
        49,
        50,
        105,
        152,
        178
      ],
      "status": "low_confidence",
      "confidence": 0.45,
      "reason": "Transitional heuristic: choose highest-ranked candidate and cut before next lesson candidate"
    },
    {
      "lesson_id": "lesson-027",
      "sheet_name": "1차시",
      "resource_id": "main",
      "role": "textbook",
      "title_query": "[단원 도입] 우리 친구는 누구?",
      "start_page": 4,
      "end_page": 111,
      "evidence_pages": [
        4,
        6,
        62,
        66,
        72
      ],
      "status": "low_confidence",
      "confidence": 0.55,
      "reason": "Transitional heuristic: choose highest-ranked candidate and cut before next lesson candidate"
    },
    {
      "lesson_id": "lesson-028",
      "sheet_name": "2-3차시",
      "resource_id": "main",
      "role": "textbook",
      "title_query": "지구본의 특징 살펴보기",
      "start_page": 112,
      "end_page": 115,
      "evidence_pages": [
        112,
        114,
        132,
        150,
        151
      ],
      "status": "low_confidence",
      "confidence": 0.55,
      "reason": "Transitional heuristic: choose highest-ranked candidate and cut before next lesson candidate"
    },
    {
      "lesson_id": "lesson-029",
      "sheet_name": "4차시",
      "resource_id": "main",
      "role": "textbook",
      "title_query": "디지털 공간 영상 정보의 의미 알아보기",
      "start_page": 116,
      "end_page": 116,
      "evidence_pages": [
        116,
        118,
        119,
        150,
        151
      ],
      "status": "low_confidence",
      "confidence": 0.45,
      "reason": "Transitional heuristic: choose highest-ranked candidate and cut before next lesson candidate"
    },
    {
      "lesson_id": "lesson-030",
      "sheet_name": "5차시",
      "resource_id": "main",
      "role": "textbook",
      "title_query": "위도와 위선의 의미 알아보기",
      "start_page": 83,
      "end_page": 83,
      "evidence_pages": [
        83,
        88,
        110,
        128,
        129
      ],
      "status": "low_confidence",
      "confidence": 0.45,
      "reason": "Transitional heuristic: choose highest-ranked candidate and cut before next lesson candidate"
    },
    {
      "lesson_id": "lesson-031",
      "sheet_name": "6차시",
      "resource_id": "main",
      "role": "textbook",
      "title_query": "경도와 경선의 의미 알아보기",
      "start_page": 54,
      "end_page": 109,
      "evidence_pages": [
        54,
        83,
        88,
        114,
        118
      ],
      "status": "low_confidence",
      "confidence": 0.55,
      "reason": "Transitional heuristic: choose highest-ranked candidate and cut before next lesson candidate"
    },
    {
      "lesson_id": "lesson-032",
      "sheet_name": "7차시",
      "resource_id": "main",
      "role": "textbook",
      "title_query": "위도와 경도를 이용해 위치를 표현하는 방법 살 펴보기",
      "start_page": 110,
      "end_page": 110,
      "evidence_pages": [
        110,
        120,
        128,
        129,
        137
      ],
      "status": "low_confidence",
      "confidence": 0.45,
      "reason": "Transitional heuristic: choose highest-ranked candidate and cut before next lesson candidate"
    },
    {
      "lesson_id": "lesson-033",
      "sheet_name": "8차시",
      "resource_id": "main",
      "role": "textbook",
      "title_query": "[주제 도입] 열려라 이야기 / 외쳐라 빙고",
      "start_page": 13,
      "end_page": 127,
      "evidence_pages": [
        13,
        55,
        71,
        91,
        111
      ],
      "status": "low_confidence",
      "confidence": 0.55,
      "reason": "Transitional heuristic: choose highest-ranked candidate and cut before next lesson candidate"
    },
    {
      "lesson_id": "lesson-034",
      "sheet_name": "9차시",
      "resource_id": "main",
      "role": "textbook",
      "title_query": "우리나라의 위치 특징 파악하기",
      "start_page": 128,
      "end_page": 130,
      "evidence_pages": [
        128,
        131,
        132,
        137,
        151
      ],
      "status": "low_confidence",
      "confidence": 0.55,
      "reason": "Transitional heuristic: choose highest-ranked candidate and cut before next lesson candidate"
    },
    {
      "lesson_id": "lesson-035",
      "sheet_name": "10차시",
      "resource_id": "main",
      "role": "textbook",
      "title_query": "아시아 주요 나라들의 위치 알아보기",
      "start_page": 131,
      "end_page": 131,
      "evidence_pages": [
        131,
        132,
        133,
        145,
        147
      ],
      "status": "low_confidence",
      "confidence": 0.45,
      "reason": "Transitional heuristic: choose highest-ranked candidate and cut before next lesson candidate"
    },
    {
      "lesson_id": "lesson-036",
      "sheet_name": "11차시",
      "resource_id": "main",
      "role": "textbook",
      "title_query": "유럽 주요 나라들의 위치 알아보기",
      "start_page": 128,
      "end_page": 130,
      "evidence_pages": [
        128,
        131,
        132,
        145,
        147
      ],
      "status": "low_confidence",
      "confidence": 0.55,
      "reason": "Transitional heuristic: choose highest-ranked candidate and cut before next lesson candidate"
    },
    {
      "lesson_id": "lesson-037",
      "sheet_name": "12차시",
      "resource_id": "main",
      "role": "textbook",
      "title_query": "북아메리카와 남아메리카 주요 나라들의 위치 알아보기",
      "start_page": 131,
      "end_page": 131,
      "evidence_pages": [
        131,
        132,
        133,
        145,
        147
      ],
      "status": "low_confidence",
      "confidence": 0.45,
      "reason": "Transitional heuristic: choose highest-ranked candidate and cut before next lesson candidate"
    },
    {
      "lesson_id": "lesson-038",
      "sheet_name": "13차시",
      "resource_id": "main",
      "role": "textbook",
      "title_query": "아프리카 주요 나라들의 위치 알아보기",
      "start_page": 131,
      "end_page": 131,
      "evidence_pages": [
        131,
        132,
        133,
        145,
        147
      ],
      "status": "low_confidence",
      "confidence": 0.45,
      "reason": "Transitional heuristic: choose highest-ranked candidate and cut before next lesson candidate"
    },
    {
      "lesson_id": "lesson-039",
      "sheet_name": "14차시",
      "resource_id": "main",
      "role": "textbook",
      "title_query": "오세아니아 주요 나라들의 위치 알아보기",
      "start_page": 131,
      "end_page": 131,
      "evidence_pages": [
        131,
        132,
        133,
        145,
        147
      ],
      "status": "low_confidence",
      "confidence": 0.45,
      "reason": "Transitional heuristic: choose highest-ranked candidate and cut before next lesson candidate"
    },
    {
      "lesson_id": "lesson-040",
      "sheet_name": "15차시",
      "resource_id": "main",
      "role": "textbook",
      "title_query": "[단원 마무리] 나만의 누리집 완성하기 / 창의·융 합 사고력 쑥쑥",
      "start_page": 49,
      "end_page": 49,
      "evidence_pages": [
        49,
        50,
        105,
        152,
        178
      ],
      "status": "low_confidence",
      "confidence": 0.45,
      "reason": "Transitional heuristic: choose highest-ranked candidate and cut before next lesson candidate"
    }
  ]
}

Supplement review:
{
  "schema_version": "1.0.0",
  "stage": "review_source_supplement",
  "lesson_id": null,
  "status": "succeeded",
  "decision": "pass",
  "findings": [],
  "blocking_issues": [],
  "warnings": [],
  "entries": []
}

Schema:
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://numbersauto.local/schemas/review_result.schema.json",
  "title": "Review Result",
  "type": "object",
  "required": [
    "schema_version",
    "stage",
    "status",
    "decision",
    "findings",
    "blocking_issues",
    "warnings"
  ],
  "properties": {
    "schema_version": {
      "type": "string"
    },
    "stage": {
      "type": "string"
    },
    "lesson_id": {
      "type": ["string", "null"]
    },
    "status": {
      "type": "string",
      "enum": [
        "pending",
        "running",
        "succeeded",
        "succeeded_with_warning",
        "failed",
        "failed_fallback_used",
        "blocked"
      ]
    },
    "decision": {
      "type": "string",
      "enum": ["pass", "pass_with_warning", "needs_revision", "blocked"]
    },
    "findings": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["severity", "message", "evidence_refs"],
        "properties": {
          "severity": {
            "type": "string",
            "enum": ["info", "warning", "error"]
          },
          "message": {
            "type": "string"
          },
          "evidence_refs": {
            "type": "array",
            "items": {
              "type": "string"
            }
          }
        },
        "additionalProperties": false
      }
    },
    "blocking_issues": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "warnings": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  },
  "additionalProperties": false
}
