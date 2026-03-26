# Run Output Policy

이 문서는 NumbersAuto 파이프라인 실행 후 생기는 산출물의 **보관/정리 규칙**을 정의한다.

목표는 단순하다.
- 평상시에는 로컬이 지저분해지지 않게 한다.
- 성공 run은 최종 `.numbers` 파일만 남긴다.
- 실패나 디버깅 상황에서는 원인 추적이 가능하도록 artifacts를 남긴다.

## 1. 기본 원칙

1. 기본 운영 모드는 `production-style run`이다.
2. `production-style run`에서는 성공한 full run 뒤에 **최종 `.numbers` 파일만 남긴다**.
3. 중간 산출물(`artifacts/runs/<run_id>/...`)은 성공 시 자동 삭제한다.
4. 실패, 차단, 디버그, 중간 중단 run은 artifacts를 보존한다.

## 2. 성공 run의 기본 처리

조건:
- `pipeline_orchestrator.py`를 끝까지 실행
- 최종 `verify_agent`까지 성공
- 별도 보존 옵션 없음

처리:
1. run 내부에서 생성된 최종 Numbers 파일을 config의 원래 `output_file` 경로로 복사
2. `artifacts/runs/<run_id>/` 전체 삭제

즉, 성공 run 뒤에 남는 것은 기본적으로 아래다.
- `output/<final>.numbers`

남기지 않는 것:
- `artifacts/runs/<run_id>/source/*`
- `artifacts/runs/<run_id>/sections/*`
- `artifacts/runs/<run_id>/render/*`
- `artifacts/runs/<run_id>/output/*`

## 3. Artifacts를 남기는 경우

아래 중 하나라도 해당하면 run artifacts를 자동 삭제하지 않는다.

1. run 실패
2. `source_parse_agent`가 `blocked`
3. `--stop-after` 사용
4. `--debug-artifacts` 사용
5. `--run-root`를 직접 지정
6. `--keep-run-artifacts` 사용

해석:
- 디버깅, 단계별 검토, 수동 재개가 필요한 경우에는 artifacts를 남긴다.

## 4. 새 기본 운영 규칙

평소 실행:

```bash
python3 scripts/pipeline_orchestrator.py \
  --config configs/<config>.json
```

기본 결과:
- `output/<final>.numbers`만 남음

디버깅용 실행:

```bash
python3 scripts/pipeline_orchestrator.py \
  --config configs/<config>.json \
  --keep-run-artifacts
```

디버깅 결과:
- `artifacts/runs/<run_id>/...` 유지
- run 내부 산출물 추적 가능

## 5. 이유

이 정책을 쓰는 이유는 다음과 같다.

1. 대부분의 정상 실행에서는 중간 JSON, HTML, PNG를 다시 볼 일이 거의 없다.
2. run이 많이 쌓이면 `artifacts/runs/`가 빠르게 비대해진다.
3. 사용자는 보통 최종 `.numbers`만 필요하다.
4. 실패 run만 남기면 원인 추적 효율이 더 좋아진다.

## 6. 운영 해석

### 성공
- 최종 산출물만 남기고 정리

### 성공이지만 검토가 더 필요한 경우
- `--keep-run-artifacts`로 보존

### 실패
- 자동 보존

### 일시 중단
- 자동 보존

## 7. 현재 결론

현재 표준 규칙은 아래 한 줄로 요약된다.

**성공한 full run은 `output/최종.numbers`만 남기고, 나머지 run artifacts는 삭제한다.**
