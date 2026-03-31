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
    "sheet_name": "1차시",
    "title": "1단원 도입 — [단원 도입] 우리 친구는 누구?",
    "sources": [
      {
        "resource_id": "main",
        "role": "textbook",
        "title_query": "1단원 도입 — [단원 도입] 우리 친구는 누구?",
        "end_before_query": null,
        "optional": false
      }
    ]
  },
  {
    "sheet_name": "2차시",
    "title": "평화 통일을 위한 노력 — 분단으로 나타난 문제점과 분단이 사회와 생활 에 끼친 영향 알아보기",
    "sources": [
      {
        "resource_id": "main",
        "role": "textbook",
        "title_query": "평화 통일을 위한 노력 — 분단으로 나타난 문제점과 분단이 사회와 생활 에 끼친 영향 알아보기",
        "end_before_query": null,
        "optional": false
      }
    ]
  },
  {
    "sheet_name": "3차시",
    "title": "평화 통일을 위한 노력 — 분단의 흔적이 남아 있는 장소 알아보기",
    "sources": [
      {
        "resource_id": "main",
        "role": "textbook",
        "title_query": "평화 통일을 위한 노력 — 분단의 흔적이 남아 있는 장소 알아보기",
        "end_before_query": null,
        "optional": false
      }
    ]
  },
  {
    "sheet_name": "4차시",
    "title": "평화 통일을 위한 노력 — 분단의 장소가 평화의 장소로 바뀐 사례 알아보기",
    "sources": [
      {
        "resource_id": "main",
        "role": "textbook",
        "title_query": "평화 통일을 위한 노력 — 분단의 장소가 평화의 장소로 바뀐 사례 알아보기",
        "end_before_query": null,
        "optional": false
      }
    ]
  },
  {
    "sheet_name": "5-6차시",
    "title": "평화 통일을 위한 노력 — 평화 통일을 위한 노력 살펴보기",
    "sources": [
      {
        "resource_id": "main",
        "role": "textbook",
        "title_query": "평화 통일을 위한 노력 — 평화 통일을 위한 노력 살펴보기",
        "end_before_query": null,
        "optional": false
      }
    ]
  },
  {
    "sheet_name": "7차시",
    "title": "민주화와 산업화로 달라진 생활 문화 — [주제 도입] 열려라 이야기 / 외쳐라 빙고",
    "sources": [
      {
        "resource_id": "main",
        "role": "textbook",
        "title_query": "민주화와 산업화로 달라진 생활 문화 — [주제 도입] 열려라 이야기 / 외쳐라 빙고",
        "end_before_query": null,
        "optional": false
      }
    ]
  }
]

Lookahead sections:
[
  {
    "sheet_name": "8-9차시",
    "title": "민주화와 산업화로 달라진 생활 문화 — 4·19 혁명 이해하기",
    "sources": [
      {
        "resource_id": "main",
        "role": "textbook",
        "title_query": "민주화와 산업화로 달라진 생활 문화 — 4·19 혁명 이해하기",
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
      "section_index": 0,
      "sheet_name": "1차시",
      "sources": [
        {
          "resource_id": "main",
          "role": "textbook",
          "query": "1단원 도입 — [단원 도입] 우리 친구는 누구?",
          "candidate_pages": [
            4,
            6,
            156
          ]
        }
      ]
    },
    {
      "section_index": 1,
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
      "section_index": 2,
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
      "section_index": 3,
      "sheet_name": "4차시",
      "sources": [
        {
          "resource_id": "main",
          "role": "textbook",
          "query": "평화 통일을 위한 노력 — 분단의 장소가 평화의 장소로 바뀐 사례 알아보기",
          "candidate_pages": [
            18,
            19,
            27
          ]
        }
      ]
    },
    {
      "section_index": 4,
      "sheet_name": "5-6차시",
      "sources": [
        {
          "resource_id": "main",
          "role": "textbook",
          "query": "평화 통일을 위한 노력 — 평화 통일을 위한 노력 살펴보기",
          "candidate_pages": [
            4,
            6,
            10
          ]
        }
      ]
    },
    {
      "section_index": 5,
      "sheet_name": "7차시",
      "sources": [
        {
          "resource_id": "main",
          "role": "textbook",
          "query": "민주화와 산업화로 달라진 생활 문화 — [주제 도입] 열려라 이야기 / 외쳐라 빙고",
          "candidate_pages": [
            4,
            10,
            28
          ]
        }
      ]
    },
    {
      "section_index": 6,
      "sheet_name": "8-9차시",
      "sources": [
        {
          "resource_id": "main",
          "role": "textbook",
          "query": "민주화와 산업화로 달라진 생활 문화 — 4·19 혁명 이해하기",
          "candidate_pages": [
            4,
            29,
            35
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
      "selected_page_count": 13,
      "pages": [
        {
          "page": 4,
          "excerpt": "안녕, 친구들! 나는 ‘우리’야. 너희들은 ‘사회’라는 단어를 들으면 어떤 모습이 떠오르니? ‘사회’는 우리가 살아가는 일상 속에서 일어나는 여러 사건과 현상을 이해하고, 더 나은 세상을 만들어 가는 데 중요한 역할을 하는 과목이야. 교과서를 펼칠 준"
        },
        {
          "page": 6,
          "excerpt": "우 리 가 들 려 주 는 사 회 이 야 기 우 사이 들 리 우리나라에서는 18세 이상 대한민국 국민이라면 누구나 자유롭게 투표에 참여할 수 있지만, 투표에 참여하지 않는 사람들도 있다. 반면에 벨기에, 오스트레일리아, 볼리비아 등 일부 나라에서는 의무"
        },
        {
          "page": 10,
          "excerpt": "1 평화 통일을 위한 노력 1 민주화와 산업화로 달라진 생활 문화 2 분 단 평화 통 일 민 주화 산업 화 평화 통일을 위한 노력, 민주화와 산업화 애니메이션"
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
          "page": 18,
          "excerpt": "새롭게 태어난 평화의 장소 한반도 곳곳에는 분단의 상징이었던 장소가 평화의 장소로 다시 바뀐 곳 들이 많다. 사람들은 분단의 장소에 평화 생태 공원을 만들고, 그곳에서 평화를 기원하는 예술제를 열기도 한다. 또한 평화의 길을 만들고, 그곳을 역사와 문"
        },
        {
          "page": 19,
          "excerpt": "분단의 상징이었던 곳 이 평화의 장소로 바뀐 사례를 더 찾아봅시다. 스스로 해 보기 곳곳에 나 있는 평화 누리길을 둘러보자. 임진강 독개다리(경기도 파주시) 6·25 전쟁 당시 폭격으로 파괴된 교각 을 활용해 전쟁 전 철교의 모습을 복원한 다리이다. "
        },
        {
          "page": 27,
          "excerpt": "옳은 설명을 들고 있는 남북 단일팀 선수를 모두 찾아 공을 전달해 골을 넣어 봅시다. 이번 주제에서 배운 내용을 정리하며 우리가 행복이를 만날 수 있는 길을 찾아봅시다. 1 한반도에서는 전쟁의 위협이 사라졌다. 4 한반도에는 분단의 흔적이 남아 있지 "
        },
        {
          "page": 28,
          "excerpt": "2 민주화와 산업화로 달라진 생활 문화 민주화를 이루려는 다양한 분야 사람들의 노력을 설명할 수 있어요. 우리나라 산업화의 성과와 한계를 파악할 수 있어요. 민주화와 산업화로 달라진 사람들의 생활 모습과 문화를 이해할 수 있어요. 이 주제를 배우면 나"
        },
        {
          "page": 29,
          "excerpt": "민주화 산업화 생활 문화 4.19 혁명 5.18 민주화 운동 6월 민주 항쟁 지방 자치제 시민 의식 중화학 공업 생태환경 경제성장 시민운동 직선제 독재 경공업 1 낱말 구름을 보고, 이 주제에서 배울 내용이 무엇인지 생각해 봅시다. 2 낱말 구름에 있"
        },
        {
          "page": 35,
          "excerpt": "비판적 사고력정보 활용 능력 1 \u0007위 자료를 살펴보고 궁금한 점과 알게 된 점을 이야기해 봅시다. 2 \u0007인터넷을 이용해 민주화 운동에 참여한 사람들의 이야기와 기록을 조사한 후, 활동 자료3 에 정리해 봅시다. “1987년 6월 10일, 명동 거리에서"
        },
        {
          "page": 156,
          "excerpt": "한 문장 정리 13쪽 문화 15쪽 분단 19쪽 평화 23쪽 교류 29쪽 자유, 권리 33쪽 민주주의 37쪽 시민 단체 40쪽 노동자 46쪽 성장 57쪽 선거 59쪽 선출 63쪽 직접, 비밀 67쪽 적극적 73쪽 국회, 행정부, 법원 76쪽 법 81쪽 "
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
