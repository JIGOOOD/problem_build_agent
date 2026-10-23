# 3-5·4-1 기대 판정

이 파일과 `expected_labels.json`은 사람/후처리용이다. 평가 LLM에 전달하지 않는다.

승인된 정상 한 쌍을 그대로 기준으로 삼았다. 오류 라벨은 이번에 작성한 기대 판정이며 아직 실제 Evaluator를 실행하지 않았다.

## 구성

| 구분 | 쌍 수 | 루브릭 수 | 직접 주입 오류 수 |
|---|---:|---:|---:|
| 승인 정상 원본 01 | 1 | 2 | 0 |
| 정상 순서·ID 변형 04 | 1 | 2 | 0 |
| 다중 오류 02·03·05·06·07·08 | 6 | 12 | 24 |
| 합계 | 8 | 16 | 24 |

정상 순서 변형은 새로운 독립 표본이 아니다. 오류 케이스마다 서로 다른 Criterion에 직접 오류 4개를 넣었다. 나머지 Level·범위·NFR·배점은 그대로다.

## 오류 유형별 개수

| 유형 | 내용 | 사례 수 | 배치 |
|---|---|---:|---|
| E01 | Level 0에 문제 인식·해결 시도 배치 | 3 | 02 C1, 05 C2, 07 C3 |
| E02 | Middle 2점에 심층 분석·기술 선택 필수화 | 3 | 02 C2, 06 C1, 08 C3 |
| E03 | Senior 1점에 미완성 제안만 배치 | 3 | 02 C3, 05 C1, 08 C4 |
| E04 | Senior 2점의 기본 흐름을 고급 어휘로 포장 | 3 | 02 C4, 06 C2, 07 C1 |
| E05 | Senior 3점에 추상적인 분석·Trade-off만 추가 | 3 | 03 C1, 05 C3, 07 C4 |
| E06 | Middle 1점에 완성된 기본 흐름 배치 | 3 | 03 C2, 06 C4, 08 C1 |
| E07 | Senior 2점에 Middle 2점 기본 흐름 그대로 배치 | 3 | 03 C3, 05 C4, 08 C2 |
| E08 | Senior 3점에 구체적 예외 대응을 추가하지만 대안 비교·선택 근거가 부족 | 3 | 03 C4, 06 C3, 07 C2 |

v4에서 E06은 동일 난이도의 기본 흐름을 다른 표현으로 재서술했다. v5에서 E08은 구체적인 상황과 단일 대응 방안을 추가했으나 대안 비교·선택 근거가 없는 오류로 변경했다. 직접 주입 개수와 기대 Pass/Fail은 유지한다.

E04와 E07은 별개의 근본 원인이라기보다, Senior 2점의 깊이 부족을 각각 어려운 어휘와 원문 복사로 표현한 변형이다.

## Criterion별 3-5와 쌍별 4-1

| 케이스 | M C1 | M C2 | M C3 | M C4 | S C1 | S C2 | S C3 | S C4 | 4-1 |
|---|---|---|---|---|---|---|---|---|---|
| 01 | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass |
| 02 | Fail | Fail | Pass | Pass | Pass | Pass | Fail | Fail | Fail |
| 03 | Pass | Fail | Pass | Pass | Fail | Pass | Fail | Fail | Fail |
| 04 | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass | Pass |
| 05 | Pass | Fail | Pass | Pass | Fail | Pass | Fail | Fail | Fail |
| 06 | Fail | Pass | Pass | Fail | Pass | Fail | Fail | Pass | Fail |
| 07 | Pass | Pass | Fail | Pass | Fail | Fail | Pass | Fail | Fail |
| 08 | Fail | Pass | Fail | Pass | Pass | Fail | Pass | Fail | Fail |

04의 대응은 M C1↔S C1, M C2↔S C2, M C3↔S C4, M C4↔S C3이다. 번호가 다르다는 사실은 Fail 근거가 아니다.

## Level별 Fail 위치

| 케이스 | 직접 변경한 Level | 같은 오류의 연쇄 영향 |
|---|---|---|
| 01 | 없음 | 없음 |
| 02 | Middle C1 L0 (E01-01) / Middle C2 L2 (E02-01) / Senior C3 L1 (E03-01) / Senior C4 L2 (E04-01) | Middle C2 L3: L2 요구 상속 (E02-01) |
| 03 | Senior C1 L3 (E05-01) / Middle C2 L1 (E06-01) / Senior C3 L2 (E07-01) / Senior C4 L3 (E08-01) | 없음 |
| 04 | 없음 | 없음 |
| 05 | Senior C1 L1 (E03-02) / Middle C2 L0 (E01-02) / Senior C3 L3 (E05-02) / Senior C4 L2 (E07-02) | 없음 |
| 06 | Middle C1 L2 (E02-02) / Senior C2 L2 (E04-02) / Senior C3 L3 (E08-02) / Middle C4 L1 (E06-02) | Middle C1 L3: L2 요구 상속 (E02-02) |
| 07 | Senior C1 L2 (E04-03) / Senior C2 L3 (E08-03) / Middle C3 L0 (E01-03) / Senior C4 L3 (E05-03) | 없음 |
| 08 | Middle C1 L1 (E06-03) / Senior C2 L2 (E07-03) / Middle C3 L2 (E02-03) / Senior C4 L1 (E03-03) | Middle C3 L3: L2 요구 상속 (E02-03) |

직접 주입은 24건이다. E02의 Middle 3점은 「2점에 더해」 때문에 과도한 2점 요구를 상속하므로 연차 적합성도 Fail을 기대한다. 이 3개 연쇄 영향은 새로운 주입 오류로 세지 않는다.

나머지 Level은 해당 연차의 조건만으로 Pass를 기대한다. 다만 직전 Level 수정으로 단계 간 연결성(별도 기준 3-2)이 달라지는 것은 별도의 연쇄 지적으로 기록한다.

## 판정을 확인하는 방식

3-5: Level마다 위치·원문·조건 위반을 확인한다. 한 Level이라도 Fail이면 Criterion은 Fail이다. 4-1: 비교 가능한 문제를 맞춘 뒤 추가로 요구되는 동작과 분석을 확인한다. 정상 두 쌍은 Pass, 오류 여섯 쌍은 Fail을 기대한다.

오류 케이스가 Fail이라는 사실만으로 4개 오류를 모두 탐지했다고 세지 않는다. 직접 주입 위치와 같은 의미의 위반이 판단 근거에 있어야 검출이다. 정상 부분을 잘못 Fail한 경우도 별도로 기록한다.

E01은 두 연차의 Level 0 차이를 요구하는 오류가 아니다. E06은 Middle 1점의 경계 오류로 3-5에서 검출해야 한다. 이 둘에 대해 별도의 4-1 Fail을 반드시 요구하지 않는다. 해당 케이스의 다른 명백한 연차 차이 오류 때문에 쌍 전체 4-1은 Fail이다.

의도하지 않은 실제 문제를 발견하면 오탐으로 단정하지 않고 기대 라벨을 검토한다. 실제 판정·실행 오류·판단 불가·누락된 평가 결과는 구분한다. null을 정답에 맞는 Pass 또는 Fail로 처리하지 않는다.

## 측정 단위

- 직접 주입 오류 검출: 오류 ID 24개를 각각 한 번씩 확인한다. 3-5와 4-1에 같은 오류가 반복돼도 중복 집계하지 않는다.
- Criterion 판정: 3-5 총 64개(기대 Pass 40, Fail 24).
- 루브릭 쌍 판정: 4-1 총 8개(기대 Pass 2, Fail 6).
- Level 판정: 총 256개. 기대 Fail은 직접 변경 24개와 E02의 상속 3개를 합한 27개다.
단위가 다르므로 하나의 정확도·총점으로 합치지 않는다. 여러 변형은 같은 주제를 공유하며 일반 성능을 입증하는 독립 표본이 아니다.

원문·변경문·기대 검출 이유는 `mutations.md`, 기계 처리용 상세 라벨은 `expected_labels.json`에 있다.
