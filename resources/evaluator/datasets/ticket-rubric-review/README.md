# 실제 티켓 루브릭 검토 데이터

원본 데이터셋 ID: `ticket_uploaded_expected_v2`

## 전체 구성

- `inputs/ticket/middle/nfr_rubric.md` — Middle 원문, 바이트 그대로
- `inputs/ticket/senior/nfr_rubric.md` — Senior 원문, 바이트 그대로
- `policy/seniority-criteria_채점표_수정본.md` — 이번 판정에 적용한 연차별 점수 기준
- `review/expected_labels.md` — Middle·Senior 32개 Level 원문, 각 판정, 이유 및 4-1 비교
- `review/expected_labels.json` — 같은 라벨의 구조화된 정답 후보
- `review/judgment_basis.md` — 채점 경계와 오탐 판정 원칙
- `validation_report.json` — 구성·원문 동일성·정답 구조 검증

## 결과

32 Level: Pass 21, Fail 11. 8 Criterion: Pass 2, Fail 6. 연차 비교 4-1: Fail 1쌍.

이것은 **평가기가 루브릭 난이도를 올바르게 판정하는지 검증하는 데이터**다. 지원자 답안의 점수를 매기는 데이터가 아니다. 두 원문은 수정하지 않았으며, 최신 채점표에 맞춰 판정과 근거만 수정했다. 기존 v1과 별도 파일로 보존했다.

## 사용

평가기에는 `inputs/`의 두 원문과 `policy/` 채점표만 제공한다. `review/`와 `validation_report.json`은 정답 누출 방지를 위해 주지 않는다.

3-5는 Middle·Senior Criterion별로 0~3점 각각의 필수 요구가 적절한지 확인한다. 4-1은 대응 항목의 연차별 요구 차이를 확인한다. 둘은 별개이며, Level 하나라도 Fail이면 해당 Criterion 전체가 Fail이다.

`†`가 붙는 개별 Level/항목은 사람이 재확인해야 하는 해석 경계 사례다. 판정 방향은 제안하지만 검토 전에는 확정 정답으로 보지 않는다. 실제 평가기를 호출한 결과는 아니다.
