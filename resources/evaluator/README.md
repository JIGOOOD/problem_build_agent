# 평가기 데이터

튜닝에 사용한 자료와 평가기를 고정한 뒤 검사할 검증 자료를 분리한다.
Dropbox·Slack은 정상·오류 판정이 함께 있는 검증 데이터이며 골든셋으로 분류하지 않는다.

| 구분 | 데이터셋 | 입력 | 정답 |
|---|---|---|---|
| 튜닝 | 연차 오류 주입 · 8쌍 | [사례 목록](datasets/tuning/seniority-error-injection/cases.json) | [정답 JSON](datasets/tuning/seniority-error-injection/review/expected_labels.json) |
| 튜닝 | 실제 티켓 · 1쌍 | `datasets/tuning/ticket-rubric-review/inputs/ticket/` | [정답 JSON](datasets/tuning/ticket-rubric-review/review/expected_labels.json) |
| 검증 | Dropbox · 1쌍 | `datasets/validation/dropbox/inputs/dropbox/` | [정답 JSON](datasets/validation/dropbox/review/expected_labels.json) |
| 검증 | Slack · 1쌍 | `datasets/validation/slack/inputs/slack/` | [정답 JSON](datasets/validation/slack/review/expected_labels.json) |
| 검증 | YouTube · 1쌍 | `datasets/validation/youtube/inputs/youtube/` | [예상 정답 JSON](datasets/validation/youtube/review/expected_labels.json) |
| 검증 | Uber · 1쌍 | `datasets/validation/uber/uber_middle.md`·`uber_senior.md` | [정답 JSON](datasets/validation/uber/review/expected_labels.json) |
| 검증 | 신규 오류 주입 · 2주제 4쌍 | [사례 목록](datasets/validation/injected-errors/cases.json) | [예상 정답 JSON](datasets/validation/injected-errors/review/expected_labels.json) |

평가 구현은 `archgen.evaluation.evaluate`, 명령 진입점은 `evaluate_rubric.py`다.
평가에는 프로젝트의 `docs/evaluator/rubric.md`와 `resources/seniority-criteria.md`를 그대로 사용한다.
평가기·연차 기준·모델 설정을 고정하며, 데이터셋에 동봉됐던 별도 policy는 사용하지 않는다.
평가기와 연차 기준은 고정한다. 사용자가 정답 오류를 정정하면 기존 결과를 사용하지 않고 수정본으로 재평가한다.
묶음별 판정 건수를 마지막에 합산한다.

데이터셋에는 입력 루브릭, 정답 JSON, 필요한 사례 목록만 남긴다.
policy·중복 정답 Markdown·템플릿·패키지 검증 리포트는 제거했다.
입력 원문과 정답 판정·근거는 유지하며, 데이터셋 명칭과 사용하지 않는 기준 파일 참조만 정리했다.
현재 정답표의 범위는 3-5·4-1이다. 정답 JSON은 평가 모델에 전달하지 않고 사후 대조에만 사용한다.

이전 튜닝 데이터 두 세트의 사용자 정답 확인은 [확인 기록](label-approval.json)에 보존한다.
티켓·Dropbox·Slack의 현재 정답은 `ticket_dropbox_slack_uber_anchor_v1.zip`의 수정본이다.
입력은 기존과 같고, 정답 판정 변경은 Slack Senior C1 1점 Fail→Pass이며 그 밖에는 판단 근거를 정리했다.
이전 튜닝의 티켓 정답은 [당시 정답](datasets/tuning/ticket-rubric-review/review/expected_labels-before-anchor.json)으로 고정하여 과거 기록을 보존한다.
새 운영 정답의 독립 검토를 완료했다고 주장하지 않는다.
검증 데이터의 제공된 판정은 별도로 대조하며, 튜닝 결과와 검증 결과를 섞어 최종 성능으로 집계하지 않는다.
Criterion Fail만으로 해당 항목의 모든 Level 오류를 검출했다고 세지 않으며, 같은 원인과 상속 영향도 구분한다.

원본 데이터는 이 디렉토리에만 두고 실험 결과는 원본 경로·오류 ID를 참조한다.
이전 실행의 입력 경로·해시는 당시 이력이며, 폴더 이동 후 현재 원본 참조만 갱신한다.
[튜닝 실험 기록](../../docs/evaluator/experiments/evaluator/error-detection-before-tuning/README.md)을 함께 확인한다.

현재 재평가 결과: [4차 튜닝](../../docs/evaluator/experiments/evaluator/rubric-criteria-round4/README.md) · [검증 결과](../../docs/evaluator/experiments/evaluator/validation-20261024/README.md).
사용자 요청으로 이전 검증 결과·원시 응답은 삭제했으며 이번 검증 기록만 유지한다. 기존 round1~3 튜닝 기록과 검증 데이터는 유지한다.

Uber는 사용자가 전체 Pass인 정상 기준으로 확인했으며 현재 검증 정확도에 포함한다. 실제 평가기의 Senior C3 Fail은 오탐으로 유지한다.
