# Agent Docs

현재 NumbersAuto 파이프라인에서 사용하는 agent를 문서 단위로 정의한다.

기준:
- 각 agent는 `scripts/*.py`의 실제 구현 책임을 따른다.
- 입력과 출력은 현재 run-root 구조를 기준으로 적는다.
- review stage도 가능한 한 독립 Python 실행 단위로 유지한다.

현재 agent 목록:
- `document_inventory_agent`
- `pdf_extract_agent`
- `page_index_agent`
- `schedule_parse_agent`
- `lesson_query_agent`
- `page_candidate_agent`
- `boundary_decision_agent`
- `boundary_validation_agent`
- `source_boundary_agent`
- `source_validation_agent`
- `lesson_analysis_agent`
- `lesson_review_agent`
- `activity_plan_agent`
- `activity_review_agent`
- `html_card_agent`
- `capture_agent`
- `numbers_compose_agent`
- `review_manifest_agent`
- `verify_agent`

실행 기준 진입점:
- `python3 scripts/pipeline_orchestrator.py --config configs/<config>.json`

기본 stage 순서:
1. `source_boundary_agent`
2. `source_validation_agent`
3. `lesson_analysis_agent`
4. `lesson_review_agent`
5. `activity_plan_agent`
6. `activity_review_agent`
7. `html_card_agent`
8. `capture_agent`
9. `numbers_compose_agent`
10. `review_manifest_agent`
11. `verify_agent`

관련 문서:
- [AGENT_TEST_PLAN.md](./AGENT_TEST_PLAN.md)
- [PIPELINE_AGENT_CATALOG.md](./PIPELINE_AGENT_CATALOG.md)
- [READING_AGENT_CONTRACTS.md](/Users/jonyeock/Desktop/Tool/NumbersAuto/archive/docs/plans/20260331_manual_workflow_cleanup/READING_AGENT_CONTRACTS.md)
- `ACTIVITY_RULE.md`
- `NumbersDesign.md`
- `MULTI_RESOURCE_POLICY.md`

비고:
- 현재 canonical 경로는 [MANUAL_PAGE_SELECTION_WORKFLOW.md](/Users/jonyeock/Desktop/Tool/NumbersAuto/MANUAL_PAGE_SELECTION_WORKFLOW.md) 기준의 `pdf_pages` 확정 config다.
- 이 경우 읽기/해석 계층은 기본 경로에서 skip 될 수 있다.
- `source_boundary_agent`와 아래 읽기/해석 계층은 자동 차시 분류가 필요한 legacy/optional path로 본다.
  - `document_inventory_agent`
  - `pdf_extract_agent`
  - `page_index_agent`
  - `schedule_parse_agent`
  - `lesson_query_agent`
  - `page_candidate_agent`
  - `boundary_decision_agent`
  - `boundary_validation_agent`
