# Legacy Scripts

이 폴더는 범용 실행기 도입 전에 사용하던 스크립트를 보관한다.

## 이유
- 하드코딩된 파일명, 페이지 범위, 시트명에 의존한다.
- 현재 표준 흐름인 `configs/*.json + generate_numbers_lesson.py`보다 재사용성이 낮다.
- 과거 실험이나 참고 구현을 보존하기 위해 삭제하지 않고 분리했다.

## 현재 표준
```bash
python3 scripts/generate_numbers_lesson.py --config configs/<name>.json
```
