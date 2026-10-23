# 평가기 검증 자료

이 디렉토리는 Rubric Evaluator의 3-5·4-1 판단을 검증할 입력과 정답표를 보관한다.
원본 패키지의 파일 내용과 내부 경로를 유지한다.

| 데이터셋 | 입력 | 정답·검토 자료 | 연차 정책 |
|---|---|---|---|
| [연차 오류 주입 검증](datasets/seniority-error-injection/README.md) | `cases.json`의 8쌍 | `review/` | 평가 시점의 프로젝트 연차 기준 |
| [실제 티켓 루브릭 검토](datasets/ticket-rubric-review/README.md) | `inputs/ticket/`의 1쌍 | `review/` | 데이터셋에 동봉된 `policy/` |

평가기에는 두 입력 MD와 평가·연차 기준만 전달한다. 정답·검토 폴더, 데이터셋 안내문,
검증 리포트는 모델에 전달하지 않고 결과를 대조할 때만 사용한다.

두 데이터셋의 정답표는 2026-10-24 사용자가 확인했다. [확인 기록](label-approval.json)에
대상 파일의 해시와 확인 범위를 보존한다. 원본의 `review_required`·검토 전 상태는 제작 당시
이력으로 유지하되 현재 집계에는 모두 포함한다. 같은 원인의 직접 오류와 상속 영향은 구분한다.
Criterion이 Fail이라는 사실만으로 그 안의 모든 오류를 검출했다고 세지 않는다.

검증 구현은 `archgen.evaluation.evaluate`, 기존 명령 진입점은 `evaluate_rubric.py`다.
이 데이터셋의 정답 범위는 3-5·4-1이므로 다른 평가 항목까지 포함한 결과와 혼합하지 않는다.
동봉 정책 파일을 프로젝트의 `resources/seniority-criteria.md`에 자동 적용하지 않는다.

[2026-10-24 실행 결과](../../docs/evaluator/experiments/error-detection-before-tuning/README.md)를 함께 확인한다.
