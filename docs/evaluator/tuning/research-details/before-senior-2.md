# 수정 전 Senior 2회 평가 상세

새로 생성한 Research 결과를 평가한 실행이다.

[주요 실험 기록](../research-tuning.md) · [원본 JSON](../../../../.archgen/m7-followup/current-criteria-20261019/research-tuning/before/senior/2-evaluation/research.json) · [당시 평가 기준](../../../../.archgen/m7-followup/current-criteria-20261019/research-tuning/before/senior/2-evaluation/research-criteria.md) · [Trace](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/efed034b5caa4a1ebbe4d58109d2630c)

전체 158건: Pass 77 · Fail 69 · 판단 불가 12. 아래 표에는 모든 Fail과 판단 불가를 생략 없이 기록했다. Pass도 기준별 개수를 표시하며 개별 근거는 원본 JSON에 보존한다.

## 기준별 전체 집계

| 평가 기준 | Pass | Fail | 판단 불가 |
| --- | --- | --- | --- |
| 1-1 평가 초점 반영 | 1 | 0 | 0 |
| 1-2 후보 도출의 타당성 | 5 | 0 | 0 |
| 2-1 후보 검증에 적합한 쿼리 | 5 | 0 | 0 |
| 3-1 검색 결과의 관련성 | 9 | 2 | 0 |
| 4-1 출처 선정의 타당성 | 17 | 50 | 0 |
| 5-1 본문 수집의 유효성 | 38 | 17 | 12 |
| 6-1 핵심 평가 초점의 근거 확보 | 1 | 0 | 0 |
| 6-2 Research 판단과 수집 근거의 일치 | 1 | 0 | 0 |

## 3-1 검색 결과의 관련성

### 당시 문서에 명시된 판정 기준

- Pass: 반환된 결과에 검색 쿼리의 설계 문제와 연결되는 문서 후보가 있어 후속 본문 확인 대상으로 검토할 수 있다.
- Fail: 결과가 일반 소개·광고·다른 주제에 치우쳐 후보 검증에 사용할 문서 후보가 없는데도 검색을 충분한 근거 탐색으로 취급한다.

검색 서비스 오류는 별도로 기록한다. 검색 결과에 나온 제목·요약만으로 기술적 주장이 사실이라고 판정하지 않는다.

### 모든 Fail과 판단 불가 원문

| 번호 | 평가 대상 | 판정 | 실제 적용한 기준 원문 | 판단 근거 원문 |
| --- | --- | --- | --- | --- |
| 1 | call_R02ccl7PuDBcIfHcdOa1fOBM | Fail | 반환 결과에 해당 품질 문제를 검증할 적절한 문서 후보가 없다. | query-3의 중복 배정·동시성 문제에 대해 결과는 행사 소개와 기술 블로그 목록·동일 경로 변형에 치우쳤다. 1위 https://www.uber.com/blog/uber-technology-day의 대응 문서 doc-8d9d22546edf4213b7a163d96e98ad57도 문장 9–29에서 발표를 소개할 뿐 배정 경합을 설명하지 않는다. 이후 재검색 수행과는 구분한 해당 호출의 판정이다. |
| 2 | call_kHAO6nw3TzxirSk6brfOsD8p | Fail | 반환 결과가 다른 주제에 치우쳐 후보 검증용 문서 후보가 없다. | query-4의 추가 검색 결과는 면허 승인, 화물 고객 사례·제휴, 재무 안내로 구성된다. 예를 들어 2위 https://www.uber.com/blog/rural-king-uber-freight-customer-story의 doc-a3b87a5303844af282d980de0c34d39e 문장 7–16은 화물 조달 사례다. 위치 업데이트 수집 처리량을 조사할 기술 후보가 없다. |

## 4-1 출처 선정의 타당성

### 당시 문서에 명시된 판정 기준

- Pass: 검색 결과 중 설계 범위와 후보 검증에 관련되고 게시 주체를 식별할 수 있는 문서를 선택한다. 동일 내용의 중복 URL이나 근거가 부족한 목록·홍보 페이지를 불필요하게 우선하지 않는다.
- Fail: 관련성이나 출처를 확인하지 않은 채 무관한·중복된·본문 근거가 없는 문서를 선택하고, 검색 결과에 있던 더 적절한 출처를 뚜렷한 이유 없이 제외한다.

공식 출처가 아니라는 이유만으로 Fail하지 않는다. 이 평가는 저장된 검색 결과에서 실제 선택 가능한 문서를 기준으로 한다.

### 모든 Fail과 판단 불가 원문

| 번호 | 평가 대상 | 판정 | 실제 적용한 기준 원문 | 판단 근거 원문 |
| --- | --- | --- | --- | --- |
| 1 | doc-8d9d22546edf4213b7a163d96e98ad57 | Fail | 구체적 기술 출처보다 근거가 약한 행사 소개를 불필요하게 선택했다. | doc-8d9d22546edf4213b7a163d96e98ad57, https://www.uber.com/blog/uber-technology-day, 문장 9–29는 발표 소개이며 중복 배정 제어의 본문이 아니다. 관련 기술 문서를 추가로 찾은 기록이 있지만 이 행사 페이지를 본문 수집 대상으로 우선한 이유는 없다. |
| 2 | doc-437c9347eb174650bcb68faefb6cf48e | Fail | 후보 검증용 본문이 식별되지 않는 목록 페이지를 선택했다. | doc-437c9347eb174650bcb68faefb6cf48e, https://www.uber.com/blog/engineering?id=879, 문장 0–28은 공통 메뉴뿐이다. 검색 결과도 기술 블로그 목록으로 표시되며 배정 동시성 문서라는 근거가 없다. |
| 3 | doc-a8bcff20a99f4607a9a583bffcc4c702 | Fail | 무의미한 URL 변형과 본문 근거가 없는 목록을 불필요하게 선택했다. | doc-a8bcff20a99f4607a9a583bffcc4c702의 수집 URL은 기술 블로그 경로에 비정상적으로 긴 countryiso2 매개변수가 붙은 형태다. 문장 0–28은 doc-437c9347eb174650bcb68faefb6cf48e와 같은 공통 메뉴이며, 별도 기술 문서로 선택할 근거가 없다. |
| 4 | doc-a01743cd79804dd89ec56d80b2c2531c | Fail | 무관한 매개변수 변형의 목록 페이지를 불필요하게 선택했다. | doc-a01743cd79804dd89ec56d80b2c2531c의 수집 URL은 기술 블로그 경로에 다른 주소 등이 섞인 id 매개변수를 붙인 형태다. 문장 0–28은 공통 메뉴이고, 같은 검색의 https://www.uber.com/blog/ringpop-open-source-nodejs-library가 더 직접적인 후보였다. |
| 5 | doc-3ae73bb3581346ff9611d803b5122080 | Fail | 본문 근거가 없는 중복 목록 페이지를 불필요하게 선택했다. | doc-3ae73bb3581346ff9611d803b5122080, https://www.uber.com/blog/engineering?id=72, 문장 0–28은 다른 기술 블로그 매개변수 URL과 같은 메뉴다. 지역 분할·부하 편중을 검증할 별도 문서가 아니다. |
| 6 | doc-42000a57dc004daf9a06b04f1619c734 | Fail | 후보 검증용 본문이 없는 일반 목록을 불필요하게 선택했다. | doc-42000a57dc004daf9a06b04f1619c734, https://www.uber.com/blog?userId=_msv%2B_31_66466374232242242422434222344320233, 문장 0–28은 공통 메뉴다. 같은 검색에 내구성 큐 기술 문서가 있었으며 이 URL의 별도 관련성은 확인되지 않는다. |
| 7 | doc-fb45b9cda15748f3aee089c24eff71d0 | Fail | 범위 밖 자료를 더 직접적인 출처와의 구분·선정 이유 없이 선택했다. | doc-fb45b9cda15748f3aee089c24eff71d0, https://www.uber.com/blog/payments-platform, 문장 4·9–21은 결제 처리와 발표 소개다. 결제는 제외 범위이고 같은 검색에 Cherami가 있었다. 배차에 적용할 비교 목적이나 선정 이유는 저장되어 있지 않다. |
| 8 | doc-a778d87e10c34a0ab718a0169087d10d | Fail | 본문 근거가 없는 중복 목록 페이지를 불필요하게 선택했다. | doc-a778d87e10c34a0ab718a0169087d10d, https://www.uber.com/blog/engineering?uber_client_name=706, 문장 0–28은 공통 메뉴다. 배정 동시성에 관한 문서로 식별할 근거가 없다. |
| 9 | doc-46384179f7ca4382af2530d0353c33e7 | Fail | 본문 근거가 없는 중복 목록 페이지를 불필요하게 선택했다. | doc-46384179f7ca4382af2530d0353c33e7, https://www.uber.com/blog/engineering?id=x, 문장 0–28은 기존 목록 URL과 같은 메뉴다. 별도 기술 본문이라는 검색 정보가 없다. |
| 10 | doc-de83c66573a846b59671fca68ff68a2b | Fail | 본문 근거가 없는 중복 목록 페이지를 불필요하게 선택했다. | doc-de83c66573a846b59671fca68ff68a2b, https://www.uber.com/blog/engineering?id=998638, 문장 0–28은 공통 메뉴다. 호출 배정의 일관성을 확인할 수 있는 문서로 선정한 근거가 없다. |
| 11 | doc-f1f046ee354b4bfbb198f6225ef5e9bc | Fail | 관련 기술 문서 대신 근거가 약한 목록 페이지를 선택했다. | doc-f1f046ee354b4bfbb198f6225ef5e9bc, https://www.uber.com/blog/engineering/page/3, 문장 0–27은 분류·날짜 목록이다. query-4 결과의 구체적인 수집 처리 기술 문서와 달리 위치 갱신 처리량을 확인할 본문이 없다. |
| 12 | doc-aee98b8158bc43f49c0fdd585c6a76ff | Fail | 관련 기술 문서 대신 근거가 약한 목록 페이지를 선택했다. | doc-aee98b8158bc43f49c0fdd585c6a76ff, https://www.uber.com/blog/engineering/backend, 문장 0–21은 분류·날짜 목록이다. 백엔드라는 분류만으로 위치 갱신 처리량 후보를 검증할 수 없다. |
| 13 | doc-cfc78d3039f44087ad1d0756faff5754 | Fail | 관련 기술 문서 대신 근거가 약한 목록 페이지를 선택했다. | doc-cfc78d3039f44087ad1d0756faff5754, https://www.uber.com/blog/engineering/page/2, 문장 0–27은 분류·날짜 목록이다. 같은 검색의 스트림 수집 기술 문서보다 이 페이지를 수집할 별도 이유가 없다. |
| 14 | doc-2d48edf3cbf04e9d854041d974ffab73 | Fail | 관련 기술 문서 대신 본문 근거가 없는 목록을 선택했다. | doc-2d48edf3cbf04e9d854041d974ffab73, https://uber.com/blog/engineering/page/23, 문장 0–28은 공통 메뉴다. 같은 검색의 Ringpop 문서와 달리 지역 분산의 기술적 설명을 식별할 수 없다. |
| 15 | doc-1882dbc9e23f4bca89dfca493648fcc8 | Fail | 범위 밖 행사 소개를 더 적절한 기술 출처와의 구분 없이 선택했다. | doc-1882dbc9e23f4bca89dfca493648fcc8, https://www.uber.com/blog/moneycon, 문장 6–25는 결제·금융 기술 행사와 발표 소개다. 같은 검색에 내구성 큐·트리거 기술 문서가 있었으며, 호출 재처리 검증을 위한 별도 선정 이유가 없다. |
| 16 | doc-f449bed5774e4476ac77ea4871a30434 | Fail | 후보 검증용 본문이 없는 목록을 불필요하게 선택했다. | doc-f449bed5774e4476ac77ea4871a30434, https://www.uber.com/blog/engineering/page/34, 문장 0–28은 공통 메뉴다. query-2에 공간 검색 기술 문서가 있었는데도 이 목록을 수집한 별도 이유가 없다. |
| 17 | doc-7535f00dff3f4dea8d603058507805ab | Fail | 본문 근거가 없는 중복 목록 페이지를 불필요하게 선택했다. | doc-7535f00dff3f4dea8d603058507805ab, http://uber.com/blog/engineering, 문장 0–28은 다른 기술 블로그 목록 변형과 같은 메뉴다. 배정 동시성에 관한 별도 본문이 식별되지 않는다. |
| 18 | doc-130273f83b084f9eb0f8cc38dd4bfab6 | Fail | 본문 근거가 없는 중복 목록 페이지를 불필요하게 선택했다. | doc-130273f83b084f9eb0f8cc38dd4bfab6, https://www.uber.com/blog/engineering?id=26, 문장 0–28은 공통 메뉴다. 매개변수가 다르다는 점 외에 별도 기술 출처로 볼 근거가 없다. |
| 19 | doc-abefb6b534a74cb295819162e9d8ea33 | Fail | 후보 검증용 본문이 없는 목록을 불필요하게 선택했다. | doc-abefb6b534a74cb295819162e9d8ea33, https://www.uber.com/blog/engineering/page/5, 문장 0–21은 분류·날짜 목록이다. 운전자 중복 배정 방지에 관한 기술 문서로 식별되지 않는다. |
| 20 | doc-f5f8e8a198af431abec8e3227dfa557a | Fail | 본문 근거가 없는 지역별 목록을 불필요하게 선택했다. | doc-f5f8e8a198af431abec8e3227dfa557a, https://www.uber.com/blog/new-york/engineering, 문장 0–28은 공통 메뉴다. 위치 갱신 처리량에 관련된 별도 기술 내용이 식별되지 않는다. |
| 21 | doc-ffa0ca9dc25045028430fd8db431af6e | Fail | 동일 본문의 중복 URL을 별도 수집 대상으로 불필요하게 선택했다. | doc-ffa0ca9dc25045028430fd8db431af6e, https://www.uber.com/blog/building-ubers-fulfillment-platform?ref=highscalability.com, 문장 0–91은 doc-24150fe4c0594a26a74db28af0210371과 동일하다. 검색 결과에서도 제목·경로가 같고 추가 수집 이유가 없다. |
| 22 | doc-fde18b5f8b0e4979b35b725feb299146 | Fail | 동일 본문의 중복 URL을 별도 수집 대상으로 불필요하게 선택했다. | doc-fde18b5f8b0e4979b35b725feb299146, http://uber.com/blog/h3, 문장 0–110은 doc-06dafc110df84b31abc70d89b786b95d와 동일하다. 프로토콜·호스트 표기 차이 외에 추가 근거를 얻을 이유가 없다. |
| 23 | doc-cdb395ecf48d47a58533c5922793327f | Fail | 실시간 매칭 경로와의 연결 없이 다른 처리 맥락의 문서를 선택했다. | doc-cdb395ecf48d47a58533c5922793327f, https://www.uber.com/blog/pinot-for-low-latency, 문장 7·15–26·29–46은 오프라인 분석 테이블 수집을 다룬다. 같은 검색의 H3보다 주변 운전자 검색과의 연결이 약하며 별도 선정 이유가 없다. |
| 24 | doc-42a9ad73182f4044b84d2766036ac8f9 | Fail | 범위 밖 자료의 적용 관계를 설명하지 않고 더 직접적인 출처와 함께 선택했다. | doc-42a9ad73182f4044b84d2766036ac8f9, https://www.uber.com/blog/money-scale-strong-data, 문장 9–10·44–56은 결제·계정 변경의 일관성이다. 비교 후보로 검토할 수는 있지만 배정 불변식에 대한 적용 설명이 없고, 저장된 검색에는 직접적인 이행 플랫폼 문서도 있었다. |
| 25 | doc-a14021bfba93462d88aa22020cd2db2f | Fail | 범위 밖 문서의 동일 본문 중복 URL을 불필요하게 선택했다. | doc-a14021bfba93462d88aa22020cd2db2f, https://www.uber.com/blog/money-scale-strong-data?ref=highscalability.com, 문장 0–125는 doc-42a9ad73182f4044b84d2766036ac8f9와 동일하다. 결제 맥락의 적용 설명도, 참조 매개변수 URL을 추가 수집할 이유도 없다. |
| 26 | doc-1db4c294de64413d808ab3a9e2e600f9 | Fail | 설계 대상 동작을 다루지 않는 API 소개를 선택했다. | doc-1db4c294de64413d808ab3a9e2e600f9, https://www.uber.com/blog/driver-api, 문장 12–15는 운전자 프로필·이력·지급 조회다. 배정 경쟁 제어·위치 갱신 경로의 기술 근거가 아니며 별도 선정 이유가 없다. |
| 27 | doc-a3b87a5303844af282d980de0c34d39e | Fail | 후보 검증과 무관한 고객 홍보 사례를 선택했다. | doc-a3b87a5303844af282d980de0c34d39e, https://www.uber.com/blog/rural-king-uber-freight-customer-story, 문장 7–23은 화물 운송 용량 조달·가격 통제 사례다. 운전자 위치 갱신의 수집 처리량과 연결되는 기술 내용이 없다. |
| 28 | doc-2786de66134b455d8e97111e4dd87ee5 | Fail | 후보 검증과 무관한 사업·고객 관계 소개를 선택했다. | doc-2786de66134b455d8e97111e4dd87ee5, https://www.uber.com/blog/how-uber-freight-builds-customer-relationships, 문장 13–39는 고객 신뢰·화물 가격·영업 사례다. 실시간 운전자 위치 처리 구조를 확인할 출처가 아니다. |
| 29 | doc-119da02dfe96471f8c9a4dcf0bc9cc83 | Fail | 동일 본문의 중복 URL을 별도 수집 대상으로 불필요하게 선택했다. | doc-119da02dfe96471f8c9a4dcf0bc9cc83, https://www.uber.com/blog/gairos-scalability, 문장 0–112는 앞서 수집된 doc-57a0c2f720e945aeae158f92a7d4f0bd와 동일하다. 대표 URL로 통합할 수 있었으며 별도 수집 이유가 없다. |
| 30 | doc-baf9941f0286473fb20ded48cf74e7db | Fail | 구체적 시스템 근거보다 조직·채용 소개를 불필요하게 선택했다. | doc-baf9941f0286473fb20ded48cf74e7db, https://www.uber.com/blog/bangalore-engineering, 문장 4–10·63–64는 팀 업무와 채용 소개다. 같은 결과의 공간 플랫폼·게이트웨이 기술 문서보다 지역 매칭 부하 분산 검증에 부적절하다. |
| 31 | doc-6874c558f76e4b4f9467e0c912bf3cef | Fail | 설계 대상 경로와의 연결 없이 분석 저장소 자료를 선택했다. | doc-6874c558f76e4b4f9467e0c912bf3cef, https://www.uber.com/blog/uber-big-data-platform, 문장 3·47–65·69–79는 분석 데이터레이크·배치 모델링을 다룬다. 주변 운전자 검색 경로와의 적용 관계가 없고 같은 검색에 H3가 있었다. |
| 32 | doc-386e76c415f1405897f012799dfcc241 | Fail | 후보 검증과의 연결이 설명되지 않은 다른 저장 맥락의 자료를 선택했다. | doc-386e76c415f1405897f012799dfcc241, https://www.uber.com/blog/jellyfish-cost-effective-data-tiering, 문장 9–11·28–40·57–69는 오래된 데이터의 압축·계층 저장이다. 순간적인 위치 상태·주변 검색·호출 재처리와 연결한 선정 이유가 없다. |
| 33 | doc-0845ed844a13497fa5b99e9b540f760e | Fail | 제외 범위의 사용자 화면 기능을 별도 적용 설명 없이 선택했다. | doc-0845ed844a13497fa5b99e9b540f760e, https://www.uber.com/blog/real-time-earnings-tracker, 문장 6–9·18–35는 수입 표시와 화면 데이터 정합성이다. 운전자 중복 배정이나 주변 검색 지연의 기술 출처로 선택할 연결 근거가 없다. |
| 34 | doc-01184f015b3c45a9aebb03aba52aa14d | Fail | 기능상 연관성만 있는 모바일 확장 구조를 시스템 후보 근거로 선택했다. | doc-01184f015b3c45a9aebb03aba52aa14d, https://www.uber.com/blog/carbon-driver-app-preferences-ribs, 문장 16–18·28–35·60–74는 설정 화면의 플러그인·코드 격리다. 배정 경쟁 제어나 서버 처리 규모를 조사할 선정 이유가 없다. |
| 35 | doc-da6c9affff2c46829c1e9e0646eb3d5c | Fail | 후보 검증과 무관한 상품 기능 소개를 선택했다. | doc-da6c9affff2c46829c1e9e0646eb3d5c, https://www.uber.com/blog/uber-freight-helps-keep-freight-fresh-with-reefer-upgrades, 문장 5–9는 냉장 화물의 예약 정보 개선이다. 위치 업데이트 수집 처리량과 관련된 시스템 설명이 없다. |
| 36 | doc-c889f7b1187b430b85ec5d6817d5eb3a | Fail | 후보 검증과 무관한 사업 제휴 소개를 선택했다. | doc-c889f7b1187b430b85ec5d6817d5eb3a, https://www.uber.com/blog/uber-freight-and-waymo-via-partnership, 문장 0–9는 자율주행 화물 제휴 계획이다. 대규모 위치 업데이트 수집 구조나 처리 한계의 근거가 아니다. |
| 37 | doc-d1c220ace27e44768344d8950eb0a4f0 | Fail | 공간 데이터라는 단어만 연관되는 다른 시스템 자료를 선택했다. | doc-d1c220ace27e44768344d8950eb0a4f0, https://www.uber.com/blog/nebulagl, 문장 4–12·25–29는 브라우저 지도 도형 편집·렌더링이다. 서버의 운전자 검색·위치 갱신·지역 부하 분산과 다르며 선정 연결 근거가 없다. |
| 38 | doc-f422ade32d71465d9c26d605b77dfef5 | Fail | 제외 범위 자료를 더 관련된 출처와의 구분·적용 설명 없이 선택했다. | doc-f422ade32d71465d9c26d605b77dfef5, https://www.uber.com/blog/driver-app-cash-payments, 문장 16–36·42–47은 현금 정산과 오프라인 운행 진행이다. 요청 재시도 설명은 있으나 배정 확정의 안전성과 구분한 적용 설명이 없고 같은 결과에 게이트웨이 기술 문서가 있었다. |
| 39 | doc-f8cf04d0f8104a989c1a436792de9abf | Fail | 후보 검증과의 연결이 설명되지 않은 다른 기술 주제의 자료를 선택했다. | doc-f8cf04d0f8104a989c1a436792de9abf, https://www.uber.com/blog/michelangelo-machine-learning-model-representation, 문장 4–5·29–45는 모델 직렬화·표현·추론 호환성이다. 공간 인덱스나 매칭 호출 경로를 다루지 않으며 같은 검색에 H3가 있었다. |
| 40 | fetch:https://www.uber.com/blog/research/engineering/page/2 | Fail | 구체적 기술 출처가 있는데도 본문 근거가 약한 목록을 불필요하게 선택했다. | https://www.uber.com/blog/research/engineering/page/2는 query-1 결과 3위의 기술 블로그 목록이다. 같은 결과에 doc-10957f7033ec4588b667799c183741a3의 위치 기술 문서가 있었고 목록 우선 수집 이유가 없다. 404로 해당 본문 문장은 없다. |
| 41 | fetch:https://www.uber.com/blog/search/data+analytics/page/5 | Fail | 직접적인 기술 문서 대신 근거가 약한 검색 목록을 선택했다. | https://www.uber.com/blog/search/data+analytics/page/5는 query-2 결과 3위의 검색 목록이다. 같은 결과의 공간 검색 기술 문서 두 건보다 별도 본문 근거가 약하며 선정 이유가 없다. 404로 문서 ID·문장 번호는 없다. |
| 42 | fetch:https://www.uber.com/blog/research | Fail | 관련 기술 문서 대신 일반 목록을 불필요하게 선택했다. | https://www.uber.com/blog/research는 query-4 결과 1위의 일반 기술 목록이다. 같은 결과에 스트림 수집 기술 문서가 있었으나 목록을 본문 대상으로 선택할 설명이 없다. 404로 문서 ID·본문 문장은 없다. |
| 43 | fetch:https://eng.uber.com/blog/apache-hudi-at-uber | Fail | 설계 대상 경로와의 연결이 없는 분석 저장소 문서를 선택했다. | https://eng.uber.com/blog/apache-hudi-at-uber는 query-4 결과 2위에서 데이터레이크 운영 문서로 표시된다. 실시간 운전자 위치 반영 경로와의 적용 설명 없이 선택되었다. 404로 본문·문장 번호는 없으며 판정은 검색상 주제와 선정 근거에 한정한다. |
| 44 | fetch:http://eng.uber.com/blog/apache-hudi-at-uber | Fail | 동일 출처의 중복 URL을 별도 수집 대상으로 불필요하게 선택했다. | http://eng.uber.com/blog/apache-hudi-at-uber는 같은 검색의 HTTPS 결과와 제목·경로가 같다. 실패 기록도 동일 HTTPS 주소로의 요청을 나타낸다. 추가 수집 이유가 없고 404로 문서 ID·본문 문장은 없다. |
| 45 | fetch:https://www.uber.com/blog/search/pinot | Fail | 직접적인 기술 문서 대신 근거가 약한 검색 목록을 선택했다. | https://www.uber.com/blog/search/pinot는 query-2 결과 4위의 검색 목록이다. 같은 결과에 실제 공간 검색 기술 문서가 있었으므로 이 목록을 본문 수집 대상으로 삼을 필요성이 확인되지 않는다. 404로 문서 ID·본문 문장은 없다. |
| 46 | fetch:https://www.uber.com/blog/search/data+analytics | Fail | 직접적인 기술 문서 대신 근거가 약한 검색 목록을 선택했다. | https://www.uber.com/blog/search/data+analytics는 query-2 결과 5위의 일반 검색 목록이다. 주변 운전자 검색 지연을 검증할 별도 기술 본문이 식별되지 않으며, 더 직접적인 결과가 있었다. 404로 문장 번호는 없다. |
| 47 | fetch:https://www.uber.com/blog/search/data+analytics/page/2 | Fail | 근거가 약한 검색 목록의 추가 페이지를 불필요하게 선택했다. | https://www.uber.com/blog/search/data+analytics/page/2는 query-2 결과 6위의 목록이다. 같은 검색에서 선택 가능한 공간 검색 기술 문서와 달리 후보 검증용 본문이 확인되지 않는다. 404로 문서 ID·문장 번호는 없다. |
| 48 | fetch:https://www.uber.com/blog/research/driver-surge-pricing | Fail | 명시적으로 제외된 주제의 출처를 적용 설명 없이 선택했다. | https://www.uber.com/blog/research/driver-surge-pricing는 query-2 결과 7위에서 운전자 할증 가격 주제로 표시된다. 요금 계산은 제외 범위이며 주변 검색 지연과의 연결 설명이 없다. 404로 문서 ID·본문 문장은 없다. |
| 49 | fetch:https://www.uber.com/blog/puc-approves-two-year-license | Fail | 후보 검증과 무관한 정책 안내를 선택했다. | https://www.uber.com/blog/puc-approves-two-year-license는 query-4 추가 검색의 1위로 면허 승인 안내다. 운전자 위치 업데이트 처리량과 연결되는 기술 문서가 아니다. 404로 문서 ID·본문 문장은 없다. |
| 50 | fetch:https://www.uber.com/blog/update-covid-19-financial?id=9611 | Fail | 후보 검증 관련성을 확인하지 않은 무관한 안내를 선택했다. | https://www.uber.com/blog/update-covid-19-financial?id=9611는 query-4 추가 검색의 4위로 재무 안내 경로이며, 위치 갱신 수집·처리와 연결할 검색 정보가 없다. 404로 문서 ID·본문 문장은 없다. |

## 5-1 본문 수집의 유효성

### 당시 문서에 명시된 판정 기준

- Pass: 선택한 문서의 실제 본문을 정상적으로 수집하여 후속 근거 확인에 사용할 수 있다.
- Fail: 본문 대신 검색 요약이나 다른 문서 내용을 수집하고 정상적인 본문으로 처리한다.

판단 불가/실행 오류: 접근 차단·타임아웃 등으로 본문 수집에 실패한 경우는 별도로 기록한다.

### 모든 Fail과 판단 불가 원문

| 번호 | 평가 대상 | 판정 | 실제 적용한 기준 원문 | 판단 근거 원문 |
| --- | --- | --- | --- | --- |
| 1 | doc-437c9347eb174650bcb68faefb6cf48e | Fail | 공통 메뉴만 수집되어 후속 기술 근거로 사용할 실제 본문이 없다. | doc-437c9347eb174650bcb68faefb6cf48e, https://www.uber.com/blog/engineering?id=879, 문장 0–28은 광고·서비스 분류·블로그 메뉴뿐이다. 수집 문서로 저장됐지만 조사에 사용할 기사 본문은 확보되지 않았다. |
| 2 | doc-a8bcff20a99f4607a9a583bffcc4c702 | Fail | 공통 메뉴만 수집되어 후속 기술 근거로 사용할 실제 본문이 없다. | doc-a8bcff20a99f4607a9a583bffcc4c702의 수집 URL은 countryiso2 매개변수가 붙은 기술 블로그 경로다. 문장 0–28은 다른 목록 변형과 동일한 공통 메뉴이며 기사 본문이 아니다. 접근 오류 기록과는 구분된다. |
| 3 | doc-a01743cd79804dd89ec56d80b2c2531c | Fail | 공통 메뉴만 수집되어 후속 기술 근거로 사용할 실제 본문이 없다. | doc-a01743cd79804dd89ec56d80b2c2531c의 수집 URL은 여러 주소가 섞인 id 매개변수의 기술 블로그 경로다. 문장 0–28은 공통 메뉴뿐이며 특정 기술 문서의 본문이 확보되지 않았다. |
| 4 | doc-3ae73bb3581346ff9611d803b5122080 | Fail | 공통 메뉴만 수집되어 후속 기술 근거로 사용할 실제 본문이 없다. | doc-3ae73bb3581346ff9611d803b5122080, https://www.uber.com/blog/engineering?id=72, 문장 0–28은 서비스·블로그 분류 메뉴다. 문서 항목으로 저장되었으나 기술 본문은 없다. |
| 5 | doc-42000a57dc004daf9a06b04f1619c734 | Fail | 공통 메뉴만 수집되어 후속 기술 근거로 사용할 실제 본문이 없다. | doc-42000a57dc004daf9a06b04f1619c734, https://www.uber.com/blog?userId=_msv%2B_31_66466374232242242422434222344320233, 문장 0–28은 공통 메뉴다. 특정 기사나 후보 검증용 기술 본문이 수집되지 않았다. |
| 6 | doc-a778d87e10c34a0ab718a0169087d10d | Fail | 공통 메뉴만 수집되어 후속 기술 근거로 사용할 실제 본문이 없다. | doc-a778d87e10c34a0ab718a0169087d10d, https://www.uber.com/blog/engineering?uber_client_name=706, 문장 0–28은 공통 메뉴다. 기술 기사 본문 대신 탐색 요소만 저장되었다. |
| 7 | doc-46384179f7ca4382af2530d0353c33e7 | Fail | 공통 메뉴만 수집되어 후속 기술 근거로 사용할 실제 본문이 없다. | doc-46384179f7ca4382af2530d0353c33e7, https://www.uber.com/blog/engineering?id=x, 문장 0–28은 광고·서비스 분류 메뉴다. 후속 후보 검증에 사용할 기사 내용은 없다. |
| 8 | doc-de83c66573a846b59671fca68ff68a2b | Fail | 공통 메뉴만 수집되어 후속 기술 근거로 사용할 실제 본문이 없다. | doc-de83c66573a846b59671fca68ff68a2b, https://www.uber.com/blog/engineering?id=998638, 문장 0–28은 다른 목록 변형과 같은 메뉴다. 기술 본문 수집으로 볼 수 없다. |
| 9 | doc-f1f046ee354b4bfbb198f6225ef5e9bc | Fail | 분류·날짜 목록만 수집되어 기술 본문 근거가 없다. | doc-f1f046ee354b4bfbb198f6225ef5e9bc, https://www.uber.com/blog/engineering/page/3, 문장 0–27은 기사 수·분류·날짜뿐이다. 본문 수집 항목으로 저장되었지만 실제 기술 설명이 없다. |
| 10 | doc-aee98b8158bc43f49c0fdd585c6a76ff | Fail | 분류·날짜 목록만 수집되어 기술 본문 근거가 없다. | doc-aee98b8158bc43f49c0fdd585c6a76ff, https://www.uber.com/blog/engineering/backend, 문장 0–21은 목록 분류와 날짜다. 후보 검증에 사용할 본문은 확보되지 않았다. |
| 11 | doc-cfc78d3039f44087ad1d0756faff5754 | Fail | 분류·날짜 목록만 수집되어 기술 본문 근거가 없다. | doc-cfc78d3039f44087ad1d0756faff5754, https://www.uber.com/blog/engineering/page/2, 문장 0–27은 목록 메타정보뿐이다. 구체적인 기사 본문을 수집한 결과가 아니다. |
| 12 | doc-2d48edf3cbf04e9d854041d974ffab73 | Fail | 공통 메뉴만 수집되어 후속 기술 근거로 사용할 실제 본문이 없다. | doc-2d48edf3cbf04e9d854041d974ffab73, https://uber.com/blog/engineering/page/23, 문장 0–28은 공통 메뉴다. 기술 기사나 유용한 상세 목록의 본문이 확보되지 않았다. |
| 13 | doc-f449bed5774e4476ac77ea4871a30434 | Fail | 공통 메뉴만 수집되어 후속 기술 근거로 사용할 실제 본문이 없다. | doc-f449bed5774e4476ac77ea4871a30434, https://www.uber.com/blog/engineering/page/34, 문장 0–28은 공통 메뉴다. 공간 검색 지연을 검토할 본문이 확보되지 않았다. |
| 14 | doc-7535f00dff3f4dea8d603058507805ab | Fail | 공통 메뉴만 수집되어 후속 기술 근거로 사용할 실제 본문이 없다. | doc-7535f00dff3f4dea8d603058507805ab, http://uber.com/blog/engineering, 문장 0–28은 서비스·블로그 메뉴다. 수집 문서 항목에 기사 본문이 없다. |
| 15 | doc-130273f83b084f9eb0f8cc38dd4bfab6 | Fail | 공통 메뉴만 수집되어 후속 기술 근거로 사용할 실제 본문이 없다. | doc-130273f83b084f9eb0f8cc38dd4bfab6, https://www.uber.com/blog/engineering?id=26, 문장 0–28은 다른 목록 변형과 동일한 메뉴다. 실제 기술 설명은 수집되지 않았다. |
| 16 | doc-abefb6b534a74cb295819162e9d8ea33 | Fail | 분류·날짜 목록만 수집되어 기술 본문 근거가 없다. | doc-abefb6b534a74cb295819162e9d8ea33, https://www.uber.com/blog/engineering/page/5, 문장 0–21은 목록 메타정보다. 배정 일관성의 후속 확인에 사용할 기사 본문이 없다. |
| 17 | doc-f5f8e8a198af431abec8e3227dfa557a | Fail | 공통 메뉴만 수집되어 후속 기술 근거로 사용할 실제 본문이 없다. | doc-f5f8e8a198af431abec8e3227dfa557a, https://www.uber.com/blog/new-york/engineering, 문장 0–28은 공통 메뉴다. 특정 기술 기사의 본문이 수집되지 않았다. |
| 18 | fetch:https://www.uber.com/blog/research/dynamic-pricing-and-matching-in-ride-hailing-platforms | 판단 불가 | HTTP 오류로 본문 수집에 실패한 실행 오류는 품질 판정에서 제외한다. | https://www.uber.com/blog/research/dynamic-pricing-and-matching-in-ride-hailing-platforms의 실패 기록에 1회 요청 후 지역화된 주소에서 HTTP 404가 명시되어 있다. 문서 ID·본문·문장 번호가 없어 수집 유효성을 판정할 수 없다. |
| 19 | fetch:https://www.uber.com/blog/research/engineering/page/2 | 판단 불가 | HTTP 오류로 본문 수집에 실패한 실행 오류는 품질 판정에서 제외한다. | https://www.uber.com/blog/research/engineering/page/2의 실패 기록은 1회 요청 후 HTTP 404다. 본문·문서 ID·문장 번호가 생성되지 않았으며 정상 수집으로 처리한 기록은 없다. |
| 20 | fetch:https://www.uber.com/blog/search/data+analytics/page/5 | 판단 불가 | HTTP 오류로 본문 수집에 실패한 실행 오류는 품질 판정에서 제외한다. | https://www.uber.com/blog/search/data+analytics/page/5는 실패 기록상 HTTP 404로 수집되지 않았다. 문서 ID·본문 문장과 유효한 수집 결과가 없어 판단 불가다. |
| 21 | fetch:https://www.uber.com/blog/research | 판단 불가 | HTTP 오류로 본문 수집에 실패한 실행 오류는 품질 판정에서 제외한다. | https://www.uber.com/blog/research는 1회 요청 후 지역화된 주소에서 HTTP 404가 발생했다. 문서 ID·본문·문장 번호가 없으며 실행 오류로 기록한다. |
| 22 | fetch:https://eng.uber.com/blog/apache-hudi-at-uber | 판단 불가 | HTTP 오류로 본문 수집에 실패한 실행 오류는 품질 판정에서 제외한다. | https://eng.uber.com/blog/apache-hudi-at-uber의 실패 기록에 HTTP 404가 명시되어 있다. 실제 본문과 문서 ID·문장 번호가 없어 본문 수집 품질을 판정할 수 없다. |
| 23 | fetch:http://eng.uber.com/blog/apache-hudi-at-uber | 판단 불가 | HTTP 오류로 본문 수집에 실패한 실행 오류는 품질 판정에서 제외한다. | http://eng.uber.com/blog/apache-hudi-at-uber의 요청은 실패 기록상 HTTPS 주소에서 HTTP 404가 발생했다. 본문·문서 ID·문장 번호가 없으며 중복 선정 문제와 수집 실행 오류를 구분한다. |
| 24 | fetch:https://www.uber.com/blog/search/pinot | 판단 불가 | HTTP 오류로 본문 수집에 실패한 실행 오류는 품질 판정에서 제외한다. | https://www.uber.com/blog/search/pinot의 실패 기록은 1회 요청 후 HTTP 404다. 문서 ID·본문 문장이 생성되지 않아 유효한 수집 여부를 평가할 자료가 없다. |
| 25 | fetch:https://www.uber.com/blog/search/data+analytics | 판단 불가 | HTTP 오류로 본문 수집에 실패한 실행 오류는 품질 판정에서 제외한다. | https://www.uber.com/blog/search/data+analytics는 실패 기록상 지역화된 주소에서 HTTP 404가 발생했다. 본문·문서 ID·문장 번호가 없어 실행 오류로 남긴다. |
| 26 | fetch:https://www.uber.com/blog/search/data+analytics/page/2 | 판단 불가 | HTTP 오류로 본문 수집에 실패한 실행 오류는 품질 판정에서 제외한다. | https://www.uber.com/blog/search/data+analytics/page/2는 1회 요청 후 HTTP 404로 실패했다. 문서 ID·본문 문장이 없고 검색 요약을 정상 본문으로 대신 처리한 기록도 없다. |
| 27 | fetch:https://www.uber.com/blog/research/driver-surge-pricing | 판단 불가 | HTTP 오류로 본문 수집에 실패한 실행 오류는 품질 판정에서 제외한다. | https://www.uber.com/blog/research/driver-surge-pricing의 실패 기록에 HTTP 404가 명시되어 있다. 문서 ID·본문·문장 번호가 없어 수집 유효성은 판단 불가다. |
| 28 | fetch:https://www.uber.com/blog/puc-approves-two-year-license | 판단 불가 | HTTP 오류로 본문 수집에 실패한 실행 오류는 품질 판정에서 제외한다. | https://www.uber.com/blog/puc-approves-two-year-license는 실패 기록상 1회 요청 후 HTTP 404다. 본문·문서 ID·문장 번호가 없어 출처 선정의 부적절성과 별개로 실행 오류로 기록한다. |
| 29 | fetch:https://www.uber.com/blog/update-covid-19-financial?id=9611 | 판단 불가 | HTTP 오류로 본문 수집에 실패한 실행 오류는 품질 판정에서 제외한다. | https://www.uber.com/blog/update-covid-19-financial?id=9611는 지역화된 주소에서 HTTP 404로 실패했다. 문서 ID·본문·문장 번호가 없어 수집 품질 판정을 생성하지 않는다. |
