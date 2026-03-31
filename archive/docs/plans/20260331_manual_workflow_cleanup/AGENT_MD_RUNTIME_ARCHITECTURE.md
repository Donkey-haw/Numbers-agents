# AGENT.md Runtime Architecture

## 목적

이 문서는 NumbersAuto를 `agent별 전용 스크립트` 중심 구조에서
`AGENT.md 중심 실행 구조`로 옮기기 위한 설계 방향을 정리한다.

핵심 목표:

- 각 Agent의 기능 정의를 `AGENT.md`에 고정한다.
- 오케스트레이터는 `AGENT.md`를 읽고 실행한다.
- Agent별 스크립트는 점진적으로 줄이고, 공용 runtime만 남긴다.
- Rules와 hook으로 특정 기능이 반드시 특정 Agent를 거치도록 강제한다.


## 핵심 판단

`AGENT.md`가 충분히 엄격한 실행 계약이 되면,
각 Agent마다 별도 Python 스크립트가 반드시 필요한 것은 아니다.

다만 완전히 코드가 없어지는 것은 아니다.
남아야 하는 것은 아래 두 종류다.

1. 공용 runtime
2. deterministic tool adapter

즉 제거 대상은 "agent별 전용 구현 스크립트"이고,
남는 것은 "문서 기반 agent 실행기"다.


## 현재 구조와 목표 구조 비교

## 현재 구조

- `AGENT.md`: 설명 문서
- `scripts/<agent>.py`: 실제 구현
- `pipeline_orchestrator.py`: stage 순서 관리

문제:

- 책임 정의는 문서에 있고, 실제 동작은 스크립트에 있다.
- 문서와 구현이 어긋날 위험이 있다.
- 기능 경계를 문서가 아니라 구현이 사실상 결정한다.


## 목표 구조

- `AGENT.md`: 실행 계약
- `agent_runtime`: 공용 실행기
- `tool adapters`: deterministic tool 호출 계층
- `pipeline_orchestrator`: DAG와 hook 관리

즉 구조는 아래처럼 바뀐다.

1. 오케스트레이터가 실행할 Agent를 결정한다.
2. runtime이 해당 `AGENT.md`를 읽는다.
3. runtime이 입력 artifact, 허용 tool, 출력 artifact 규칙을 해석한다.
4. deterministic task면 tool adapter를 호출한다.
5. model task면 CLI agent를 호출한다.
6. 출력 artifact를 검증한다.
7. hook에 따라 downstream을 연다.


## `AGENT.md`가 가져야 할 필수 필드

지금처럼 자유 서술만 있으면 실행 계약으로 쓰기 어렵다.
앞으로는 모든 `AGENT.md`가 아래 항목을 공통으로 가져야 한다.

### 1. identity

- agent name
- status
- layer


### 2. responsibility

- 역할
- 단일 책임 설명


### 3. inputs

- 읽을 수 있는 artifact 목록
- 필수 입력 / 선택 입력 구분


### 4. outputs

- 생성해야 하는 artifact 목록
- status file 경로


### 5. allowed_tools

- local deterministic tool
- model inference tool
- rendering/platform tool

예:

- `pymupdf`
- `json_schema_validator`
- `gemini_cli`
- `playwright`


### 6. allowed_actions

- 이 Agent가 할 수 있는 기능


### 7. forbidden_actions

- 이 Agent가 해서는 안 되는 기능


### 8. rules

- 이 기능은 반드시 이 Agent를 거친다


### 9. hook_contract

- 어떤 입력 artifact가 없으면 이 Agent를 호출해야 하는가
- 어떤 출력 artifact가 생기면 어떤 Agent가 다음으로 열리는가


### 10. success_criteria

- 성공 판정 기준


### 11. failure_modes

- 실패 유형
- retry 가능 여부
- fallback 가능 여부


## 권장 `AGENT.md` 템플릿

```md
# agent_name

## identity
- status: planned|active|deprecated
- layer: reading|generation|rendering|verification

## responsibility
- ...

## inputs
- required:
  - ...
- optional:
  - ...

## outputs
- ...

## allowed_tools
- local:
  - ...
- model:
  - ...
- platform:
  - ...

## allowed_actions
- ...

## forbidden_actions
- ...

## rules
- ...

## hook_contract
- trigger_if_missing:
  - ...
- unlocks:
  - ...

## success_criteria
- ...

## failure_modes
- ...
```


## Runtime이 해야 하는 일

`AGENT.md` 중심 구조에서는 runtime이 훨씬 중요해진다.

runtime은 아래 기능을 가져야 한다.

### 1. Agent 문서 로드

- `agents/<agent>/AGENT.md` 읽기


### 2. Agent spec 파싱

- 문서에서 구조화된 필드 추출
- 가능하면 YAML frontmatter 또는 명시 구간 파싱


### 3. 입력 artifact 확인

- required input 존재 여부 확인
- 없으면 hook 규칙 확인


### 4. tool 권한 제한

- 허용된 tool만 호출 가능
- forbidden action 수행 시 실패 처리


### 5. 실행 방식 분기

- deterministic agent:
  - local tool adapter 실행
- model agent:
  - Gemini/Codex CLI 실행


### 6. 출력 artifact 검증

- output path 생성 확인
- schema validation
- status file 작성


### 7. event / manifest 반영

- running
- succeeded
- failed
- blocked


## 공용 Tool Adapter 구조

agent별 스크립트를 줄이려면 deterministic 작업을 공용 adapter로 빼야 한다.

예:

- `tool_pdf_extract`
- `tool_page_index`
- `tool_json_schema_validate`
- `tool_page_candidate_score`
- `tool_numbers_compose`

중요한 점:

- tool은 기능 단위여야 한다.
- Agent는 tool을 조합할 뿐, 자기만의 숨겨진 구현을 가지지 않는 방향이 좋다.


## 오케스트레이터 역할 변화

현재 오케스트레이터는 stage 함수를 직접 호출한다.
목표 구조에서는 아래 역할로 축소된다.

1. DAG 관리
2. 직렬/병렬 실행 결정
3. hook 평가
4. run manifest 갱신
5. retry / cancel / timeout 관리

즉 오케스트레이터는 "업무 구현자"가 아니라 "실행 관리자"가 된다.


## Rules와 Hook의 의미

`AGENT.md` 중심 구조에서는 Rules와 hook이 핵심이다.

### Rules

Rules는 기능 독점권을 명시한다.

예:

- PDF raw text extraction은 `pdf_extract_agent`만 수행 가능
- lesson query 생성은 `lesson_query_agent`만 수행 가능
- boundary final decision은 `boundary_decision_agent`만 수행 가능


### Hook

hook은 artifact 기반으로 agent 호출을 강제한다.

예:

- `page_texts.json`이 없으면 `pdf_extract_agent` 실행
- `lesson_queries.json`이 없으면 `lesson_query_agent` 실행
- `boundary_decisions.json`은 `boundary_decision_agent`만 생성 가능

즉 hook은 convenience가 아니라 enforcement다.


## 왜 이 구조가 필요한가

이 구조의 장점은 명확하다.

1. 기능 정의와 실행 정의가 한곳에 모인다.
2. Agent 책임 경계가 더 강해진다.
3. 스크립트와 문서가 어긋날 위험이 줄어든다.
4. 멀티 CLI 환경에서 agent 교체가 쉬워진다.
5. deterministic task와 model task를 같은 runtime 위에 올릴 수 있다.


## 현실적인 전환 전략

한 번에 전부 바꾸는 것은 무리다.
아래 순서가 적절하다.

### 1단계. 문서 강화

- 모든 `AGENT.md`에 공통 섹션 추가
- 입력/출력/툴/금지 기능 명시


### 2단계. runtime 파서 추가

- `AGENT.md`에서 구조화된 필드 읽기
- 최소한 allowed_tools / inputs / outputs를 파싱


### 3단계. 읽기 레이어 전환

- `document_inventory_agent`
- `pdf_extract_agent`
- `page_index_agent`
- `schedule_parse_agent`

이 레이어부터 agent별 스크립트 대신 공용 tool adapter 호출 구조로 전환


### 4단계. boundary 레이어 전환

- `lesson_query_agent`
- `page_candidate_agent`
- `boundary_decision_agent`
- `boundary_validation_agent`


### 5단계. 기존 stage wrapper 제거

- `source_boundary_agent` 같은 transitional agent를 단계적으로 축소 또는 제거


## 지금 당장 필요한 것

지금 가장 먼저 필요한 것은 아래 두 가지다.

1. 모든 Agent 문서를 "설명 문서"에서 "실행 계약 문서"로 바꾸는 기준 확정
2. 읽기/해석 계층 Agent부터 그 기준으로 다시 정리

즉 지금은 스크립트를 먼저 지우는 단계가 아니라,
`AGENT.md`가 실제 계약 문서로 동작할 수 있게 포맷과 규칙을 먼저 고정하는 단계다.


## 결론

가능하다.

NumbersAuto는 앞으로 아래 방향으로 가는 것이 자연스럽다.

- agent별 전용 스크립트 중심
-> `AGENT.md` 중심 계약 구조
-> 공용 runtime + tool adapter + CLI inference

즉 최종적으로 남겨야 하는 것은
"각 Agent의 숨겨진 구현 파일"이 아니라
"Agent 문서와 그 문서를 실행하는 공용 런타임"이다.
