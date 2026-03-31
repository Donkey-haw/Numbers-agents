# Config Layout

`configs/`는 이제 수동 페이지 선택 workflow의 실행 결과만 보관한다.

- `configs/units/<subject>/`
  - 교사가 교과서 페이지를 직접 선택한 뒤 생성된 final config
  - 각 section은 `pdf_pages`를 직접 가진다.

운영 원칙:

- 새 실행은 `configs/units/` 아래에서 생성된 config만 사용한다.
- 과거 chart/samples/legacy config는 active tree에 두지 않는다.
- 기존 config가 필요하면 `archive/`에서만 참고한다.
