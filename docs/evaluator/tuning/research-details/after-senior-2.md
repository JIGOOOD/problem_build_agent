# 수정 후 Senior 2회 평가 상세

새로 생성한 Research 결과를 평가한 실행이다.

[주요 실험 기록](../research-tuning.md) · [원본 JSON](../../../../.archgen/m7-followup/current-criteria-20261019/research-tuning/after/senior/2-evaluation/research.json) · [당시 평가 기준](../../../../.archgen/m7-followup/current-criteria-20261019/research-tuning/after/senior/2-evaluation/research-criteria.md) · [Trace](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/a6600ad0a14d4a21b20ba1e1bee3c4ee)

전체 147건: Pass 113 · Fail 30 · 판단 불가 4. 아래 표에는 모든 Fail과 판단 불가를 생략 없이 기록했다. Pass도 기준별 개수를 표시하며 개별 근거는 원본 JSON에 보존한다.

## 기준별 전체 집계

| 평가 기준 | Pass | Fail | 판단 불가 |
| --- | --- | --- | --- |
| 1-1 평가 초점 반영 | 1 | 0 | 0 |
| 1-2 후보 도출의 타당성 | 5 | 0 | 0 |
| 2-1 후보 검증에 적합한 쿼리 | 5 | 0 | 0 |
| 3-1 검색 결과의 관련성 | 10 | 0 | 0 |
| 4-1 출처 선정의 타당성 | 32 | 30 | 0 |
| 5-1 본문 수집의 유효성 | 58 | 0 | 4 |
| 6-1 핵심 평가 초점의 근거 확보 | 1 | 0 | 0 |
| 6-2 Research 판단과 수집 근거의 일치 | 1 | 0 | 0 |

## 4-1 출처 선정의 타당성

### 당시 문서에 명시된 판정 기준

- Pass: 검색 결과 중 설계 범위와 후보 검증에 관련되고 게시 주체를 식별할 수 있는 문서를 선택한다. 동일 내용의 중복 URL이나 근거가 부족한 목록·홍보 페이지를 불필요하게 우선하지 않는다.
- Fail: 관련성이나 출처를 확인하지 않은 채 무관한·중복된·본문 근거가 없는 문서를 선택하고, 검색 결과에 있던 더 적절한 출처를 뚜렷한 이유 없이 제외한다.

공식 출처가 아니라는 이유만으로 Fail하지 않는다. 이 평가는 저장된 검색 결과에서 실제 선택 가능한 문서를 기준으로 한다.

### 모든 Fail과 판단 불가 원문

| 번호 | 평가 대상 | 판정 | 실제 적용한 기준 원문 | 판단 근거 원문 |
| --- | --- | --- | --- | --- |
| 1 | doc-1f8d35673c9047c1a855547321a98182 | Fail | 기술 근거와 게시 주체를 충분히 확인하지 않은 자료를 불필요하게 선택했다. | doc-1f8d35673c9047c1a855547321a98182, https://www.scribd.com/document/997545312/Coding-Assignment-Uber-Style-Driver-Dispatch-Operations-System은 과제 제목 외 작성 주체·NFR 검증 내용이 확인되지 않는다. 이후 query-1에서 직접 관련된 Uber 기술 글이 선택 가능했는데도 이 과제 자료의 수집 필요성은 기록되지 않았다. 문장 0~4는 접근 안내뿐이며 차단 자체는 별도 오류로 본다. |
| 2 | doc-abdf1fbeb82e490dad91bea0d079d712 | Fail | 기술 검증 근거가 부족한 제품 홍보 페이지를 불필요하게 선택했다. | doc-abdf1fbeb82e490dad91bea0d079d712, https://apps.apple.com/us/app/uber-%EC%9A%B0%EB%B2%84-%ED%83%9D%EC%8B%9C-%ED%98%B8%EC%B6%9C-%ED%94%8C%EB%9E%AB%ED%8F%BC/id368677368?l=ko&platform=vision, 문장 0~16은 호출 기능·권한 소개다. brief에 이미 있는 기능을 반복하며 검색 지연·중복 배정·내구성 검증 자료가 아니다. 여러 동일 앱 URL까지 선택한 이유도 없다. |
| 3 | doc-a11a6ce62f73418aaccc0591953b2553 | Fail | 동일 내용의 중복 URL을 필요성 없이 추가 선택했다. | doc-a11a6ce62f73418aaccc0591953b2553, https://www.oreilly.com/ideas/query-the-planet-geospatial-big-data-analytics-at-uber, 문장 0~77은 doc-69902ab150744f46b02af3c6a0099761의 본문과 동일하다. query-2에 두 경로가 함께 있었으며 추가 검증 목적이나 차이 확인 사유가 없다. |
| 4 | doc-37b35f1daa614a3496f1d5d60225844a | Fail | 검증 목적이 구분되지 않는 동일 내용의 버전 중복을 선택했다. | doc-37b35f1daa614a3496f1d5d60225844a, https://www.postgresql.org/docs/devel/fdw-row-locking.html, 문장 0~28은 먼저 선택한 FDW 문서와 실질적으로 같고 절 번호만 다르다. 개발 버전과 10 버전을 함께 확인해야 할 설계상 이유가 없다. |
| 5 | doc-65f4bec8872943918ab93a1fbee8f9e2 | Fail | 불필요한 구버전·동일 내용 중복을 선택했다. | doc-65f4bec8872943918ab93a1fbee8f9e2, http://www.postgresql.org/docs/9.5/fdw-row-locking.html, 문장 2~30은 다른 FDW 버전의 내용과 동일하다. brief에 9.5 사용 조건이 없고 버전 비교 사유도 기록되지 않았다. |
| 6 | doc-eb6fe80da5634c5e9d3cebc5e8868555 | Fail | 프로토콜·앵커만 다른 동일 문서를 중복 선택했다. | doc-eb6fe80da5634c5e9d3cebc5e8868555, https://docs.confluent.io/kafka/design/producer-design.html#producer-design, 문장 0~26은 doc-562bfae840d4461ba0ddce8910ac247f와 같다. 추가 근거나 다른 적용 조건을 얻지 못하는 중복 선택이다. |
| 7 | doc-4ac859359e584166b5492a678172ddff | Fail | 기술 검증 내용이 없는 동일 앱 페이지를 중복 선택했다. | doc-4ac859359e584166b5492a678172ddff, https://apps.apple.com/us/app/uber-%EC%9A%B0%EB%B2%84-%ED%83%9D%EC%8B%9C-%ED%98%B8%EC%B6%9C-%ED%94%8C%EB%9E%AB%ED%8F%BC/id368677368?l=ko, 문장 0~16은 기존 앱 소개와 같고 이후는 사용자 후기다. 기술적 NFR 검증을 위해 이 변형 URL을 추가 수집할 이유가 없다. |
| 8 | doc-d83d0b5808c845d3b4cd037426a3c241 | Fail | 주소 표기만 다른 제품 소개·후기 페이지를 중복 선택했다. | doc-d83d0b5808c845d3b4cd037426a3c241, https://apps.apple.com/us/app/uber-taxi-%EC%9A%B0%EB%B2%84-%ED%83%9D%EC%8B%9C-%ED%83%9D%EC%8B%9C-%ED%98%B8%EC%B6%9C-%ED%94%8C%EB%9E%AB%ED%8F%BC/id368677368?l=ko, 문장 0~16 및 17~40은 이미 수집한 동일 앱 소개·후기와 같다. 후보 검증에 추가 가치가 확인되지 않는다. |
| 9 | doc-a73194282e3a47eb94bc37f7ac958037 | Fail | 동일 앱의 플랫폼별 홍보 페이지를 필요성 없이 중복 선택했다. | doc-a73194282e3a47eb94bc37f7ac958037, https://apps.apple.com/us/app/uber-%EC%9A%B0%EB%B2%84-%ED%83%9D%EC%8B%9C-%ED%98%B8%EC%B6%9C-%ED%94%8C%EB%9E%AB%ED%8F%BC/id368677368?l=ko&platform=watch, 문장 0~16은 동일한 제품 설명이다. 문장 32~35의 체감 후기 역시 서버 검색 지연이나 재처리 보장을 검증하지 못한다. |
| 10 | doc-e3abb1e2d22e4f8f9bf6be77d6f6b227 | Fail | 지역 경로만 다른 동일 내용의 문서를 중복 선택했다. | doc-e3abb1e2d22e4f8f9bf6be77d6f6b227, https://www.uber.com/en-BE/blog/orders-near-you, 문장 0~100은 doc-2b122955f3304c3fa5962fa99a484797와 같다. 지역별 적용 차이를 조사한 기록 없이 같은 글을 추가 선택했다. |
| 11 | doc-0161275bfe344b05b899fc4c5c7deb08 | Fail | 동일 FDW 잠금 내용의 구버전·경로 중복을 선택했다. | doc-0161275bfe344b05b899fc4c5c7deb08, https://www.postgresql.org/docs/9.6//fdw-row-locking.html, 문장 2~30은 이미 선택한 FDW 문서와 실질적으로 같다. 이중 슬래시 경로나 9.6 버전을 별도로 검토할 필요가 기록되지 않았다. |
| 12 | doc-2917ca1f1ee94f06b1b7880f86e73d4f | Fail | 동일 버전의 프로토콜·경로 중복 문서를 선택했다. | doc-2917ca1f1ee94f06b1b7880f86e73d4f, http://www.postgresql.org/docs/9.6/fdw-row-locking.html, 문장 0~30은 doc-0161275bfe344b05b899fc4c5c7deb08과 같다. 중복 수집을 정당화할 내용 차이나 설계 조건이 없다. |
| 13 | doc-40e923cb185b4f67adca039542e716b5 | Fail | 프로토콜만 다른 동일 문서를 중복 선택했다. | doc-40e923cb185b4f67adca039542e716b5, https://www.postgresql.org/docs/9.5/fdw-row-locking.html, 문장 0~30은 doc-65f4bec8872943918ab93a1fbee8f9e2와 같다. 배정 경합 검증에 새로운 정보를 주지 않는 중복이다. |
| 14 | doc-53e1962443f6461d96788b7bec587e45 | Fail | 후보 검증과 무관한 제공 지역 목록을 선택했다. | doc-53e1962443f6461d96788b7bec587e45, https://docs.cloud.google.com/managed-service-for-apache-kafka/docs/locations?hl=ko, 문장 0~12는 관리형 Kafka의 제공 리전 목록이다. 위치 이벤트 수집의 처리량·적체 제어와 무관하며 같은 query-4에 생산자 설계와 할당량 문서가 있었다. |
| 15 | doc-e4a062b101b74355923f4c3cf9cb3d07 | Fail | 무관한 제공 지역 목록을 다른 도메인으로 중복 선택했다. | doc-e4a062b101b74355923f4c3cf9cb3d07, https://docs.cloud.google.cn/managed-service-for-apache-kafka/docs/locations?hl=ko, 문장 0~13은 doc-53e1962443f6461d96788b7bec587e45와 동일한 제공 리전 정보다. 처리량 검증과 무관하고 추가 수집 사유도 없다. |
| 16 | doc-e6fc0d92e1a24771969b44f139023a25 | Fail | 언어별 주소만 다른 동일 앱 소개를 불필요하게 중복 선택했다. | doc-e6fc0d92e1a24771969b44f139023a25, https://apps.apple.com/us/app/uber-%C4%91%E1%BA%B7t-xe/id368677368?l=ko, 문장 0~16과 17~40은 이미 수집한 같은 앱의 소개·후기다. 후보별 기술 동작이나 보장 조건을 추가 확인하지 못한다. |
| 17 | doc-d399a711f4f34f7789e369ac9d7da167 | Fail | 동일 앱의 주소 변형을 검증 목적 없이 중복 선택했다. | doc-d399a711f4f34f7789e369ac9d7da167, https://apps.apple.com/us/app/uber-commandez-un-trajet/id368677368?l=ko, 문장 0~16은 기존 앱 소개와 같고 이후도 동일 후기다. 검색 지연·배정 원자성·위치 처리량의 기술 근거가 아니다. |
| 18 | doc-7aed05827b604114ae5a1b1c2b207334 | Fail | 동일 제품 소개·후기의 중복 URL을 선택했다. | doc-7aed05827b604114ae5a1b1c2b207334, https://apps.apple.com/us/app/uber-%D9%85%D8%B4%D8%A7%D9%88%D9%8A%D8%B1-%D9%85%D8%B1%D9%8A%D8%AD%D8%A9-%D9%88%D9%85%D9%88%D8%AB%D9%88%D9%82%D8%A9/id368677368?l=ko, 문장 0~40은 기존 동일 앱 페이지와 같다. 별도 적용 조건이나 NFR 검증 가치를 확인하지 않고 반복 수집했다. |
| 19 | doc-49c5c91b346b497c92d9bc8ff41f23a1 | Fail | 국가 경로만 다른 동일 기술 글을 중복 선택했다. | doc-49c5c91b346b497c92d9bc8ff41f23a1, https://www.uber.com/en-BG/blog/elk, 문장 0~104는 doc-89e30c8af090441cb213b9dc5da6ef75와 같다. 지역별 설계 차이나 별도 내용 확인 목적이 없다. |
| 20 | doc-e91784cc4f664b438cfac92d05c21b1d | Fail | 프로토콜만 다른 같은 버전의 문서를 중복 선택했다. | doc-e91784cc4f664b438cfac92d05c21b1d, https://www.postgresql.org/docs/10/fdw-row-locking.html, 문장 0~28은 doc-29e37ae90b7b48b4a19727341a6a5337와 같다. 추가 수집의 검증 목적이 기록되지 않았다. |
| 21 | doc-a430a00a94644a4dbe09fb4b74bf8019 | Fail | 설계 조건과 무관한 버전 중복을 불필요하게 선택했다. | doc-a430a00a94644a4dbe09fb4b74bf8019, http://www.postgresql.org/docs/19/fdw-row-locking.html, 문장 0~28은 개발 버전 및 다른 FDW 문서와 실질적으로 같다. 특정 버전 사용이나 차이 검증 계획이 없다. |
| 22 | doc-410df9d1b7344ac18aef31f475041a92 | Fail | 동일 버전·동일 내용의 주소 중복을 선택했다. | doc-410df9d1b7344ac18aef31f475041a92, https://www.postgresql.org/docs/9.6/fdw-row-locking.html, 문장 0~30은 앞서 수집한 9.6 FDW 문서들과 같다. 프로토콜·슬래시 차이는 추가 기술 근거가 아니다. |
| 23 | doc-e7d22be5cf3f40f79c5a5a74a7cf824d | Fail | 더 직접적인 자료가 있는데도 요약·연결 페이지를 본문 근거 대상으로 선택했다. | doc-e7d22be5cf3f40f79c5a5a74a7cf824d, https://daily.dev/posts/design-uber-lyft-location-index-pt-2-deep-dives-systems-design-questions-3-0-with-ex-google-swe-cbmt7vblq, 문장 1~5는 영상 내용 소개와 시청 시간뿐이다. 같은 검색에 원본 영상 https://www.youtube.com/watch?v=8wDRlS3vJvc와 Uber의 H3 글이 있었지만 이 요약을 별도 기술 근거로 택한 이유가 없다. |
| 24 | doc-8c3b80764f7c45a0af35532512a4be02 | Fail | 기술 검증 가치가 없는 동일 앱 페이지의 주소 변형을 중복 선택했다. | doc-8c3b80764f7c45a0af35532512a4be02, https://apps.apple.com/us/app/uber-%D0%B7%D0%B0%D0%BA%D0%B0%D0%B7-%D0%BF%D0%BE%D0%B5%D0%B7%D0%B4%D0%BE%D0%BA/id368677368?l=ko, 문장 0~40은 기존 앱 소개·후기와 같다. 호출 처리의 기술적 제약을 추가 확인할 자료가 아니다. |
| 25 | doc-196e4556ae784aa29b5552169ac54749 | Fail | 동일 잠금 설명의 불필요한 버전 중복을 선택했다. | doc-196e4556ae784aa29b5552169ac54749, https://www.postgresql.org/docs/11/fdw-row-locking.html, 문장 0~28은 이미 수집한 FDW 잠금 내용과 같다. 11 버전만의 적용 조건을 조사할 필요가 기록되지 않았다. |
| 26 | doc-e56415172cca449ab61b194d0cadda2a | Fail | 더 직접적인 기술 자료가 있는 결과에서 홍보성 요약을 불필요하게 추가 선택했다. | doc-e56415172cca449ab61b194d0cadda2a, https://www.linkedin.com/posts/nk-systemdesign-one_i-spent-hours-studying-how-uber-finds-nearby-activity-7317149051009794048-ktqj, 문장 1~3은 일곱 항목 요약과 뉴스레터 홍보다. 같은 결과의 H3 공식 사이트와 기술 해설에 비해 적용 조건·제약이 부족하며 추가 검증 목적이 기록되지 않았다. |
| 27 | doc-46125a5baa71406faa6c3816b2c7630e | Fail | 이미 확보한 동일 기술 글을 지역 경로만 바꾸어 중복 선택했다. | doc-46125a5baa71406faa6c3816b2c7630e, https://www.uber.com/us/en/blog/orders-near-you, 문장 0~100은 doc-2b122955f3304c3fa5962fa99a484797 및 다른 지역 경로와 동일하다. 글 자체의 관련성은 있지만 세 번째 동일 본문을 수집할 이유가 없다. |
| 28 | doc-11cff75665084e848f7b870d269e8355 | Fail | 후보 검증과 무관한 문서를 선택했다. | doc-11cff75665084e848f7b870d269e8355, https://www.cnbc.com/2019/05/07/uber-lyft-drivers-to-go-on-strike-over-low-wages-and-benefits.html, 문장 0~4는 임금·복지 관련 파업 기사다. 검색 지연, 동시 배정, 위치 이벤트 처리, 호출 보존과 무관하다. 같은 query-2 결과에 H3 기술 자료가 있었다. |
| 29 | doc-329a1617d5da48f291ab8c23ee1e699a | Fail | 설계 범위·평가 초점과 무관한 기사를 선택했다. | doc-329a1617d5da48f291ab8c23ee1e699a, https://finance.yahoo.com/news/uber-lyft-drivers-plan-strikes-221103231.html, 문장 0~7, 17~23은 파업·임금·기업공개에 관한 내용이다. query-2의 근접 검색 지연을 검증할 기술 근거가 아니다. |
| 30 | fetch:https://www.instagram.com/popular/uber-dispatch-system-architecture-diagram | Fail | 게시 주체와 본문 근거를 확인하기 어려운 목록 페이지를 선택했다. | https://www.instagram.com/popular/uber-dispatch-system-architecture-diagram은 query-1의 인기 주제 목록 주소로, 개별 작성자나 검증 가능한 기술 글이 식별되지 않는다. 문서 ID·문장 번호는 없으며 빈 본문 오류만 저장되었다. 배차라는 제목만으로 수집 대상으로 선택한 타당성이 부족하다. |

## 5-1 본문 수집의 유효성

### 당시 문서에 명시된 판정 기준

- Pass: 선택한 문서의 실제 본문을 정상적으로 수집하여 후속 근거 확인에 사용할 수 있다.
- Fail: 본문 대신 검색 요약이나 다른 문서 내용을 수집하고 정상적인 본문으로 처리한다.

판단 불가/실행 오류: 접근 차단·타임아웃 등으로 본문 수집에 실패한 경우는 별도로 기록한다.

### 모든 Fail과 판단 불가 원문

| 번호 | 평가 대상 | 판정 | 실제 적용한 기준 원문 | 판단 근거 원문 |
| --- | --- | --- | --- | --- |
| 1 | doc-1f8d35673c9047c1a855547321a98182 | 판단 불가 | 접근 제한으로 실제 본문 수집에 실패한 경우는 실행 문제로 구분한다. | doc-1f8d35673c9047c1a855547321a98182, https://www.scribd.com/document/997545312/Coding-Assignment-Uber-Style-Driver-Dispatch-Operations-System, 문장 0~4는 자바스크립트 비활성화와 사이트 로딩 실패 안내뿐이다. 과제 본문은 확보되지 않았고 이를 기술 본문으로 정상 활용한 기록도 없어 수집 실패로 제외한다. |
| 2 | doc-f564894850c046b1a6f54b01ddab93d5 | 판단 불가 | 실질적 본문이 확보되지 않은 수집 문제는 별도로 기록한다. | doc-f564894850c046b1a6f54b01ddab93d5, https://wherobots.com/discover/h3, 문장 0은 건너뛰기 링크와 제휴 배너뿐이다. H3 해설 본문이 추출되지 않았고 원인은 기록되지 않았다. 이를 정상 기술 본문으로 활용한 기록도 없어 수집 실패로 제외한다. |
| 3 | fetch:https://www.instagram.com/popular/uber-dispatch-system-architecture-diagram | 판단 불가 | 빈 본문으로 수집에 실패한 실행 오류는 품질 실패와 구분한다. | https://www.instagram.com/popular/uber-dispatch-system-architecture-diagram에 대해 fetch_failures에 본문이 비었다는 오류가 저장되어 있다. 실제 본문·문서 ID·문장 번호가 없으므로 유효성을 판정할 수 없다. 정상 본문으로 대체 처리했다는 증거도 없다. |
| 4 | fetch:https://docs.redhat.com/en/documentation/red_hat_streams_for_apache_kafka/2.3/html/kafka_configuration_tuning/con-consumer-config-properties-str | 판단 불가 | 서버 오류로 본문 수집에 실패한 경우는 실행 오류로 제외한다. | https://docs.redhat.com/en/documentation/red_hat_streams_for_apache_kafka/2.3/html/kafka_configuration_tuning/con-consumer-config-properties-str은 두 차례 요청 모두 HTTP 503으로 실패했다. 확인 위치: fetch_failures. 수집된 문서 ID·본문·문장 번호가 없으므로 품질 실패로 점수화하지 않는다. |
