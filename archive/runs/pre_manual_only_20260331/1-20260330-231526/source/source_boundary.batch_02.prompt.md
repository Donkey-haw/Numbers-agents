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
  },
  {
    "sheet_name": "10차시",
    "title": "민주화와 산업화로 달라진 생활 문화 — 대통령 직선제와 지방 자치제의 부활 이해하기",
    "sources": [
      {
        "resource_id": "main",
        "role": "textbook",
        "title_query": "민주화와 산업화로 달라진 생활 문화 — 대통령 직선제와 지방 자치제의 부활 이해하기",
        "end_before_query": null,
        "optional": false
      }
    ]
  },
  {
    "sheet_name": "11차시",
    "title": "민주화와 산업화로 달라진 생활 문화 — 산업화 과정 이해하기",
    "sources": [
      {
        "resource_id": "main",
        "role": "textbook",
        "title_query": "민주화와 산업화로 달라진 생활 문화 — 산업화 과정 이해하기",
        "end_before_query": null,
        "optional": false
      }
    ]
  },
  {
    "sheet_name": "12-13차시",
    "title": "민주화와 산업화로 달라진 생활 문화 — 산업화로 달라진 사회와 생활 문화 이해하기",
    "sources": [
      {
        "resource_id": "main",
        "role": "textbook",
        "title_query": "민주화와 산업화로 달라진 생활 문화 — 산업화로 달라진 사회와 생활 문화 이해하기",
        "end_before_query": null,
        "optional": false
      }
    ]
  },
  {
    "sheet_name": "14차시",
    "title": "1단원 정리 — [단원 마무리] 나만의 누리집 완성하기 / 창의·융 합 사고력 쑥쑥",
    "sources": [
      {
        "resource_id": "main",
        "role": "textbook",
        "title_query": "1단원 정리 — [단원 마무리] 나만의 누리집 완성하기 / 창의·융 합 사고력 쑥쑥",
        "end_before_query": null,
        "optional": false
      }
    ]
  },
  {
    "sheet_name": "1차시",
    "title": "2단원 도입 — [단원 도입] 우리 친구는 누구?",
    "sources": [
      {
        "resource_id": "main",
        "role": "textbook",
        "title_query": "2단원 도입 — [단원 도입] 우리 친구는 누구?",
        "end_before_query": null,
        "optional": false
      }
    ]
  }
]

Lookahead sections:
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
  }
]

Candidate catalog:
{
  "schema_version": "1.0.0",
  "strategy": "query_token_preselection",
  "section_candidates": [
    {
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
    },
    {
      "sheet_name": "10차시",
      "sources": [
        {
          "resource_id": "main",
          "role": "textbook",
          "query": "민주화와 산업화로 달라진 생활 문화 — 대통령 직선제와 지방 자치제의 부활 이해하기",
          "candidate_pages": [
            31,
            33,
            41
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
      "sheet_name": "12-13차시",
      "sources": [
        {
          "resource_id": "main",
          "role": "textbook",
          "query": "민주화와 산업화로 달라진 생활 문화 — 산업화로 달라진 사회와 생활 문화 이해하기",
          "candidate_pages": [
            4,
            10,
            42
          ]
        }
      ]
    },
    {
      "sheet_name": "14차시",
      "sources": [
        {
          "resource_id": "main",
          "role": "textbook",
          "query": "1단원 정리 — [단원 마무리] 나만의 누리집 완성하기 / 창의·융 합 사고력 쑥쑥",
          "candidate_pages": [
            7,
            49,
            105
          ]
        }
      ]
    },
    {
      "sheet_name": "1차시",
      "sources": [
        {
          "resource_id": "main",
          "role": "textbook",
          "query": "2단원 도입 — [단원 도입] 우리 친구는 누구?",
          "candidate_pages": [
            4,
            6,
            156
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
      "sheet_name": "14차시",
      "sources": [
        {
          "resource_id": "main",
          "role": "textbook",
          "query": "민주주의와 미디어 — [주제 도입] 열려라 이야기 / 외쳐라 빙고",
          "candidate_pages": [
            7,
            52,
            90
          ]
        }
      ]
    },
    {
      "sheet_name": "1차시",
      "sources": [
        {
          "resource_id": "main",
          "role": "textbook",
          "query": "3단원 도입 — [단원 도입] 우리 친구는 누구?",
          "candidate_pages": [
            4,
            6,
            156
          ]
        }
      ]
    },
    {
      "sheet_name": "10차시",
      "sources": [
        {
          "resource_id": "main",
          "role": "textbook",
          "query": "세계의 대륙, 대양, 나라 — 아시아 주요 나라들의 위치 알아보기",
          "candidate_pages": [
            139,
            141,
            145
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
    },
    {
      "sheet_name": "14차시",
      "sources": [
        {
          "resource_id": "main",
          "role": "textbook",
          "query": "세계의 대륙, 대양, 나라 — 오세아니아 주요 나라들의 위치 알아보기",
          "candidate_pages": [
            139,
            141,
            147
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
      "selected_page_count": 28,
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
          "page": 7,
          "excerpt": "다음 내용이 옳으면 ◯표를, 틀리면 ×표를 선택해 오늘의 점심 식단을 찾아봅시다. 미디어를 올바르게 이용하려는 노력은 국가만 하면 된다. 미디어에서는 잘못된 정보가 무분별하게 퍼지기도 한다. 미디어의 내용은 비판적으로 받아들여야 한다. 미디어의 정보는"
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
          "page": 27,
          "excerpt": "옳은 설명을 들고 있는 남북 단일팀 선수를 모두 찾아 공을 전달해 골을 넣어 봅시다. 이번 주제에서 배운 내용을 정리하며 우리가 행복이를 만날 수 있는 길을 찾아봅시다. 1 한반도에서는 전쟁의 위협이 사라졌다. 4 한반도에는 분단의 흔적이 남아 있지 "
        },
        {
          "page": 29,
          "excerpt": "민주화 산업화 생활 문화 4.19 혁명 5.18 민주화 운동 6월 민주 항쟁 지방 자치제 시민 의식 중화학 공업 생태환경 경제성장 시민운동 직선제 독재 경공업 1 낱말 구름을 보고, 이 주제에서 배울 내용이 무엇인지 생각해 봅시다. 2 낱말 구름에 있"
        },
        {
          "page": 31,
          "excerpt": "박정희 대통령과 전두환 대통령은 군인 신분으로 군대를 동원해 권력을 잡았다. 유신 헌법이 공포된 이후엔 국민들이 직접 투표로 대통령을 선출할 수 없었고, 정부는 방송과 신문에서 독재 정치를 비판하는 기사가 나가지 못하 도록 막았다. 이에 학생과 시민들"
        },
        {
          "page": 33,
          "excerpt": "5·18 민주화 운동 18년간 대통령의 자리에 있던 박정희 대통령이 부하에게 죽임을 당한 후, 전두환을 중심으로 한 군인들이 정변을 일으켜 권력을 잡았다. 이에 학생과 시민들은 민주주의를 되찾기 위해 거리로 나서 시위를 벌였다. 광주에서도 시위가 일어"
        },
        {
          "page": 35,
          "excerpt": "비판적 사고력정보 활용 능력 1 \u0007위 자료를 살펴보고 궁금한 점과 알게 된 점을 이야기해 봅시다. 2 \u0007인터넷을 이용해 민주화 운동에 참여한 사람들의 이야기와 기록을 조사한 후, 활동 자료3 에 정리해 봅시다. “1987년 6월 10일, 명동 거리에서"
        },
        {
          "page": 41,
          "excerpt": "2000년대 이후 우리나라는 1996년 경제협력개발기구 (OECD)에 가입하는 등 1990년대에도 경제가 꾸준히 성장했다. 그러나 일부 대기업들이 무리 하게 사업을 확장하고, 국가도 경제를 제대로 관리하지 못해 수출이 어려워졌다. 결국 외환 (달러)이"
        },
        {
          "page": 42,
          "excerpt": "다섯 땀과 노력의 결과, 경제성장을 이끈 주인공들의 이야기 우 리 가 들 려 주 는 사 회 이 야 기 우 사이 들 리 산업화로 달라진 사회와 생활 산업화로 경제가 성장하면서 국민 소득이 증가해 생활 수준도 높아졌다. 고속 국도가 건설되면서 전국이 일일"
        },
        {
          "page": 47,
          "excerpt": "옳은 설명이 적힌 창문 번호를 빈칸에 순서대로 써서 비밀번호를 찾아봅시다. 이번 주제에서 배운 내용을 정리하며 우리가 행복이를 만날 수 있는 길을 찾아봅시다. 주제마무리 독재 정치에 저항해 민주화 운동이 일어났다. 5·18 민주화 운동 당시 시민군을 "
        },
        {
          "page": 49,
          "excerpt": "산업화 카드 뉴스로 보는 인기 영상 이 단원의 독재 정권에 맞서 민주화 운동이 일어나다. 민주화로 대통령 6 과/와 지방 자치제가 부활하다. 1. 평화 통일을 위한 노력, 민주화와 산업화 나만의 누리집 완성하기 대표적인 민주화 운동에는 4·19 혁명,"
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
          "page": 59,
          "excerpt": "선거로 선출된 대표자는 구성원들의 뜻을 반영한 공약을 실천한다. 만약 대표자의 능력이 부족하거나 역할을 제대로 수행하지 못해 사람들의 지지를 받지 못하면, 다음 선거에서 대표자로 선출되기 어려울 수 있다. 이처럼 민주 주의에서 선거는 선출된 대표자의 "
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
          "page": 89,
          "excerpt": "아래 게시판의 문제를 풀어 누리가 체험 학습을 갈 장소를 찾아봅시다. 이번 주제에서 배운 내용을 정리하며 우리가 행복이를 만날 수 있는 길을 찾아봅시다. 주제마무리 되돌아가기를 만나면 교과서를 살펴본 후 처음부터 시작합니다. 72~73쪽 74~85쪽 "
        },
        {
          "page": 90,
          "excerpt": "영상이나 사진을 찍어 공유해 본 경험이 있니? 민주주의에서 미디어의 의미와 역할을 이해할 수 있어요. 미디어의 내용을 비판적으로 분석하고 평가할 수 있어요. 미디어를 올바르게 이용하는 태도를 지닐 수 있어요. 이 주제를 배우면 나는 민주주의와 미디어 "
        },
        {
          "page": 105,
          "excerpt": "2. 민주주의와 시민 참여 나만의 누리집 완성하기 민주주의와 미디어 카드 뉴스로 보는 인기 영상 이 단원의 국회의원들로 구성된 국민의 대표 기관으로, 3 을/를 만들고 고치는 일을 함. 국가기관을 가다 - 국회 편 민주주의에서 미디어의 역할 •\u0001선거 "
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
        },
        {
          "page": 145,
          "excerpt": "아프리카는 아시아에 이어 두 번째로 큰 대륙 으로, 북반구와 남반구에 걸쳐 있다. 아프리카 에는 이집트, 알제리, 케냐, 남아프리카 공화국 등 50여 개의 나라가 있다. 북반구와 남반구에 걸쳐 있는 ㅇ ㅍ ㄹ ㅋ 에는 이집트, 케냐 등 많은 나라가 있"
        },
        {
          "page": 147,
          "excerpt": "정보 활용 능력 오세아니아에는 오스트레일리아, ㄴ ㅈ ㄹ ㄷ , 키리바시 등의 나라가 있다. 한 문장 정리 1 146쪽 지도의 나라 중 하나를 선택해 위치와 영토 특징을 이야기해 봅시다. 2 \u0007디지털 공간 영상 정보를 활용해 오세아니아에 있는 여러 나"
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
