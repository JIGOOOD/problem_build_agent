# Rubric 튜닝 기록

이 문서의 전후 2회 결과는 완료된 렌더 코드 수정 사례다. 새 프롬프트 튜닝·골든 비교 실험은 아직 미실행이며 [하루 계획](../m7.md)에 따라 별도로 기록한다.


M7의 기존 Middle·Senior Uber 실행에서 **정성 목표가 Markdown 출력에서 사라지는 문제**를 수정했다. 골든셋 수동 수정과 생성 모델 변경은 하지 않았다. 독립 LLM 평가 결과이며 사람이 확인한 정확도는 아니다.

## 문제와 원인

Senior의 최초 생성본은 `2-2 / NFR-3`에서 Fail이었다. 요구 수준이 '상호작용 경로에 적합한 낮은 지연'이라는 선언에 그친다는 판단이다.

데이터의 `qualitative_target`에는 전체 활성 차량의 전수 순회를 피하고 후보 검색 대기를 줄인다는 구체적인 목표가 있었다. 그러나 기존 렌더러는 정성 목표를 statement의 요약이라고 간주하여 출력하지 않았고, 후단 검사도 statement만 기대해서 누락을 놓쳤다. Selection의 근거·목표가 없는 문제와 구분한다.

## 수정과 검증

- 정성 목표가 statement와 다르면 요구 수준에 두 내용을 모두 출력한다. 같으면 중복 출력하지 않는다.
- 정량 목표의 기존 출력은 유지하고, 후단 검사도 정성 목표의 유실을 검출한다.
- `tests/test_renderer.py`에서 누락을 먼저 재현한 뒤 수정했다. 관련 렌더·후단 검사 51개가 통과했다.
- 생성·선정·Judge 프롬프트, 원본 export·Research·Selection과 평가 기준은 바꾸지 않았다. 기준선 A~E는 이전에 로드한 렌더러로 완료했고 템플릿 파일도 변경하지 않았다.

## 같은 조건의 전후 평가

모델은 `gpt-6.1-sol / high`, 기준은 `docs/evaluator/rubric.md`다. 대상별 수정 전후 각 2회이며 수정 전 1회는 동일한 최초 생성본의 A 평가를 재사용했다. 별도 익명 경로에 렌더 산출물을 만들어 평가했고 입력 데이터는 동일하다.

| 대상 | 수정 전 개별 결과 | 전 평균·범위 | 수정 후 개별 결과 | 후 평균·범위 | 변화 |
| --- | --- | --- | --- | --- | --- |
| Middle | [100.0, 100.0] | 100.00% / [100.0, 100.0] | [100.0, 100.0] | 100.00% / [100.0, 100.0] | +0.00%p |
| Senior | [97.5, 97.5] | 97.50% / [97.5, 97.5] | [100.0, 100.0] | 100.00% / [100.0, 100.0] | +2.50%p |

두 대상의 관측 평균은 98.75% → 100%(+1.25%p)였다. Senior의 기존 `2-2 / NFR-3` 실패는 두 수정 후 실행에서 Pass였고, 기존 Pass의 회귀나 신규 Fail은 관찰되지 않았다. 평가 기준·대상 조합에서 관측한 변화이며 사람이 확인한 오류 해결 수나 일반적인 정확도 개선으로 바꾸어 표현하지 않는다.

판단: **출력 보존 수정 채택**. 데이터에 있는 정성 목표를 삭제하는 코드 결함은 평가 점수와 별개로 테스트로 확인했다. Search·Keep·Selection 기준 변경과 무관한 수정이며 이 세 단계의 튜닝을 대신한 것이 아니다. 추가 튜닝 회차는 진행하지 않았다.

## Trace와 재현 자료

| 대상 | 시점 | 반복 | Trace |
| --- | --- | --- | --- |
| Middle | before | 1 | [24ed01f292b04905ae7ee996948179b7](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/24ed01f292b04905ae7ee996948179b7) |
| Middle | before | 2 | [d4e2fb7497f343f1943602a16dfe57df](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/d4e2fb7497f343f1943602a16dfe57df) |
| Middle | after | 1 | [50b5937fac25475583e492cafa794d76](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/50b5937fac25475583e492cafa794d76) |
| Middle | after | 2 | [a749883b61454316b13b925ac71c808c](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/a749883b61454316b13b925ac71c808c) |
| Senior | before | 1 | [4f66edb75d4a43c68f95ce4a9fa22ba1](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/4f66edb75d4a43c68f95ce4a9fa22ba1) |
| Senior | before | 2 | [8605cd502ce041b49049819f369601e0](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/8605cd502ce041b49049819f369601e0) |
| Senior | after | 1 | [3f00cf1e0ae64e61b208f6b18cefe055](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/3f00cf1e0ae64e61b208f6b18cefe055) |
| Senior | after | 2 | [1956fdcfb64f4a94a7d9a594bbcc370e](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/1956fdcfb64f4a94a7d9a594bbcc370e) |

- 원본 실행: Middle `20261017-142751-994x8noq`, Senior `20261017-143246-h69dfxub`.
- 전후 기록·코드: `.archgen/m7-followup/render-tuning/`.
- 실제 MD·사용량: `.archgen/m7-followup/rubric-recheck/`.
- 코드 변경은 현재 미커밋이며 원본 생성 파일과 골든셋은 변경하지 않았다.

## 면접용으로 설명할 수 있는 범위

평가에서 발견된 추상적 요구 수준의 원인을 따라가 데이터 생성이 아니라 출력 과정의 정성 목표 유실을 확인했다. 렌더러·후단 검사를 수정하고 동일한 두 Uber 실행·같은 모델과 기준으로 각 2회 전후 평가하여 관측 평균 98.75% → 100%를 확인했다. 한 주제 두 실행의 작은 사례 분석이며 사람 정답 기반 정확도나 일반화 성능은 검증하지 않았다.


## M7 새 기준선의 공통 Rubric 품질 검사 — 2026-10-19

기존 Uber 두 실행의 저장 export를 현재 renderer로 출력한 뒤 기존 `rubric.md` 품질 기준·Sol high로 각각 1회 평가했다. 생성 프롬프트 변경이나 새 생성 실험은 아니다.

| 대상 | Pass | Fail | 판단 불가 | 통과율 | Trace |
| --- | --- | --- | --- | --- | --- |
| middle | 40 | 0 | 0 | 100.0% | [Trace](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/12cf3dd70a9d4d288d4b0ae0621eaa22) |
| senior | 40 | 0 | 0 | 100.0% | [Trace](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/1cca1bf2b2eb4f3eb9dd7881029a152f) |

저장 원본은 변경하지 않았다. 이 결과는 골든 참고 비교와 별개이며 1회 결과로 일반화하지 않는다. 실행 자료는 `current-criteria-20261019/baseline/{middle,senior}/rubric.json`이다.


## M7 골든 비교 기능의 실제 검증 — 2026-10-19

기존 Uber 생성물 두 개를 사용자 `resources/golden/uber/v3/`의 같은 연차 참조와 비교했다. **새 프롬프트 최종 검증이 아니라 저장 산출물로 비교 기능을 확인한 실행**이다. 앞 절의 품질 점수는 그대로 재사용하여 중복 호출하지 않았다. 단위가 다른 두 점수를 합산하지 않는다.

| 대상 | 기존 품질 | 핵심 NFR 1-1 | 핵심 역량 2-1 | Level 동등성 3-1 | 판단 불가 / 미대응 | 비교 Trace |
| --- | --- | --- | --- | --- | --- | --- |
| middle | 100.0% | 100.0% | 100.0% | 25.0% | 0 / 0 | [Trace](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/920fa1d3209544b5b30a5030dd5b109e) |
| senior | 100.0% | 100.0% | 100.0% | 0.0% | 0 / 0 | [Trace](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/894338bb0b714d1bb8177bd2b88c7c18) |

Middle의 차이: C1은 기본 타임아웃보다 경합 안전성을 깊게 요구하고, C3에 대응하는 생성 C2는 골든 3점의 중복 효과 방지를 2점부터 요구한다. C4는 3점에서 적체·작업 분담 개선으로 충족할 수 있어 골든의 불필요한 전송 원천 감축을 반드시 평가하지 않는다. 실제 대응 ID·양쪽 문구·차이 Level은 `golden-smoke/{middle,senior}/result.json`에 보존했다.

이는 “자체적으로 타당한가”와 “참조와 같은 점수 수준인가”가 별개의 평가라는 관측이다. 모든 Level 차이가 생성물의 기술 오류라는 뜻은 아니며, 사람 검토 전에는 잠정 판정이다. 이번 Research 검색 프롬프트를 이 점수에 맞춰 추가 수정하지 않았다. 사용자 골든은 변경하지 않았다. 다른 두 주제의 골든과 미사용 검증 주제 생성·반복 평가는 아직 없어 일반화 성능을 주장하지 않는다.

Senior의 차이도 기술명 누락이 아닌 평가 조건의 차이였다. C1은 예약 확보·만료 해제의 시점, C2는 최신성과 쓰기 부하의 상충 대응, C3은 3점의 멱등성 보장 범위·비용, C4는 입력 발생량과 정확도를 함께 제어하는 정책이 참조와 달랐다. 비교기는 C1→생성 C1·C2, C2→생성 C3·C4처럼 일대다 대응도 기록했다.
