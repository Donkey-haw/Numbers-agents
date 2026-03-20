# V1 Activity Templates

이 디렉토리는 v1에서 공식 지원하는 활동 템플릿 3종의 기준본을 보관한다.

## Supported Templates
- `learning_note.html`
- `see_think_wonder.html`
- `worksheet.html`

## Design Contract
- [NumbersDesign.md](/Users/jonyeock/Desktop/Tool/NumbersAuto/NumbersDesign.md)의 배지, 파스텔 배경, 검정 테두리, iPad 필기 영역 원칙을 따른다.
- 학생 입력 영역은 반드시 `2px solid #333` 이상의 테두리를 사용한다.
- 템플릿은 자유 HTML 생성의 참고 예시가 아니라, 향후 렌더러가 따를 기준 UI다.

## Intended Next Step
- 각 템플릿은 정적 기준본이다.
- 다음 단계에서 `activity_plan.json` payload를 받아 결정론적으로 HTML을 렌더링하는 renderer를 연결한다.
