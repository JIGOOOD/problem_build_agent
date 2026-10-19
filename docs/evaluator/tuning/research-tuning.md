# Research 튜닝 기록

## 새 기준 연결과 실제 기준선 — 2026-10-19

사용자 기준 `docs/evaluator/research.md`의 후보·쿼리·Search·Fetch·전체 결과 평가를 기존 코드에 연결했다. 원본 Uber Middle·Senior의 저장 자료를 Sol high로 각각 1회 평가했다. 이 단계는 과거 생성 결과의 진단이며 새 프롬프트 생성 성능 측정이 아니다. 판정은 사람 확인 전 잠정값이다.

검색/재검색 결과를 URL만으로 합치던 연결 문제를 코드 테스트로 재현하고 호출 ID를 보존하도록 수정했다. 이미 진행한 전체 평가 원본을 유지하고 `3-1`만 같은 기준의 올바른 검색 입력으로 별도 재평가했다. `research-verified.json`에는 두 Trace의 판정을 합쳤음을 명시했다. 이 변화는 생성 프롬프트 효과가 아니다.

| 대상 | Fetch 선별 4-1 | 본문 유효성 5-1 | 핵심 근거 6-1 | 주장 일치 6-2 | 원본 평가 |
| --- | --- | --- | --- | --- | --- |
| middle | 30.38% | 55.38% | 100.0% | 100.0% | [Trace](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/0d44655da5f648338cea714308b2bd84) |
| senior | 26.47% | 69.49% | 100.0% | 100.0% | [Trace](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/15b74527dc0849609a3e3b0b5efe48c5) |

4-1의 Pass/Fail은 Middle 24/55, Senior 18/50이었다. 실패 사유에는 서버 매칭과 무관한 앱 개발·가입 절차 글, 추적 매개변수만 다른 중복 URL, 기술 본문이 없는 목록·메뉴가 포함됐다. 연결을 보완한 3-1은 두 실행 모두 Pass 8·판단 불가 3으로, 누락된 검색 결과를 추정하여 채우지 않았다. 근거 URL·문장 번호와 별도 재평가 Trace는 실행 폴더에 남겼다.

## 프롬프트 시도 1 — 운영사 사이트 편중 완화

- 문제 근거: 두 실행에서 핵심 근거는 확보했지만 Fetch 선별·본문 유효성의 실패가 많다. 초기 쿼리는 Middle 6/6, Senior 5/6이 사이트 제한을 사용했다. 무관·중복·목록 페이지 실패 사례를 원문과 함께 보존했다.
- 가설: 주제 쿼리 외 후보 검색을 한 운영사 사이트에 몰지 않고 구체적인 동작을 검증할 개별 공식 기술 문서도 찾게 하면, 4-1·5-1이 개선되면서 6-1·6-2를 유지할 수 있다.
- 실제 변경: `initial_system.md.j2` 출처 규칙에 한 항목만 추가한다. “후보 쿼리를 모두 같은 서비스 운영사 사이트로 제한하지 않고, 구체적 동작을 검증할 개별 기술 문서·다른 운영사 기술 글도 검색한다. 목록·메뉴·채용·제품 소개 페이지를 찾는 쿼리는 피한다.”
- 고정 조건: 같은 Uber brief·카탈로그·도구 제한·코드·Sol medium 생성, 같은 새 Research 기준·Sol high 평가. Middle·Senior 수정 전후 각 2회 실제 새 조사다. 웹 결과와 Fetch 성공 변동은 남는다.
- 수정 전 원문·수정 후보 원문·diff·해시·실패 사례·가설은 실행 전 저장했다. 수정 전 새 조사 4회(연차별 2회)를 완료하고 각 원문·해시를 확인한 뒤 후보를 적용했다. 수정 전후 생성·평가 각 4회, 총 8회를 완료했다. 결과는 아래 실행별 표에 기록한다.

변경 위치: `src/archgen/research/templates/initial_system.md.j2`의 `출처` 규칙. 아래는 실제 전후 실험에 사용한 변경이다. 8회 결과를 확인한 뒤 잠정 채택했다.

**수정 전**

```text
출처
- 검색어는 한국어·영어로 작성하고 중국어 문서는 검색 대상에서 제외한다.
```

**수정 후 — 잠정 채택**

```text
출처
- 주제 쿼리 외의 후보 쿼리를 모두 같은 서비스 운영사의 사이트로 제한하지 않는다. 후보의 구체적 동작·문제를 검증할 개별 기술 문서를 찾고, 적합한 기술의 공식 문서·다른 운영사의 기술 글도 검색한다. 일반 블로그 목록·메뉴·채용·제품 소개 페이지를 찾는 쿼리는 피한다.
- 검색어는 한국어·영어로 작성하고 중국어 문서는 검색 대상에서 제외한다.
```

전체 원문은 `research-tuning/before-initial-system.md.j2`와 `candidate-initial-system.md.j2`, 변경분은 `prompt.diff`에 보존했다. 수정 전 해시는 `0b677b5f12a54366795a0ae1c7c4c5a91f4306e9f81c7f7ed5ed94dc1e17cf98`, 후보 해시는 `93a8c6b84753973048b5f9dd6b22bfad5db4cdb5078ee22ecb5a683a5a3fcff1`이다. 각 실제 실행에도 사용한 원문과 해시를 따로 저장한다.

자료: `.archgen/m7-followup/current-criteria-20261019/`의 `baseline/`, `search-link-recheck/`, `research-tuning/`. 과거 준비 문서는 `document-history/before-one-day-plan/`에 보존했다. 코드 연결 검증과 프롬프트 성능 실험은 분리한다.

수정 전 Senior 1회차 생성은 완료됐으나 평가 호출이 600초 시간 초과로 종료됐다. 생성물을 재사용하고 평가 대기 상한만 1200초로 늘려 별도 재시도하여 137 Pass·65 Fail·21 판단 불가(67.82%)로 완료했다. 실패 원본·재시도 경로를 모두 보존하며 평가 재시도를 새로운 생성 반복으로 세지 않는다.


## 수정 전후 실제 실행 결과 — 2026-10-19

동일 Uber 입력·코드·도구 제한·카탈로그·Sol medium 생성·Sol high 평가로 연차별 전후 각 2회, 총 8회 새 조사를 수행했다. 아래 값은 실행별 관측값이다. 초기 평가 시간 초과 1회는 같은 생성물을 재평가했고 새로운 생성 반복으로 세지 않았다.

| 조건 | 대상·회차 | Fetch 선별 4-1 | 본문 유효성 5-1 | 핵심 근거 6-1 / 주장 일치 6-2 | 판단 불가 수 | 최종 후보에서 빠진 초점 |
| --- | --- | --- | --- | --- | --- | --- |
| before | middle 1 | 21.21% | 62.5% | 100.0% / 100.0% | 12 | 검색 지연·중복 배정·위치 처리량 |
| before | middle 2 | 34.0% | 100.0% | 100.0% / 100.0% | 26 | 중복 배정·위치 처리량 |
| before | senior 1 | 44.21% | 85.37% | 100.0% / 100.0% | 21 | 검색 지연 |
| before | senior 2 | 25.37% | 69.09% | 100.0% / 100.0% | 12 | 검색 지연·중복 배정·위치 처리량 |
| after | middle 1 | 42.86% | 96.55% | 100.0% / 100.0% | 19 | 없음 |
| after | middle 2 | 45.76% | 96.36% | 100.0% / 100.0% | 4 | 없음 |
| after | senior 1 | 67.44% | 94.59% | 100.0% / 100.0% | 6 | 없음 |
| after | senior 2 | 51.61% | 100.0% | 100.0% / 100.0% | 4 | 검색 지연 |

6-1은 수집 본문의 근거 확보를 검사하므로 최종 후보 누락 여부와 다르다. 마지막 열은 네 핵심 초점에 대응하는 kind가 최종 후보에 남았는지 별도로 확인한 값이며 골든 충족률은 아니다.

| 조건 | 대상·회차 | 생성 LLM 호출 / 시간 / 비용 | 평가 시도 / 유효 평가 시간 | 확인된 생성+평가 비용 | 생성 Trace | 평가 Trace |
| --- | --- | --- | --- | --- | --- | --- |
| before | middle 1 | 12회 / 208.7초 / $0.4313 | 1회 / 473.6초 | $0.9958 | [Trace](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/39b31a39e6a04bd4bef680dafdcd55f6) | [Trace](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/cfd8c18159d24e32bedd7a6d729344fe) |
| before | middle 2 | 11회 / 152.2초 / $0.3547 | 1회 / 446.3초 | $0.8579 | [Trace](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/2bf6ae1b1a704cc79af7b6bb2e8f1518) | [Trace](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/5e4a184b746b408aaf8d19add4f45653) |
| before | senior 1 | 12회 / 217.7초 / $0.5744 | 2회 / 572.8초 | $0.9162 + 실패 호출 미확인 | [Trace](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/ca624c4ef99b4a3c959014100b47d6cc) | [Trace](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/059911f13fc845f9b87d0e2cd9acddd5) |
| before | senior 2 | 10회 / 159.8초 / $0.4224 | 1회 / 515.0초 | $1.0164 | [Trace](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/72f1ab0faf2c48528687886b0e0ae943) | [Trace](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/efed034b5caa4a1ebbe4d58109d2630c) |
| after | middle 1 | 12회 / 164.9초 / $0.4818 | 1회 / 530.2초 | $1.1776 | [Trace](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/a1618a502b024784b6ce405583f9a579) | [Trace](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/3f8fd5489c73408ba36a89a91da7417b) |
| after | middle 2 | 11회 / 179.1초 / $0.4937 | 1회 / 430.6초 | $1.1538 | [Trace](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/647782378dd045568eaf87b035124dae) | [Trace](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/e9cf8be100204e169d71c28dcea0d882) |
| after | senior 1 | 11회 / 163.5초 / $0.3522 | 1회 / 442.5초 | $0.8262 | [Trace](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/3aac3190c44c479288bcf97dd9f8879d) | [Trace](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/648cc8b2e8294b6bb5abe64f41189e6b) |
| after | senior 2 | 11회 / 201.8초 / $0.5425 | 1회 / 466.3초 | $1.2557 | [Trace](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/5dbae50a3d0346a8a3841209feeb8f28) | [Trace](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/a6600ad0a14d4a21b20ba1e1bee3c4ee) |

생성 호출은 LLM 호출 수이며 검색·Fetch 요청 수와 다르다. 시간은 단계별 측정값이며 병렬 전체 벽시계 시간과 다르다. 유효 평가 시간에는 최초 시간 초과 대기 시간이 포함되지 않는다. 비용은 완료 응답 사용량으로 계산한 추정이며 API 실패 호출의 미확인 과금·검색 요금을 포함하지 않는다.

| 지표 | 수정 전 4회 평균 (범위) | 수정 후 4회 평균 (범위) |
| --- | --- | --- |
| 4-1 | 31.2% (21.21~44.21%) | 51.92% (42.86~67.44%) |
| 5-1 | 79.24% (62.5~100.0%) | 96.88% (94.59~100.0%) |
| 6-1 | 100.0% (100.0~100.0%) | 100.0% (100.0~100.0%) |
| 6-2 | 100.0% (100.0~100.0%) | 100.0% (100.0~100.0%) |


## 채택 판단과 남은 문제

**한 항목을 추가한 Research 프롬프트를 잠정 채택한다.** 4회 실행의 산술평균에서 Fetch 선별은 31.20%→51.92%(+20.72%p), 본문 유효성은 79.24%→96.88%(+17.64%p)였고 핵심 근거·주장 일치는 모두 Pass를 유지했다. 최종 후보에서 빠진 핵심 초점은 9건→1건으로 줄었지만, 수정 후 Senior 2회차의 검색 지연 후보 누락은 남았다. 이를 해결 완료로 표시하지 않는다.

생성 LLM 호출은 전후 각 45회로 같았고 생성 시간의 관측 평균은 184.6초→177.3초였다. 확인된 생성+평가 비용은 수정 전 $3.7862, 수정 후 $4.4133이다. 수정 전 시간 초과 호출의 과금은 미확인이라 실제 비용 차이를 확정하지 않는다. 품질 개선에 비용이 더 들 수 있음을 함께 기록하며 비용 절감으로 표현하지 않는다.

평가 실패는 수정 전 Senior 1회차의 시간 초과 1건, 수정 후는 0건이었다. 같은 생성물 평가를 재시도한 결과도 원본 오류와 함께 보존했다. 검색·Fetch의 접근 차단·404·본문 상한 잘림은 삭제하거나 성공으로 바꾸지 않았다. Fetch 자동 일괄 선택에 따른 무관·목록·중복 URL은 여전히 남아 있어 검색 프롬프트 한 항목으로 모두 해결하지 못했다.

같은 Uber 한 주제의 두 연차에서 전후 각 2회만 관찰했다. 새 웹 검색과 수집 성공 변동, 앞뒤 순차 실행, LLM 평가의 변동이 있어 인과 효과·통계적 유의성·다른 주제에 대한 일반화 성능을 주장하지 않는다. 사람 미검토 판정은 잠정값이다. 이번에는 두 번째 프롬프트 시도를 추가하지 않았고 Keep·Selection·Rubric 생성 프롬프트는 변경하지 않았다.

전체 M7의 완료 응답 146개로 확인한 비용 추정은 $13.4067이다. 이 값에는 이번 전후 실험 외 기존 비교·기준선·회귀·골든 기능 검증도 포함된다. 응답 ID를 받지 못한 시간 초과·과거 중단 호출의 미확인 과금과 검색 요금은 제외되므로 최종 청구액으로 제시하지 않는다. 상세 사용량은 `.archgen/m7-followup/cost.json`에 보존했다.
