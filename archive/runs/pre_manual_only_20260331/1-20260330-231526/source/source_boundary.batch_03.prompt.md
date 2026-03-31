# Runtime Agent Spec: source_boundary_agent

아래 AGENT.md는 이 단계의 역할과 경계를 정의한다.
문서에 적힌 역할만 수행하고, 하지 말아야 할 일은 넘지 마라.
출력 형식 요구가 있으면 반드시 지켜라.

# source_boundary_agent

## 역할
- 입력 config를 기준으로 차시별 source boundary를 확정한다.
- PDF 페이지 발췌문을 읽고 Agent 자율 판단으로 시작/종료 페이지를 추론한다.
- 실행에 필요한 source 산출물만 생성한다.

구현:
- `scripts/source_boundary_agent.py`

## 입력
- `configs/<config>.json`
- 필요 시 진도표 원본 경로

## 출력
- `source/resource_page_catalog.json`
- `source/source_boundary.ai.json`
- `source/schedule_draft.json`
- `source/textbook_context.json`
- `source/runtime_config.json`
- `source/source_boundary.status.json`

## 하지 말아야 할 일
- source 품질 검토를 하지 않는다.
- deterministic regex 규칙으로 boundary를 고정하지 않는다.
- lesson/activity 생성을 하지 않는다.


# Execution Task

너의 역할은 교과서 파싱의 source boundary를 자율적으로 결정하는 agent다.
규칙 기반 문자열 매칭을 흉내 내지 말고, 후보 페이지 발췌문의 맥락을 보고 차시 시작과 끝을 추론하라.
후보 페이지는 로컬 preselection 결과다. 반드시 candidate_pages 안에서 시작 근거를 찾고, 필요하면 인접 페이지를 포함해 연속 구간을 확정하라.
각 source는 연속된 페이지 구간 하나만 반환하라.
필수 source는 matched 또는 not_found여야 한다. optional source만 optional_not_found를 허용한다.
다음 차시나 다음 주제 도입이 시작되기 전까지만 포함하라.
반드시 Target sections에 대해서만 boundaries를 반환하라. Lookahead sections는 끝 경계를 판단하기 위한 참고 정보다.
출력은 JSON object 하나만 반환하라.

Target sections:
[
  {
    "sheet_name": "2차시",
    "title": "민주주의와 선거 — 선거의 의미와 중요성 파악하기",
    "sources": [
      {
        "resource_id": "main",
        "role": "textbook",
        "title_query": "민주주의와 선거 — 선거의 의미와 중요성 파악하기",
        "end_before_query": null,
        "optional": false
      }
    ]
  },
  {
    "sheet_name": "3차시",
    "title": "민주주의와 선거 — 민주주의에서 선거의 역할 파악하기",
    "sources": [
      {
        "resource_id": "main",
        "role": "textbook",
        "title_query": "민주주의와 선거 — 민주주의에서 선거의 역할 파악하기",
        "end_before_query": null,
        "optional": false
      }
    ]
  },
  {
    "sheet_name": "4-5차시",
    "title": "민주주의와 선거 — 우리나라의 선거 과정 살펴보기",
    "sources": [
      {
        "resource_id": "main",
        "role": "textbook",
        "title_query": "민주주의와 선거 — 우리나라의 선거 과정 살펴보기",
        "end_before_query": null,
        "optional": false
      }
    ]
  },
  {
    "sheet_name": "6-7차시",
    "title": "민주주의와 선거 — 선거에 적극적으로 참여해야 하는 까닭 알아보기",
    "sources": [
      {
        "resource_id": "main",
        "role": "textbook",
        "title_query": "민주주의와 선거 — 선거에 적극적으로 참여해야 하는 까닭 알아보기",
        "end_before_query": null,
        "optional": false
      }
    ]
  },
  {
    "sheet_name": "8차시",
    "title": "국가기관이 하는 일 — [주제 도입] 열려라 이야기 / 외쳐라 빙고",
    "sources": [
      {
        "resource_id": "main",
        "role": "textbook",
        "title_query": "국가기관이 하는 일 — [주제 도입] 열려라 이야기 / 외쳐라 빙고",
        "end_before_query": null,
        "optional": false
      }
    ]
  },
  {
    "sheet_name": "9-10차시",
    "title": "국가기관이 하는 일 — 국회의 구성과 하는 일 파악하기",
    "sources": [
      {
        "resource_id": "main",
        "role": "textbook",
        "title_query": "국가기관이 하는 일 — 국회의 구성과 하는 일 파악하기",
        "end_before_query": null,
        "optional": false
      }
    ]
  }
]

Lookahead sections:
[
  {
    "sheet_name": "11차시",
    "title": "국가기관이 하는 일 — 행정부의 구성과 하는 일 파악하기",
    "sources": [
      {
        "resource_id": "main",
        "role": "textbook",
        "title_query": "국가기관이 하는 일 — 행정부의 구성과 하는 일 파악하기",
        "end_before_query": null,
        "optional": false
      }
    ]
  }
]

Candidate catalog:
{
  "schema_version": "1.0.0",
  "strategy": "query_token_preselection",
  "section_candidates": [
    {
      "sheet_name": "2차시",
      "sources": [
        {
          "resource_id": "main",
          "role": "textbook",
          "query": "평화 통일을 위한 노력 — 분단으로 나타난 문제점과 분단이 사회와 생활 에 끼친 영향 알아보기",
          "candidate_pages": [
            4,
            12,
            27
          ]
        }
      ]
    },
    {
      "sheet_name": "3차시",
      "sources": [
        {
          "resource_id": "main",
          "role": "textbook",
          "query": "평화 통일을 위한 노력 — 분단의 흔적이 남아 있는 장소 알아보기",
          "candidate_pages": [
            16,
            17,
            27
          ]
        }
      ]
    },
    {
      "sheet_name": "11차시",
      "sources": [
        {
          "resource_id": "main",
          "role": "textbook",
          "query": "민주화와 산업화로 달라진 생활 문화 — 산업화 과정 이해하기",
          "candidate_pages": [
            33,
            41,
            47
          ]
        }
      ]
    },
    {
      "sheet_name": "2차시",
      "sources": [
        {
          "resource_id": "main",
          "role": "textbook",
          "query": "민주주의와 선거 — 선거의 의미와 중요성 파악하기",
          "candidate_pages": [
            54,
            59,
            69
          ]
        }
      ]
    },
    {
      "sheet_name": "3차시",
      "sources": [
        {
          "resource_id": "main",
          "role": "textbook",
          "query": "민주주의와 선거 — 민주주의에서 선거의 역할 파악하기",
          "candidate_pages": [
            54,
            59,
            69
          ]
        }
      ]
    },
    {
      "sheet_name": "4-5차시",
      "sources": [
        {
          "resource_id": "main",
          "role": "textbook",
          "query": "민주주의와 선거 — 우리나라의 선거 과정 살펴보기",
          "candidate_pages": [
            5,
            54,
            57
          ]
        }
      ]
    },
    {
      "sheet_name": "6-7차시",
      "sources": [
        {
          "resource_id": "main",
          "role": "textbook",
          "query": "민주주의와 선거 — 선거에 적극적으로 참여해야 하는 까닭 알아보기",
          "candidate_pages": [
            5,
            64,
            69
          ]
        }
      ]
    },
    {
      "sheet_name": "8차시",
      "sources": [
        {
          "resource_id": "main",
          "role": "textbook",
          "query": "국가기관이 하는 일 — [주제 도입] 열려라 이야기 / 외쳐라 빙고",
          "candidate_pages": [
            52,
            70,
            71
          ]
        }
      ]
    },
    {
      "sheet_name": "9-10차시",
      "sources": [
        {
          "resource_id": "main",
          "role": "textbook",
          "query": "국가기관이 하는 일 — 국회의 구성과 하는 일 파악하기",
          "candidate_pages": [
            52,
            70,
            75
          ]
        }
      ]
    },
    {
      "sheet_name": "11차시",
      "sources": [
        {
          "resource_id": "main",
          "role": "textbook",
          "query": "국가기관이 하는 일 — 행정부의 구성과 하는 일 파악하기",
          "candidate_pages": [
            52,
            70,
            89
          ]
        }
      ]
    },
    {
      "sheet_name": "8차시",
      "sources": [
        {
          "resource_id": "main",
          "role": "textbook",
          "query": "세계의 대륙, 대양, 나라 — [주제 도입] 열려라 이야기 / 외쳐라 빙고",
          "candidate_pages": [
            108,
            132,
            133
          ]
        }
      ]
    },
    {
      "sheet_name": "11차시",
      "sources": [
        {
          "resource_id": "main",
          "role": "textbook",
          "query": "세계의 대륙, 대양, 나라 — 유럽 주요 나라들의 위치 알아보기",
          "candidate_pages": [
            139,
            141,
            143
          ]
        }
      ]
    }
  ],
  "resources": [
    {
      "resource_id": "main",
      "label": "교과서",
      "kind": "textbook",
      "page_count": 180,
      "selected_page_count": 25,
      "pages": [
        {
          "page": 4,
          "excerpt": "안녕, 친구들! 나는 ‘우리’야. 너희들은 ‘사회’라는 단어를 들으면 어떤 모습이 떠오르니? ‘사회’는 우리가 살아가는 일상 속에서 일어나는 여러 사건과 현상을 이해하고, 더 나은 세상을 만들어 가는 데 중요한 역할을 하는 과목이야. 교과서를 펼칠 준"
        },
        {
          "page": 5,
          "excerpt": "본문 주요 개념을 생활 속 다양한 장면이 담긴 사진과 그림으로 제시해 더 쉽게 이해할 수 있을 거야. 스스로 / 함께해 보기 혼자 또는 친구들과 함께하는 다양한 활동과 탐구 를 통해 사회 과목의 역량을 키워 갈 수 있어. 우리봇이 알려 주는 사회 궁금"
        },
        {
          "page": 12,
          "excerpt": "1 평화 통일을 위한 노력 분단으로 생겨난 문제점과 평화 통일의 필요성을 설명할 수 있어요. 분단과 관련된 장소를 평화의 장소로 만들려는 노력을 찾아볼 수 있어요. 평화 통일을 위해 우리가 할 수 있는 일을 탐색할 수 있어요. 이 주제를 배우면 나는 "
        },
        {
          "page": 16,
          "excerpt": "기찻길이 왜 끊어졌을까? 철원 왜 북한 군인들과 우리 헌병들이 마주 보고 있을까? 분단의 흔적이 남아 있는 장소를 찾아볼까요? 둘 비무장 지대(DMZ) 국제 조약 이나 협약에 따라 무장이 금지된 지역. 군사 분계선 에서 남북으로 2 km 지점에 해당함"
        },
        {
          "page": 17,
          "excerpt": "중단점은 무슨 뜻일까? 14~15쪽 분단의 흔적을 살펴보면서 질문에 답해 봅시다. 스스로 해 보기 연천 비무장 지대에는 가까운 거리에 남쪽의 대성동 마을과 북쪽의 기정동 마을이 마주 보고 있어. 두 마을에 대해 알고 나니 어떤 생각이 드니? 개성 우리"
        },
        {
          "page": 27,
          "excerpt": "옳은 설명을 들고 있는 남북 단일팀 선수를 모두 찾아 공을 전달해 골을 넣어 봅시다. 이번 주제에서 배운 내용을 정리하며 우리가 행복이를 만날 수 있는 길을 찾아봅시다. 1 한반도에서는 전쟁의 위협이 사라졌다. 4 한반도에는 분단의 흔적이 남아 있지 "
        },
        {
          "page": 33,
          "excerpt": "5·18 민주화 운동 18년간 대통령의 자리에 있던 박정희 대통령이 부하에게 죽임을 당한 후, 전두환을 중심으로 한 군인들이 정변을 일으켜 권력을 잡았다. 이에 학생과 시민들은 민주주의를 되찾기 위해 거리로 나서 시위를 벌였다. 광주에서도 시위가 일어"
        },
        {
          "page": 41,
          "excerpt": "2000년대 이후 우리나라는 1996년 경제협력개발기구 (OECD)에 가입하는 등 1990년대에도 경제가 꾸준히 성장했다. 그러나 일부 대기업들이 무리 하게 사업을 확장하고, 국가도 경제를 제대로 관리하지 못해 수출이 어려워졌다. 결국 외환 (달러)이"
        },
        {
          "page": 47,
          "excerpt": "옳은 설명이 적힌 창문 번호를 빈칸에 순서대로 써서 비밀번호를 찾아봅시다. 이번 주제에서 배운 내용을 정리하며 우리가 행복이를 만날 수 있는 길을 찾아봅시다. 주제마무리 독재 정치에 저항해 민주화 운동이 일어났다. 5·18 민주화 운동 당시 시민군을 "
        },
        {
          "page": 52,
          "excerpt": "2 민주주의와 선거 1 국가기관이 하는 일 2 민주주의와 미디어 3 민 주주 의 선 거 국 가기 관 권 력 분립 미 디어 민주주의와 시민 참여 애니메이션"
        },
        {
          "page": 54,
          "excerpt": "사람들이 몸으로 만든 저 모양은 무엇을 의미하는 걸까? 민주주의에서 선거의 의미와 역할 및 중요성을 파악할 수 있어요. 민주 국가의 선거 과정과 선거 원칙을 파악할 수 있어요. 선거에 주체적으로 참여하는 태도를 지닐 수 있어요. 이 주제를 배우면 나는"
        },
        {
          "page": 57,
          "excerpt": "창의적 사고력 공동체를 위해 일할 대표를 선출하는 과정을 ㅅ ㄱ (이)라고 한다. 한 문장 정리 민주주의 국가에서 국가의 중요한 일은 국민의 뜻에 따라 결정된다. 선거 는 국민이 직접 주권을 행사하는 대표적인 방법으로, 민주주의에서 가장 기본적이고 중"
        },
        {
          "page": 59,
          "excerpt": "선거로 선출된 대표자는 구성원들의 뜻을 반영한 공약을 실천한다. 만약 대표자의 능력이 부족하거나 역할을 제대로 수행하지 못해 사람들의 지지를 받지 못하면, 다음 선거에서 대표자로 선출되기 어려울 수 있다. 이처럼 민주 주의에서 선거는 선출된 대표자의 "
        },
        {
          "page": 64,
          "excerpt": "비판적 사고력 문제 해결력 및 의사 결정력 선거에 참여하는 바람직한 태도는 무엇일까요? 넷 민주 시민으로서 주권을 행사하려면 선거에 적극적으로 참여하는 것이 매우 중요하다. 선거에 관심이 부족하거나 참여하는 사람이 적으면 시민 들의 의견을 충분히 반영"
        },
        {
          "page": 69,
          "excerpt": "문제를 풀면서 투표소로 가는 길을 그려 봅시다. 공동체를 위해 일할 대표를 선출하는 과정을 투표라고 한다. 선거는 국민이 주권을 직접 행사하는 정치 참여 활동이다. 선거로 선출된 대표자는 공동체를 대표해 일할 자격을 얻는다. 선거는 대표자의 권력을 견"
        },
        {
          "page": 70,
          "excerpt": "국회 의사당 천장에는 왜 365개의 전등이 달려 있을까? 민주 국가의 국가기관을 파악할 수 있어요. 민주 국가에서 국회, 행정부, 법원이 하는 일을 설명할 수 있어요. 국가기관이 권력을 나누어 갖는 까닭을 탐색할 수 있어요. 이 주제를 배우면 나는 국"
        },
        {
          "page": 71,
          "excerpt": "1 낱말 구름을 보고, 이 주제에서 배울 내용이 무엇인지 생각해 봅시다. 2 낱말 구름에 있는 낱말 9개를 골라서 빙고 놀이를 해 봅시다. 정의의 여신은 왜 저울과 책을 들고 있을까? 2 국회 행정부 법원국가기관 국무 회의 시민 대통령 국정 감사 재판"
        },
        {
          "page": 75,
          "excerpt": "국회에서 법을 만드는 과정 국회가 만든 「학교 급식법」이 어린이들의 생활에 어떤 영향을 줄지 이야기해 봅시다. 스스로 해 보기 1 ‌\u0007새로운 법을 요구하는 국민이 많아 진다. 최근 학교 급식과 관련된 새로운 법을 요구하는 사람들이 많아졌습니다. 3 ‌"
        },
        {
          "page": 89,
          "excerpt": "아래 게시판의 문제를 풀어 누리가 체험 학습을 갈 장소를 찾아봅시다. 이번 주제에서 배운 내용을 정리하며 우리가 행복이를 만날 수 있는 길을 찾아봅시다. 주제마무리 되돌아가기를 만나면 교과서를 살펴본 후 처음부터 시작합니다. 72~73쪽 74~85쪽 "
        },
        {
          "page": 108,
          "excerpt": "3 지구본과 지도로 보는 세계 1 세계의 대륙, 대양, 나라 2 지 구본 세계 지 도 디 지털 공 간 영 상 정 보 대륙 대 양 지구, 대륙 그리고 국가들 애니메이션"
        },
        {
          "page": 132,
          "excerpt": "2 세계의 대륙, 대양, 나라 세계의 주요 대륙과 대양의 위치를 설명할 수 있어요. 우리나라의 위치와 영토 특징을 설명할 수 있어요. 세계 여러 나라의 위치와 영토 특징을 설명할 수 있어요. 이 주제를 배우면 나는 거꾸로 된 세계지도를 왜 만들었을까?"
        },
        {
          "page": 133,
          "excerpt": "0 200km 이 나라의 영토 모양을 보면 무엇이 떠오르니? 2 1 낱말 구름을 보고, 이 주제에서 배울 내용이 무엇인지 생각해 봅시다. 2 낱말 구름에 있는 낱말 9개를 골라서 빙고 놀이를 해 봅시다. 대륙 대양 위치 영토 태평양 대서양 인도양 북극"
        },
        {
          "page": 139,
          "excerpt": "아시아는 세계에서 가장 큰 대륙이다. 아시아에는 40여 개의 나라들이 있으며, 대부분의 나라가 북반구에 있다. 우리나라를 비롯해 중국, 일본, 베트남, 인도, 사우디아라비아 등 다양한 나라들이 아시아에 속한다. 2 \u0007다음과 같은 영토 특징을 지닌 나라"
        },
        {
          "page": 141,
          "excerpt": "유럽은 아시아의 서쪽에 있는 대륙이다. 다른 대륙보다 면적은 좁은 편 이지만, 40여 개의 나라가 있다. 프랑스, 영국, 독일 등 유럽의 여러 나라들은 일찍부터 산업과 문화가 발달했다. ㅍ ㄹ ㅅ , 영국, 독일 등 유럽의 여러 나라들은 일찍부터 산업"
        },
        {
          "page": 143,
          "excerpt": "북아메리카는 북반구에 있는 대륙이다. 캐나다, 미국, 멕시코가 북아메리카 면적 의 대부분을 차지하며, 쿠바, 자메이카, 온두라스, 파나마 등의 나라도 있다. 남아메리카는 북아메리카의 남쪽에 있는 대륙이다. 대부분의 나라가 남반구에 속하며, 브라질, 에"
        }
      ]
    }
  ]
}

Schema:
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://numbersauto.local/schemas/source_boundary_inference.schema.json",
  "title": "Source Boundary Inference",
  "type": "object",
  "required": ["schema_version", "boundaries"],
  "properties": {
    "schema_version": {
      "type": "string"
    },
    "boundaries": {
      "type": "array",
      "items": {
        "type": "object",
        "required": [
          "sheet_name",
          "resource_id",
          "role",
          "status",
          "start_page",
          "end_page",
          "reason"
        ],
        "properties": {
          "sheet_name": {
            "type": "string"
          },
          "resource_id": {
            "type": "string"
          },
          "role": {
            "type": "string"
          },
          "status": {
            "type": "string",
            "enum": ["matched", "optional_not_found", "not_found"]
          },
          "start_page": {
            "type": ["integer", "null"],
            "minimum": 1
          },
          "end_page": {
            "type": ["integer", "null"],
            "minimum": 1
          },
          "reason": {
            "type": "string"
          },
          "confidence": {
            "type": "number"
          },
          "evidence_pages": {
            "type": "array",
            "items": {
              "type": "integer",
              "minimum": 1
            }
          }
        },
        "additionalProperties": false
      }
    }
  },
  "additionalProperties": false
}
