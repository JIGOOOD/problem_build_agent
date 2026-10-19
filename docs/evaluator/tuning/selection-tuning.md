# Selection 튜닝 기록

평가 대상: NFR 선정 타당성·근거 일치·핵심 초점 누락·중복 선정.
평가 기준: [Selection 평가 기준](../selection.md).

## 현재 상태

새 기준으로 기존 Uber 저장 결과를 평가 중이다. 아래 결과는 기존 산출물의 진단이며 프롬프트 튜닝 성능이 아니다. Selection 프롬프트는 변경하지 않았다. 사람 미검토 판정은 잠정값이다.

예전 기준의 준비 표·승인 대기 설명·2회 반복 예정·중복 템플릿은 제거했다. 실제 실행하지 않은 실험을 성과로 기록하지 않는다. 이전 문서 사본은 `.archgen/m7-followup/document-history/before-one-day-plan/`에 보존했다.

## 실제 실행 후 기록할 내용

문제와 원문 근거 → 원인·가설 → 수정한 프롬프트 → 고정 입력·모델·기준·반복 횟수 → 실행별 전후 결과·Trace·비용 → 회귀·채택/보류/되돌림 순서로 기록한다.

실행 범위와 횟수는 [M7 하루 실행 계획](../m7.md)을 따른다. 코드 검증은 품질 실험과 구분하고, 새 결과가 생기기 전에는 빈 결과 표나 예상 개선 수치를 추가하지 않는다.

## 새 기준선 — 2026-10-19

선정된 NFR 4개에 대해 1-1·1-2 각 4개, 전체 결과에 대해 2-1·2-2 각 1개를 평가했다. 핵심 초점 누락은 두 연차 모두 검출되지 않았다.

| 대상 | Pass | Fail | 판단 불가 | 통과율 | 소요 시간 | Trace |
| --- | --- | --- | --- | --- | --- | --- |
| middle | 10 | 0 | 0 | 100.0% | 119.7초 | [Trace](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/590fd7d1ee6c467f8bc6a2fe759a823e) |
| senior | 10 | 0 | 0 | 100.0% | 103.1초 | [Trace](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/fcbef2e1d87f4e65a82e06f970559455) |

연차별 한 산출물의 진단값이며 일반화 성능이나 개선 수치가 아니다. 실제 입력·기준 스냅샷·모델·호출 사용량은 `current-criteria-20261019/baseline/{middle,senior}/selection*.json`에 보존했다. 이 결과만으로 Selection 프롬프트를 의무적으로 변경하지 않는다.
