# Harness·Judge 튜닝 기록

M7의 두 Uber 기존 실행을 같은 최초 생성본에서 A~E로 비교했다. 생성·보완은 `gpt-6.1-sol / medium`, 운영 Judge와 독립 평가는 `gpt-6.1-sol / high`다. 독립 LLM 판정은 잠정 결과이며 사람 검토를 마쳤다고 가정하지 않는다.

## 실제 기준선

### Middle

| 조건 | 하네스 검사 | Judge 호출 | 보완 완료 | 추가 시간(초) | 독립 통과율 |
| --- | --- | --- | --- | --- | --- |
| A | 0 | 0 | 0 | 0.00 | 100% |
| B | 1 | 1 | 0 | 16.41 | 100% |
| C | 1 | 0 | 0 | 0.00 | 100% |
| D | 0 | 1 | 0 | 13.77 | 100% |
| E | 1 | 1 | 0 | 24.39 | 100% |

모든 조건이 정상 종료했다.

### Senior

| 조건 | 하네스 검사 | Judge 호출 | 보완 완료 | 추가 시간(초) | 독립 통과율 |
| --- | --- | --- | --- | --- | --- |
| A | 0 | 0 | 0 | 0.00 | 97.5% |
| B | 1 | 1 | 0 | 38.51 | 97.5% |
| C | 1 | 0 | 0 | 0.00 | 97.5% |
| D | 0 | 3 | 2 | 196.74 | 97.5% |
| E | 3 | 3 | 2 | 220.58 | 97.5% |

A·C는 정상 종료, B는 오류 관찰 후 종료, D·E는 보완 상한 도달로 종료했다. 두 표에서 보완 호출은 모두 완료되어 호출 수와 완료 수가 같다.

A는 검사 없음, B는 둘 다 검사만, C는 하네스 보완, D는 Judge 보완, E는 둘 다 보완이며 보완은 합계 최대 두 번이다. 추가 시간은 검사·보완 시간이고 독립 평가 시간은 별도다. A·B 및 동일 내용의 산출물은 독립 평가와 Trace를 재사용했다. 자연 발생 오류를 주입 사례와 섞지 않았다.

- Middle: 하네스·Judge 모두 문제를 지적하지 않았고 보완 없이 100%였다.
- Senior: 하네스 Finding은 0개였다. Judge는 `NFR_NOT_GROUNDED / export.tradeoffs[0]`를 반복 지적했다. 주변 후보 검색 지연과 배정 확정 경로의 조정 지연을 연결하는 Trade-off의 근거가 부족하다는 판단이다. 사람의 최종 정답 판정은 아니다.
- Senior D·E는 각각 두 번 보완했지만 같은 선정 오류가 남았고 독립 루브릭 통과율도 97.5%였다. 독립 평가의 Fail은 `2-2 / NFR-3`의 요구 수준 명확성이며, Judge가 지적한 Trade-off와 구분한다. 독립 루브릭 평가만으로 선정 오류 해결을 단정하지 않는다.
- 사람 정답 라벨이 없어 TP·FP·FN, Precision·Recall 및 확인된 오류 해결 수는 N/A다. `provisional_changes`는 평가 기준·대상 조합의 변화이며 중복 없는 실제 오류 수가 아니다.

원본: Middle `20261017-142751-994x8noq`, Senior `20261017-143246-h69dfxub`. 기록: `.archgen/m7-followup/comparison/{middle,senior}/`의 `comparison.json`, `comparison.md`, 회차별 생성본·Finding·평가.

| 평가 | Trace |
| --- | --- |
| Middle A 및 동일 산출물 | [24ed01f292b04905ae7ee996948179b7](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/24ed01f292b04905ae7ee996948179b7) |
| Senior A 및 동일 산출물 | [4f66edb75d4a43c68f95ce4a9fa22ba1](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/4f66edb75d4a43c68f95ce4a9fa22ba1) |
| Senior D 보완 후 | [387f07a0355e49faa17da9b64b54ddf6](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/387f07a0355e49faa17da9b64b54ddf6) |
| Senior E 보완 후 | [6888c0fd09014b08a13b29f26580b36d](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/6888c0fd09014b08a13b29f26580b36d) |

## 알려진 오류의 별도 검증

두 실행에 배점 합계·점수 중복을 각각 주입한 구조 오류 4개에서 하네스가 예상 코드를 검출했다. 2점 기준을 모호한 문장으로 교체한 의미 오류 2개는 실제 Sol high Judge가 모두 `LEVEL_AMBIGUOUS`로 지적했다. 이는 구성한 사례의 검증이며 일반적인 탐지 정확도·Precision·Recall이 아니다. 정답 라벨은 `synthetic_expected`로 남겼다.

## 튜닝 1. 동일 경로를 미탐으로 집계하는 오류

문제: 모호한 서술 두 사례를 Judge가 지적했는데 초기 집계는 0/2였다. 스크립트는 `rubric.criteria[0]`으로 시작하는지만 검사했고 실제 경로는 `export.rubric.criteria[0]...`이었다.

수정: 사람 라벨 대조와 주입 사례 집계에서 선택적 `export.` 접두어만 제거하고 비교한다. 다른 경로를 합치지 않는다. 해당 테스트를 먼저 실패시킨 뒤 통과시켰다.

같은 모델 응답을 그대로 재집계한 결과는 0/2 → 2/2다. 모델 호출·프롬프트·판정 근거는 바꾸지 않았고 원본 응답도 보존했다. 집계 수정은 채택하며 모델 성능 개선으로 주장하지 않는다. 재집계 파일은 `.archgen/m7-followup/known-errors/summary-v2.json`이다.

의미 사례 Trace: Middle `8f0b5239f8954f2296bdbf3674b5cc24`, Senior `9e9903b5638b4576b3e76a6debfff97e`.

## 튜닝 2. 루브릭으로 바꿀 수 없는 선정 오류의 반복 보완

문제: Senior의 Trade-off 오류가 두 번 보완 뒤에도 동일하게 남았다. `generate_rubric`은 Selection을 고정 입력으로 받아 rubric만 반환하므로 선정된 NFR·Trade-off·범위·제외 요구는 바꿀 수 없다.

수정: 이 고정 영역에만 있는 오류는 루브릭 보완을 반복하지 않고 상위 선정 단계의 수정 필요를 명시한다. 수정 가능한 루브릭 오류와 경로를 알 수 없는 오류의 기존 보완 동작은 유지한다. 선정 NFR을 평가 항목이 덮지 못한 `NFR_NOT_COVERED`는 항목 추가로 고칠 수 있으므로 계속 보완한다. 실제 생성 그래프와 수동 비교 도구가 같은 분류 함수를 사용한다.

검증: 선정 오류의 보완 0회·실패 이유, 수정 가능한 오류의 최대 두 번 보완, 미커버 NFR의 보완 유지에 대한 테스트를 확인했다. 실제 후속 비교는 같은 Senior 최초 생성본·이전 렌더 MD·평가 결과·모델 설정을 고정해 D·E 각 한 번씩 수행했다. 렌더 정성 목표 수정의 품질 변화와 분리했으며, 결과와 개선율은 아래에 기록했다.

기록: `.archgen/m7-followup/repair-tuning/`. 현재 코드 변경은 미커밋이다. 이 단계의 튜닝은 두 회차로 한정한다. 이 사례 실험 당시에는 단계 기준 수정으로 추가 평가를 중단했다. 현재 새 기준의 실행 상태와 하루 범위는 [M7 계획](../m7.md)을 따른다. 이번 기록은 다주제 반복 실험 완료를 뜻하지 않는다.

## 성과의 범위

동일한 두 생성본에서 코드 검사와 의미 검사의 역할을 구분하고, 실제 응답을 잘못 세는 집계 오류 및 보완할 수 없는 영역의 반복 호출 원인을 확인했다. 두 Uber 실행과 작은 주입 사례의 결과이며, 다른 주제의 일반화 성능이나 사람이 확인한 탐지 정확도를 주장하지 않는다.

### 튜닝 2 실제 후속 결과

| 조건 | 보완 횟수 전→후 | Judge 호출 전→후 | 추가 시간 전→후(초) | 관측 시간 감소율 | 종료 후 상태 |
| --- | --- | --- | --- | --- | --- |
| D | 2 → 0 | 3 → 1 | 196.74 → 56.14 | 71.47% | requires_upstream_repair |
| E | 2 → 0 | 3 → 1 | 220.58 → 47.14 | 78.63% | requires_upstream_repair |

같은 Senior 최초 생성본에서 D·E 각각 전후 1회씩 관찰했다. 수정 후에도 선정 오류는 남아 있으며 `requires_upstream_repair`로 명시한다. 오류를 해결한 것이 아니라 고칠 수 없는 영역에 대한 보완 호출을 생략한 것이다. 기존 MD와 같음을 확인한 뒤 A의 독립 평가(97.5%)를 재사용하여 렌더 수정과 품질 효과를 섞지 않았다. 실제 생성 그래프도 같은 오류에서 보완 0회와 실패 이유를 남긴다. 미커버 NFR의 루브릭 보완은 별도 회귀 테스트로 유지했다.

판단: **재시도 범위 수정 채택**. 보완 횟수는 각 2→0회, Judge 호출은 각 3→1회로 줄었다. 시간 감소율은 서버 응답 변동을 포함한 해당 실행의 관측값이며 일반적인 속도 개선으로 단정하지 않는다. 사람 검토 없는 선정 오류의 해결 수·Precision·Recall은 계속 N/A다. 기록: `.archgen/m7-followup/repair-tuning/after/`.


## 새 기준 연결 후 최소 회귀 검사 — 2026-10-19

검사 코드·Judge 프롬프트·모델은 변경하지 않았다. 기존 구조 오류 4사례는 각 1회 모두 예상 코드를 검출했다. 기존 의미 오류 두 사례는 Sol high로 각각 2회 검사했다. 이 결과는 기존 오류 검출의 회귀 확인이며 새 탐지 성능 튜닝이나 일반화 검증이 아니다.

| 대상 | 반복 | 예상 오류 검출 | 시간(초) | Trace |
| --- | --- | --- | --- | --- |
| middle | 1 | 검출 | 21.09 | [Trace](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/bfc2e2fe1d824633b26b7e6670cd1442) |
| middle | 2 | 검출 | 23.13 | [Trace](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/bf2ba9ba17d741249ccf3d57ee6e0cd2) |
| senior | 1 | 검출 | 21.97 | [Trace](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/820375a3f02b436aaa71e987064150e3) |
| senior | 2 | 검출 | 26.06 | [Trace](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/f2d2746eebf04e18ab389bb44d6f349f) |

의미 오류는 4/4회 모두 해당 2점 문장의 `LEVEL_AMBIGUOUS`를 검출했다. 정상 대조와 사람 확정 라벨을 추가한 실험은 수행하지 않았으므로 정밀도·재현율은 N/A다. 원본 응답·사용량·Finding: `.archgen/m7-followup/current-criteria-20261019/regression/`.


## 추가 요청: 하네스 규칙·Judge 프롬프트 전후 검출 실험 — 2026-10-19

이전 4/4 회귀 확인과 별도의 실험이다. 사례·정상 대조·오류 정의·응답 스키마를 먼저 저장했다. 기존 Senior 생성본에서 관련 없는 Trade-off를 제거한 고정 입력을 사용하고, 아래 두 오류만 각각 변형했다. 자연 발생 오류와 통제 변형을 합쳐 일반화 성능으로 제시하지 않는다.

### 하네스 — 정량 목표의 값·단위 누락 규칙 채택

기존 `NFRTarget`은 값 또는 단위가 빠진 객체도 파싱되지만 하네스에 해당 검사가 없었다. 모델 출력에 정량 목표가 있으면 `value`와 공백 아닌 `unit`이 모두 있어야 한다는 `check_targets`를 추가했다. 값 0과 정성 목표는 허용한다. 기존 규칙·입력은 고정하고 이 검사만 추가해 비교했다.

| 통제 사례 | 규칙 추가 전 | 규칙 추가 후 |
| --- | --- | --- |
| 기존 구조 오류 4건 | 4/4 검출 | 4/4 검출 |
| 정량 목표 오류 4건: 빈 객체·값 누락·단위 누락·공백 단위 | 0/4 검출 | 4/4 검출 |
| 오류 사례 전체 | 4/8 검출·4건 미검출 | 8/8 검출·0건 미검출 |
| 정상 대조: 기존 두 생성본·값 0인 완전한 목표 | 오탐 0/3 | 오탐 0/3 |

**새 규칙은 채택했다.** 실제 생성 그래프와 비교 실행 도구에 모두 연결했다. 선정된 목표 오류이므로 루브릭만 고치는 재시도를 하지 않고 상위 선정 수정 필요로 실패 종료한다. 그래프 테스트에서 Judge 호출·루브릭 보완·최종 MD 전달이 발생하지 않는 것을 확인했다. 이 수치는 통제한 오류 범위의 검출 커버리지이며 실제 발생 빈도나 일반적인 정확도가 아니다.

별도로 과거 원본의 실제 정성 목표 누락도 재현했다. 당시 저장된 Post-Render 검사는 Middle·Senior 모두 Finding이 없었지만, 현재 검사는 동일한 과거 MD에서 각 4개, 총 8개의 `RENDER_REQUIREMENT_MISMATCH`를 검출했다. 올바르게 렌더한 두 문서에서는 지적이 없었다. 이는 **앞서 추가한 렌더 검사의 효과 재현**이고, 이번 정량 목표 규칙이나 Judge 프롬프트의 개선으로 합산하지 않는다.

### Judge — 프롬프트 후보의 개선 효과 없음, 되돌림

고정한 표적 오류는 다음과 같다. 정상 대조는 관련 없는 Trade-off만 제거한 원본이며, 표적 오류 이외의 모든 내용에 대한 사람 정답을 확정한 것은 아니다.

- 요구 수준 모호: NFR-3의 statement를 “시스템은 빠른 매칭 응답을 제공해야 한다.”, 정성 목표를 “낮은 지연 시간을 우선시한다.”로 바꾸어 개선 대상·조건을 제거했다. 다른 필드의 구체성을 요구 수준의 충족으로 대신하지 않는지 검사한다.
- Senior 2점 대응 누락: C4의 2점을 수집·검색 반영 서버 분리, 큐, 병렬 처리, 서버 증설만 설명하는 문장으로 바꿨다. 주요 적체 문제에 대한 대응은 제거하고 다른 점수는 유지했다.

수정 전후 모두 같은 Sol high, 같은 사례 3개, 사례당 2회씩 총 12회 호출했다. 새 `NFR_REQUIREMENT_AMBIGUOUS` 응답 코드는 **양쪽 스키마에 공통으로 먼저 추가**했다. 따라서 아래 비교는 동일한 확장 스키마에서 프롬프트만 바꾼 결과이며, 예전 운영 Judge 전체와의 순수 비교라고 주장하지 않는다. 새 코드 수용은 프롬프트 개선 수치로 세지 않는다.

**수정 전 해당 구간**

```text
- LEVEL_NOT_PROGRESSIVE: 단계 간 실질적인 수준 차이가 없거나 역전됨.
- NFR_NOT_GROUNDED: NFR·목표·trade-off가 evidence_refs로 인용된 보존 문장과 맞지 않음.
```

**수정 후 후보에서 사이에 추가한 원문 — 현재는 되돌림**

```text
- NFR_REQUIREMENT_AMBIGUOUS: statement와 정량·정성 목표를 함께 읽어도 개선할 시스템 동작과 보장·개선 조건이 드러나지 않고 추상적인 품질 선언만 남음. rationale나 Criterion의 설명으로 요구 수준 필드의 누락을 대신하지 않는다. statement가 추상적이어도 목표 필드가 구체적이면 지적하지 않는다. 입력에 없는 수치 목표를 요구하지 않는다.
- Senior의 2점은 구체적 메커니즘과 해당 설계의 주요 문제에 대한 대응 흐름을 요구한다. 기본 배치·병렬화·저장 경로만 설명하거나 문제를 한계로 서술하기만 하고 대응을 3점으로 미뤘다면 CRITERION_UNSCORABLE로 지적한다. 해당 항목과 무관한 장애를 일괄 요구하지 않고, 3점의 심층 분석·Trade-off까지 2점에 요구하지 않는다.
```

| 지표 | 수정 전 | 수정 후 |
| --- | --- | --- |
| 요구 수준 모호 표적 검출 | 2/2 | 2/2 |
| Senior 2점 대응 누락 표적 검출 | 2/2 | 2/2 |
| 표적 오류 미검출 | 0/4 | 0/4 |
| 정상 대조에서 지적 발생 | 0/2 | 0/2 |
| 검출률 변화 | 기준선 100% | +0%p |
| 호출당 평균 시간 | 32.79초 | 27.26초 |

같은 경로의 중복 Finding은 오류 1건으로 센다. 수정 후 한 응답의 동일 코드·경로 두 지적을 검출 증가로 계산하지 않았다. 연속 호출의 시간 차이도 일반적인 속도 개선으로 해석하지 않는다.

**판단: 후보 프롬프트를 되돌렸다.** 이번 고정 사례에서 추가 검출·오탐 감소가 확인되지 않아 프롬프트를 길게 유지할 근거가 부족했다. 원문·후보·diff·해시·입력·전체 응답·중복 지적을 모두 보존했다. 요구 수준 모호를 표현할 수 있는 공통 응답 코드는 유지한다. 라벨은 기존 연차·품질 기준에 따른 통제 변형과 agent 검토 결과이며 사람이 확정한 자연 발생 오류의 정밀도·재현율은 계속 미측정이다.

| 사례·반복 | 수정 전 Trace | 수정 후 Trace |
| --- | --- | --- |
| normal 1 | [Trace](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/9dc5d15a12b442e6abacb8669b91086d) | [Trace](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/16c7661dd41b44b19d7b5b0e2dcd23af) |
| normal 2 | [Trace](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/204f15313813469b9ff976a25f430e1c) | [Trace](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/c20687fc28584348b0416347471a9baf) |
| vague_requirement 1 | [Trace](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/4fb643153abf4c649ce8971fc0e1bb2d) | [Trace](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/7c0589146e114d3a9d77a858dea7e814) |
| vague_requirement 2 | [Trace](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/8edf3e4c3af9458f89b77436134a3825) | [Trace](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/2ff4c656de494349878a990de85c2f2e) |
| senior_level2_gap 1 | [Trace](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/f5b27ee98cd346a188cdcbb5f1ec1c5b) | [Trace](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/c9c413e2f9d54c7496efd2fdec1cfe03) |
| senior_level2_gap 2 | [Trace](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/d6583975ad334e689ca946c929a857f8) | [Trace](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/92139e9bd1a64cada3393cb76bc6c0b8) |

이번 추가 실험 12회 호출의 확인 비용 추정은 $0.2606, 기존 M7 전체 누적 확인 비용은 $13.6672다. 실패·과거 중단 호출의 미확인 과금과 검색 요금은 제외한다. 생성·보완·외부 검색은 추가 실행하지 않았다. 자료는 `.archgen/m7-followup/detector-tuning-20261019/`의 `cases.json`, `schema.json`, `hypothesis.json`, `harness-results.json`, `judge-results.json`, 전후 원문과 회차별 응답이다.
