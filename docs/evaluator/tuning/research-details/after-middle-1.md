# 수정 후 Middle 1회 평가 상세

새로 생성한 Research 결과를 평가한 실행이다.

[주요 실험 기록](../research-tuning.md) · [원본 JSON](../../../../.archgen/m7-followup/current-criteria-20261019/research-tuning/after/middle/1-evaluation/research.json) · [당시 평가 기준](../../../../.archgen/m7-followup/current-criteria-20261019/research-tuning/after/middle/1-evaluation/research-criteria.md) · [Trace](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/3f8fd5489c73408ba36a89a91da7417b)

전체 178건: Pass 112 · Fail 47 · 판단 불가 19. 아래 표에는 모든 Fail과 판단 불가를 생략 없이 기록했다. Pass도 기준별 개수를 표시하며 개별 근거는 원본 JSON에 보존한다.

## 기준별 전체 집계

| 평가 기준 | Pass | Fail | 판단 불가 |
| --- | --- | --- | --- |
| 1-1 평가 초점 반영 | 1 | 0 | 0 |
| 1-2 후보 도출의 타당성 | 5 | 0 | 0 |
| 2-1 후보 검증에 적합한 쿼리 | 5 | 0 | 0 |
| 3-1 검색 결과의 관련성 | 10 | 1 | 0 |
| 4-1 출처 선정의 타당성 | 33 | 44 | 0 |
| 5-1 본문 수집의 유효성 | 56 | 2 | 19 |
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
| 1 | call_thuAW9asgrgga82kxh6F2Urp | Fail | 설계 문제를 검증할 문서 후보 없이 채용·제품 소식에 치우친 결과다. | query-1의 보완 결과는 채용 공고와 성별 매칭 선호 뉴스에 치우친다. doc-300a0a34ec9649d0b915ba1dcd38b4ea, https://www.cnbc.com/amp/2025/07/23/uber-women-drivers-riders.html 문장 5~10은 제품 선호 기능이며, doc-8234ef94d6e64ea5949d8005459cffa4, https://www.businessinsider.com/uber-forward-dispatch-trips-riders-drivers-study-2025-6 문장 12~20도 주로 픽업 대기 연구다. 매칭 플랫폼 구조나 핵심 품질 문제의 기술적 검토 후보가 부족하다. |

## 4-1 출처 선정의 타당성

### 당시 문서에 명시된 판정 기준

- Pass: 검색 결과 중 설계 범위와 후보 검증에 관련되고 게시 주체를 식별할 수 있는 문서를 선택한다. 동일 내용의 중복 URL이나 근거가 부족한 목록·홍보 페이지를 불필요하게 우선하지 않는다.
- Fail: 관련성이나 출처를 확인하지 않은 채 무관한·중복된·본문 근거가 없는 문서를 선택하고, 검색 결과에 있던 더 적절한 출처를 뚜렷한 이유 없이 제외한다.

공식 출처가 아니라는 이유만으로 Fail하지 않는다. 이 평가는 저장된 검색 결과에서 실제 선택 가능한 문서를 기준으로 한다.

### 모든 Fail과 판단 불가 원문

| 번호 | 평가 대상 | 판정 | 실제 적용한 기준 원문 | 판단 근거 원문 |
| --- | --- | --- | --- | --- |
| 1 | doc-c79bc335048e4874aa46ba7ab2f3f570 | Fail | 핵심 후보를 검증할 기술 근거가 부족한 홍보 출처를 불필요하게 선택했다. | query-1의 2위는 알림 기능 출시 보도자료다. doc-c79bc335048e4874aa46ba7ab2f3f570, https://finance.yahoo.com/news/delivery-updates-way-dispatch-launches-130000657.html 문장 4~16은 알림 선택과 채널 홍보이며, 검색 지연·배정 원자성·요청 보존을 설명하지 않는다. 같은 결과의 InfoQ 배차 기사가 더 적합하다. |
| 2 | doc-eb3c1ac145bb4d4d87413e0fea468abf | Fail | 관련성이 확인되지 않은 무관한 문서를 본문 수집 대상으로 선택했다. | query-1에서 제목이 일반적인 Uber이고 URL은 배달 습관 설문을 가리킨다. doc-eb3c1ac145bb4d4d87413e0fea468abf, https://www.uber.com/us/en/blog/uber-eats-delivery-habits 문장 0~3, 25~30은 설문 경품 규칙이다. 같은 결과의 배차 기술 기사와 달리 후보 검증과 무관하다. |
| 3 | doc-96c9457d1e4349f8907e52c89a814b97 | Fail | 직접적인 기술 문서가 있는데 목록 페이지를 불필요하게 선택했다. | query-4에는 4위의 구체적인 Uber 수집 구조 기사가 있으나 뉴스 목록도 수집했다. doc-96c9457d1e4349f8907e52c89a814b97, https://www.infoq.com/apache_kafka/news 문장 1~25는 서로 다른 기사 소개의 모음이다. 위치 처리량 후보를 검증할 직접 본문보다 목록의 우선 수집 필요성이 확인되지 않는다. |
| 4 | doc-af5b067148814237b8d35c35e06a26bb | Fail | 후보 검증 근거가 부족한 제품 홍보 출처를 불필요하게 선택했다. | query-4의 2위는 Unravel 연동 발표다. doc-af5b067148814237b8d35c35e06a26bb, https://finance.yahoo.com/news/unravel-data-expands-data-ingestion-123000611.html 문장 0~7, 23~27은 모니터링 제품의 효능을 홍보하며 배치·역압의 실제 처리 조건을 충분히 설명하지 않는다. 같은 검색에 구체적인 수집 구조 기사가 있다. |
| 5 | doc-df6ad7f8c0b8466ba5a5bab1d4bf1102 | Fail | 후보 검증 근거가 부족한 제품 홍보 출처를 불필요하게 선택했다. | query-4의 3위는 Kafka 연동 지원 발표다. doc-df6ad7f8c0b8466ba5a5bab1d4bf1102, https://finance.yahoo.com/news/scylladb-announces-comprehensive-support-apache-150000386.html 문장 1~11은 커넥터 지원과 일반적인 처리량 홍보가 중심이다. 위치 인덱스 수집의 적체·최신성 문제에는 같은 결과의 구체적인 구조 기사가 더 적합하다. |
| 6 | doc-f176155bc33c4c6f8fe0ce476b85a570 | Fail | 제목·경로에서 후보 관련성을 확인하지 못한 일반 문서를 선택했다. | query-5의 3위는 일반 문서 제목과 과거 보안 준수 경로를 가진다. doc-f176155bc33c4c6f8fe0ce476b85a570, https://docs.confluent.io/legacy/platform/5.1.4/security/compliance.html 문장 0~18도 일반 문서 홈 내용이다. 같은 결과의 멱등성 해설·설정 비교 문서보다 호출 보존 검증 적합성이 낮다. |
| 7 | doc-5618c04770934f44893414ecd35985e6 | Fail | 동일 내용의 중복 지역 URL을 추가 수집할 이유가 없다. | query-6의 2위는 이미 선택한 인도 지역판과 제목·경로 본문이 같은 지역 변형이다. doc-5618c04770934f44893414ecd35985e6, https://www.uber.com/en-FI/blog/visualizing-city-cores-with-h3 문장 0~23은 doc-2eef43d7451c476993944facb47a9301과 동일하다. 같은 결과의 별도 공간 분할 글보다 추가 가치가 없다. |
| 8 | doc-f6f1266fc0f542fb8810e927a5e70939 | Fail | 동일 내용의 중복 지역 URL을 추가 수집할 이유가 없다. | query-6의 3위는 기존 공식 글의 스위스 지역판이다. doc-f6f1266fc0f542fb8810e927a5e70939, https://www.uber.com/en-CH/blog/visualizing-city-cores-with-h3 문장 0~23이 기존 인도 지역판과 동일하다. 중복 대신 독립적인 분할 근거를 검토할 수 있었다. |
| 9 | doc-318cd257d9aa4712a508dd99ca9a52bb | Fail | 서비스 설계와 무관한 업체 목록을 선택했다. | query-1의 4위는 MapQuest의 지역 업체 항목이다. doc-318cd257d9aa4712a508dd99ca9a52bb, https://www.mapquest.com/us/oklahoma/driver-dispatch-425362787 는 매칭 구조의 기술 출처로 볼 근거가 없다. 문장 0~2의 접근 차단은 별도 실행 문제이며, 선정 부적합성은 업체 목록이라는 검색 기록에 근거한다. |
| 10 | doc-8c475c16b9ae44bbbaa0e21dd38fe163 | Fail | 평가 초점과 다른 지도 공급자 비용 비교를 불필요하게 선택했다. | query-1의 5위는 지도 API 비용·벤더 비교다. doc-8c475c16b9ae44bbbaa0e21dd38fe163, https://brocoders.com/blog/mapbox-vs-google-maps-vs-openstreetmap 문장 20~22, 94~112는 과금 구조가 중심이다. 검색 지연·배정 경합·위치 처리·호출 보존 검증에는 같은 결과의 배차 기술 기사가 더 적합하다. |
| 11 | doc-8057ebfb897e4aeda61d84fd69582156 | Fail | 설계 주제와 무관한 교육 홍보 페이지를 선택했다. | query-1의 6위는 인공지능 보조 개발 교육 과정이다. doc-8057ebfb897e4aeda61d84fd69582156, https://certification.qconferences.com/ai-assisted-engineering 문장 0~12는 개발 도구와 교육 일정·가격이며 차량 매칭 후보와 무관하다. |
| 12 | doc-a2ac9a7faa934a309efe2d9da72f0d05 | Fail | 동일 내용의 중복 지역 URL을 추가 수집할 이유가 없다. | query-2의 6위는 바로 앞 공식 검색 사례의 벨기에 지역판이다. doc-a2ac9a7faa934a309efe2d9da72f0d05, https://www.uber.com/en-BE/blog/orders-near-you 문장 49~69는 doc-0b8810aa573448bfab6c2c1be076878c과 동일하다. 중복 수집의 별도 목적이 기록되지 않았다. |
| 13 | doc-aa520716dc5e4f3fbce402a9d613fce5 | Fail | 온라인 매칭 후보를 검증하기 어려운 분석 제품 홍보를 선택했다. | query-4의 6위는 Dremio 데이터 레이크 제품 발표다. doc-aa520716dc5e4f3fbce402a9d613fce5, https://finance.yahoo.com/news/dremio-solidifies-position-premier-apache-131100570.html 문장 6~14는 분석 기능과 효능 홍보가 중심이다. 같은 결과에 역압·복구의 실제 구조를 다룬 기사가 있다. |
| 14 | doc-022b078bfc544ebbb32df99eb40480b9 | Fail | 구체적인 기술 근거 대신 기업 소개·목록 페이지를 선택했다. | query-5의 6위는 Tracxn 기업 프로필이다. doc-022b078bfc544ebbb32df99eb40480b9, https://tracxn.com/d/companies/apache-kafka/__u4vQDVbHEW-r0BY_Fvu_uYf9dD5fKBUk27rgAdQQwa8 문장 0~17, 27~33은 기업·경쟁사 소개와 일반 기능 요약이다. 같은 결과의 멱등성 기술 해설보다 보존·재처리 검증 근거가 부족하다. |
| 15 | doc-67e6a16039214557a2d185022666cbc1 | Fail | 동일 내용의 중복 지역 URL을 추가 수집할 이유가 없다. | query-6의 4위인 프랑스 지역판이다. doc-67e6a16039214557a2d185022666cbc1, https://www.uber.com/en-FR/blog/visualizing-city-cores-with-h3 문장 0~23이 기존 인도·핀란드·스위스 지역판과 동일하다. 독립 근거가 추가되지 않는다. |
| 16 | doc-e319321dec2549ed8c9d4f500fbc2bac | Fail | 평가 후보와 직접 연결되지 않는 운영·사기 논쟁 기사를 선택했다. | query-1의 7위는 GPS 조작 의심에 따른 계정 정지 기사다. doc-e319321dec2549ed8c9d4f500fbc2bac, https://www.businessinsider.com/uber-cracks-down-on-driver-gps-locations-deactivating-accounts-2025-9 문장 0~13, 19~31은 위치 정확도·사기 판단을 다룬다. 위치 갱신 처리량이나 검색 지연의 설계 근거를 확인할 선택 이유가 없다. |
| 17 | doc-52c2103f12cc4deb9b37c01b4d2f6e45 | Fail | 설계 범위와 무관한 사건 보도 기사를 선택했다. | query-1의 8위는 승객 영상 방송에 따른 운전자 정지 기사다. doc-52c2103f12cc4deb9b37c01b4d2f6e45, https://www.cnbc.com/2018/07/21/uber-suspends-st-louis-driver-who-broadcasts-passengers-on-twitch.html 문장 0~10은 개인정보·행동 규정 사건이며 매칭 후보 검증과 무관하다. |
| 18 | doc-dd0519a25ef4402f8eb3d9336066cf1a | Fail | 동일 글의 경로 별칭을 중복 수집할 이유가 없다. | query-2의 8위는 앞선 O’Reilly 글의 경로 변형이다. doc-dd0519a25ef4402f8eb3d9336066cf1a, https://www.oreilly.com/ideas/query-the-planet-geospatial-big-data-analytics-at-uber 문장 0~77은 doc-63ba1b53339a4f61b6e20d0f2d266ee4와 동일하다. 추가 검증 가치가 기록되지 않았다. |
| 19 | doc-e4a60030e19e47f89a2d7aa62e0462cd | Fail | 관련성이 약한 홍보 글의 추적 매개변수 URL까지 중복 수집했다. | query-4의 7위는 기존 Dremio 발표의 매개변수 변형이다. doc-e4a60030e19e47f89a2d7aa62e0462cd, https://finance.yahoo.com/news/dremio-solidifies-position-premier-apache-131100570.html?fr=sycsrp_catchall 문장 0~14가 doc-aa520716dc5e4f3fbce402a9d613fce5와 동일하다. 관련 기술 기사를 두고 추가 수집할 근거가 없다. |
| 20 | doc-e802ddeaf000487095db931a894c4ebb | Fail | 기술 키워드만 포함된 무관한 채용 공고를 선택했다. | query-4의 8위는 보안·인공지능 데이터 플랫폼 채용 공고다. doc-e802ddeaf000487095db931a894c4ebb, https://bebee.com/vn/jobs/senior-software-engineer-data-platform-python-golang-olik-global-ho-chi-minh-city--t7xk-809416821 문장 9~25는 직무·지원 요건이며 처리량·역압 설계의 검증 본문이 아니다. |
| 21 | doc-2ddf688dc6fa44409346d29a689dea77 | Fail | 기술 키워드만 포함된 무관한 채용 공고를 선택했다. | query-4의 9위도 Olik 채용 공고다. doc-2ddf688dc6fa44409346d29a689dea77, https://bebee.com/vn/jobs/senior-software-engineer-backend-data-platform-financial-systems-olik-global-ho-chi-minh-city--techmap_vn_4455278265 문장 2~11은 보안 플랫폼 직무와 요구 역량을 소개한다. 실제 위치 수집 동작의 근거가 아니며 같은 검색에 적합한 기술 기사가 있다. |
| 22 | doc-818667a36095474d897076b2e714d8b5 | Fail | 일반 기업 프로필의 경로 별칭을 중복 선택했다. | query-5의 7위는 기존 Tracxn 프로필의 별칭이다. doc-818667a36095474d897076b2e714d8b5, https://tracxn.com/d/companies/apachekafka/__u4vQDVbHEW-r0BY_Fvu_uYf9dD5fKBUk27rgAdQQwa8 문장 0~33은 doc-022b078bfc544ebbb32df99eb40480b9와 동일하다. 호출 보존의 구체적인 조건을 추가하지 않는다. |
| 23 | doc-8dbaa02e948b4541bed388138153f801 | Fail | 검색어가 비슷하더라도 다른 문제 영역의 문서를 불필요하게 선택했다. | query-2의 10위는 Pinecone 고차원 벡터 검색 교육이다. doc-8dbaa02e948b4541bed388138153f801, https://codesignal.com/learn/courses/optimizing-and-scaling-pinecone-for-vector-search/lessons/reducing-query-latency-with-precomputed-nearest-neighbors 문장 8~15는 문장 임베딩을 다룬다. 움직이는 운전자의 공간 검색과 적용 조건이 다르고 같은 결과에 직접적인 공간 검색 자료가 있다. |
| 24 | doc-fd7fa9d1a9eb491c9117665c743b0718 | Fail | 기술 검증 본문이 없는 자격 인증 홍보 페이지를 선택했다. | query-5의 10위는 인증 시험 안내다. doc-fd7fa9d1a9eb491c9117665c743b0718, https://www.confluent.io/certification 문장 1~18은 자격·교육·시험 소개다. 같은 결과의 멱등성 자료와 달리 호출 보존·재처리 조건을 확인할 수 없다. |
| 25 | doc-300a0a34ec9649d0b915ba1dcd38b4ea | Fail | 제품 기능 뉴스만으로 핵심 품질 후보를 검증하기 어려운 출처다. | query-1 보완 검색의 3위는 성별 매칭 선호 기능 뉴스다. doc-300a0a34ec9649d0b915ba1dcd38b4ea, https://www.cnbc.com/amp/2025/07/23/uber-women-drivers-riders.html 문장 5~10은 선호 설정과 비보장 동작을 설명하지만 검색 지연·중복 배정·수집 처리량·요청 보존의 기술 근거는 없다. |
| 26 | doc-a52c3d6b19b449d4bf6d9279182aae30 | Fail | 이미 수집한 동일 글의 지역 URL을 추가 선택할 이유가 없다. | query-2 보완 검색의 1위지만 기존 공식 글의 미국 지역판이다. doc-a52c3d6b19b449d4bf6d9279182aae30, https://www.uber.com/us/en/blog/orders-near-you 문장 49~69는 doc-0b8810aa573448bfab6c2c1be076878c과 동일하다. 실제로 최종 후보에 두 문서를 함께 연결해도 독립 근거가 늘어나지는 않는다. |
| 27 | doc-bcda2da28e5a4689a0e70a32c46f0fac | Fail | 동일 제품 소식을 반복 수집하고 핵심 후보의 기술 근거를 확보하지 못한다. | query-1 보완 검색의 6위는 앞서 수집한 성별 선호 기능의 또 다른 기사다. doc-bcda2da28e5a4689a0e70a32c46f0fac, https://finance.yahoo.com/news/button-women-riders-waiting-ubers-000140042.html 문장 7~12는 선호 설정 설명으로 핵심 NFR 검증 근거가 없다. 주제 중복 수집의 필요성이 확인되지 않는다. |
| 28 | doc-b623632793b54f9387fbfb6011ab3faf | Fail | 이미 확보한 설계 설명의 과거 버전을 추가 수집할 이유가 없다. | query-5 보완 검색의 4위는 Kafka 0.8 문서다. doc-b623632793b54f9387fbfb6011ab3faf, https://kafka.apache.org/08/design/design 문장 4~54의 핵심 내용은 이미 선택한 4.3 설계 문서와 실질적으로 중복된다. 역사적 비교 목적도 없고 버전별 한계 검토 이유도 기록되지 않았다. |
| 29 | doc-9a4287762ca749e48b537777a3270395 | Fail | 같은 기사의 일반 경로와 대체 경로를 중복 선택했다. | query-1 보완 검색의 8위는 이미 선택한 CNBC 기사의 일반 경로다. doc-9a4287762ca749e48b537777a3270395, https://www.cnbc.com/2025/07/23/uber-women-drivers-riders.html 문장 0~15는 doc-300a0a34ec9649d0b915ba1dcd38b4ea의 동일 내용이다. 핵심 품질 후보에 약한 관련성까지 중복된다. |
| 30 | doc-238aded76d0b43b298542f4d56e82bc3 | Fail | 다른 서비스의 일정 기능 홍보를 핵심 품질 검증 자료로 선택했다. | query-1 보완 검색의 9위는 다음 날 배송 일정 기능 보도자료다. doc-238aded76d0b43b298542f4d56e82bc3, https://finance.yahoo.com/news/dispatch-launches-driver-schedule-power-140000103.html 문장 3~16은 가용 시간 선호와 마케팅 효능을 설명한다. 실시간 호출의 검색·배정 경합·보존 설계를 검증할 기술 근거가 부족하다. |
| 31 | doc-8234ef94d6e64ea5949d8005459cffa4 | Fail | 범위 밖의 픽업 대기·요금 논쟁을 핵심 시스템 지연 근거와 구분하지 못한 선정이다. | query-1 보완 검색의 10위는 선행 배차의 픽업 대기·가격 연구 기사다. doc-8234ef94d6e64ea5949d8005459cffa4, https://www.businessinsider.com/uber-forward-dispatch-trips-riders-drivers-study-2025-6 문장 12~20은 배정 후 도착 대기와 요금·표본 한계를 다룬다. 주변 검색 지연이나 배정 상태의 기술적 동작을 검증할 주된 자료로 선택할 근거가 약하다. |
| 32 | fetch:https://www.zoominfo.com/c/h3-engineering-solutions/453657234 | Fail | 동일 키워드의 무관한 기업 정보 페이지를 선택했다. | query-6의 6위는 H3라는 이름의 기업 프로필이다. https://www.zoominfo.com/c/h3-engineering-solutions/453657234 은 공간 인덱스 기술 자료로 확인되지 않으며 같은 결과에 Uber 공식 글과 공간 분할 해설이 있다. 접근 차단으로 본문 문장 번호·문서 ID는 없다. |
| 33 | fetch:https://www.virtualshareholdermeeting.com | Fail | 설계 범위와 무관한 일반 서비스 홈페이지를 선택했다. | query-1의 9위는 Broadridge 주주총회 서비스다. https://www.virtualshareholdermeeting.com 은 차량 매칭 후보와 관련성이 없고 같은 검색의 배차 기술 기사보다 우선할 이유가 없다. 본문이 비어 문서 ID·문장 번호는 없다. |
| 34 | fetch:https://www.indeed.com/q-kafka-apache-jobs.html | Fail | 기술 검증 본문이 없는 채용 목록을 불필요하게 선택했다. | query-5의 9위는 Kafka 채용 검색 목록이다. https://www.indeed.com/q-kafka-apache-jobs.html 은 보존·재처리의 기술 조건을 설명하는 출처가 아니며 같은 검색에 멱등성 해설이 다수 있다. 접근 차단으로 문서 ID·문장 번호는 없다. |
| 35 | fetch:https://rocketreach.co/grw-engineering-architecture-geospatial-profile_b5e37b84f42e6d54 | Fail | 기술 키워드가 포함된 무관한 기업 연락처 정보를 선택했다. | query-6의 8위는 GRW 기업 정보다. https://rocketreach.co/grw-engineering-architecture-geospatial-profile_b5e37b84f42e6d54 은 공간 분할 기술 문서가 아니며 같은 검색의 Uber 공식·Versent 기술 글이 더 적합하다. 접근 차단으로 문서 ID·문장 번호는 없다. |
| 36 | fetch:https://www.investing.com/news/technology-news/uber-expands-into-spanish-tourist-hotspot-1440319 | Fail | 시스템 부하 집중과 무관한 사업 진출 뉴스를 선택했다. | query-6의 9위는 스페인 관광 지역 사업 확장 기사다. https://www.investing.com/news/technology-news/uber-expands-into-spanish-tourist-hotspot-1440319 의 지역 표현은 시스템 핫스폿과 다르다. 같은 결과의 공간 분할 기술 글보다 적합할 이유가 없으며 접근 차단으로 문서 ID·문장 번호는 없다. |
| 37 | fetch:https://www.wwt.com | Fail | 후보 관련성이 확인되지 않은 일반 기업 홈페이지를 선택했다. | query-1의 10위는 WWT 홈페이지다. https://www.wwt.com 에서 차량 매칭·위치 갱신·배정 일관성을 검증할 특정 기술 글이 검색 기록에 나타나지 않는다. 같은 검색의 구체적인 배차 기사와 달리 선정 이유가 없고 본문 공백으로 문서 ID·문장 번호도 없다. |
| 38 | fetch:https://rocketreach.co/clifford-partitioning-co-ltd-email-format_b4678ca1fc5d6883 | Fail | 기술 용어와 이름이 겹치는 무관한 기업 정보를 선택했다. | query-6의 10위는 Clifford 업체의 연락처 형식 정보다. https://rocketreach.co/clifford-partitioning-co-ltd-email-format_b4678ca1fc5d6883 은 데이터 분할 방법과 관련이 없고 같은 결과에 직접적인 공간 기술 자료가 있다. 접근 차단으로 문서 ID·문장 번호는 없다. |
| 39 | fetch:https://www.uber.com/global/en/careers/list/148438 | Fail | 기술 본문 근거가 확인되지 않는 채용 공고를 불필요하게 선택했다. | query-1 보완 검색의 1위는 매칭·인덱싱 팀 관리자 채용 공고다. https://www.uber.com/global/en/careers/list/148438 은 팀 명칭만으로 핵심 품질 동작을 설명하는 문서임이 확인되지 않는다. 저장된 다른 검색에 실제 공간 검색·배정 기술 문서가 있다. 404 오류로 문서 ID·본문 문장 번호는 없다. |
| 40 | fetch:https://www.uber.com/global/ne/careers/list/148438 | Fail | 기술 근거가 약한 동일 채용 공고의 지역 URL을 중복 선택했다. | query-1 보완 검색의 2위는 같은 공고 번호와 제목의 지역 변형이다. https://www.uber.com/global/ne/careers/list/148438 은 영어 지역판과 동일한 채용 경로로 이동했다. 중복 수집 이유가 없으며 404 오류로 문서 ID·본문 문장 번호는 없다. |
| 41 | fetch:https://www.instagram.com/reel/DWv9hpGKtVi | Fail | 관련성과 게시자를 확인할 수 없는 일반 제목의 결과를 선택했다. | query-2 보완 검색의 3위는 제목이 Instagram일 뿐 기술 주제와 게시자가 확인되지 않는다. https://www.instagram.com/reel/DWv9hpGKtVi 보다 같은 검색의 Uber 공식 글과 작성자 명시 설계 해설이 적합하다. 수집 본문이 비어 문서 ID·문장 번호는 없다. |
| 42 | fetch:https://www.thepmrepo.com/job-board/lyft--product-manager-matching-and-fulfillment--0b7fc6fd-f2da-4061-8890-e6de630f6238 | Fail | 후보의 기술 조건을 검증할 근거가 부족한 채용 목록을 선택했다. | query-1 보완 검색의 4위는 Lyft 제품 관리자 채용 항목이다. https://www.thepmrepo.com/job-board/lyft--product-manager-matching-and-fulfillment--0b7fc6fd-f2da-4061-8890-e6de630f6238 은 매칭 직무명 외에 핵심 품질 동작의 기술 근거가 확인되지 않는다. TLS 오류로 문서 ID·본문 문장 번호는 없다. |
| 43 | fetch:https://thepmrepo.com/job-board/lyft--product-manager-matching-and-fulfillment--0b7fc6fd-f2da-4061-8890-e6de630f6238 | Fail | 동일 채용 항목의 호스트 별칭을 불필요하게 중복 선택했다. | query-1 보완 검색의 5위는 앞선 채용 항목과 경로·식별자가 동일하다. https://thepmrepo.com/job-board/lyft--product-manager-matching-and-fulfillment--0b7fc6fd-f2da-4061-8890-e6de630f6238 을 추가 수집할 근거가 없으며 기술 관련성도 약하다. TLS 오류로 문서 ID·본문 문장 번호는 없다. |
| 44 | fetch:https://www.tealhq.com/job/product-manager-matching-fulfillment_7ea1a8d69608734bf535606d6210e9c94c6d2 | Fail | 기술 동작 검증보다 채용 안내에 해당하는 출처를 선택했다. | query-1 보완 검색의 7위는 Lyft 매칭 제품 관리자 채용 공고다. https://www.tealhq.com/job/product-manager-matching-fulfillment_7ea1a8d69608734bf535606d6210e9c94c6d2 은 요청 보존·검색 지연·배정 경합의 기술 근거가 검색 기록에 없다. 410 오류로 문서 ID·본문 문장 번호는 확보되지 않았다. |

## 5-1 본문 수집의 유효성

### 당시 문서에 명시된 판정 기준

- Pass: 선택한 문서의 실제 본문을 정상적으로 수집하여 후속 근거 확인에 사용할 수 있다.
- Fail: 본문 대신 검색 요약이나 다른 문서 내용을 수집하고 정상적인 본문으로 처리한다.

판단 불가/실행 오류: 접근 차단·타임아웃 등으로 본문 수집에 실패한 경우는 별도로 기록한다.

### 모든 Fail과 판단 불가 원문

| 번호 | 평가 대상 | 판정 | 실제 적용한 기준 원문 | 판단 근거 원문 |
| --- | --- | --- | --- | --- |
| 1 | doc-f176155bc33c4c6f8fe0ce476b85a570 | Fail | 선택한 문서 대신 일반 문서 홈페이지 내용을 정상 문서로 수집했다. | doc-f176155bc33c4c6f8fe0ce476b85a570, https://docs.confluent.io/legacy/platform/5.1.4/security/compliance.html 의 선택 경로는 과거 보안 준수 문서지만 문장 0~18, 100~116은 일반 제품·개발 문서 목록이다. 원래 선택 문서의 본문이 아닌데 정상 수집 문서로 남았다. |
| 2 | doc-318cd257d9aa4712a508dd99ca9a52bb | 판단 불가 | 접근 차단으로 인한 본문 미수집은 실행 문제로 분리한다. | doc-318cd257d9aa4712a508dd99ca9a52bb, https://www.mapquest.com/us/oklahoma/driver-dispatch-425362787 문장 0~2는 자바스크립트 기반 로봇 검증 안내뿐이다. 실제 업체 본문은 확보되지 않았으며 접근 차단이 명시되어 품질 실패와 별도로 기록한다. |
| 3 | doc-a96f172cc8044a309817bdf8ce153071 | Fail | 기술 본문 대신 탐색·홍보 문구만 수집하고 정상 문서로 남겼다. | doc-a96f172cc8044a309817bdf8ce153071, https://wherobots.com/discover/h3 문장 0에는 본문 건너뛰기와 제휴 홍보만 있다. H3 설명 본문이 없는데 정상 수집 문서로 기록되었고 접근 차단·타임아웃 등의 명시적 실행 오류도 없다. |
| 4 | fetch:https://levelup.gitconnected.com/idempotent-producer-in-kafka-6b53e7394831 | 판단 불가 | 접근 차단으로 인한 수집 실패는 품질 판정에서 제외한다. | fetch_failures의 https://levelup.gitconnected.com/idempotent-producer-in-kafka-6b53e7394831 에 1회 요청 후 HTTP 403 오류가 기록되어 있다. 실제 본문·문서 ID·문장 번호가 없어 수집 내용의 유효성은 판단할 수 없다. |
| 5 | fetch:https://medium.com/versent-tech-blog/geospatial-indexing-and-partitioning-in-grid-systems-b7b9c310bfb0 | 판단 불가 | 접근 차단으로 인한 수집 실패는 품질 판정에서 제외한다. | fetch_failures의 https://medium.com/versent-tech-blog/geospatial-indexing-and-partitioning-in-grid-systems-b7b9c310bfb0 에 1회 요청 후 HTTP 403이 기록되어 있다. 실제 본문·문서 ID·문장 번호는 확보되지 않았다. |
| 6 | fetch:https://www.zoominfo.com/c/h3-engineering-solutions/453657234 | 판단 불가 | 부적합한 출처 선정과 접근 오류를 분리한다. | fetch_failures의 https://www.zoominfo.com/c/h3-engineering-solutions/453657234 에 HTTP 403이 기록되어 있다. 선정 관련성은 별도 실패지만 실제 본문을 수집하지 못한 실행 문제에는 문서 ID·문장 번호가 없어 품질 판정을 부여하지 않는다. |
| 7 | fetch:https://www.virtualshareholdermeeting.com | 판단 불가 | 명시된 본문 공백 수집 오류는 실행 문제로 분리한다. | fetch_failures의 https://www.virtualshareholdermeeting.com 에 본문이 비었다는 실패가 명시되어 있다. 정상 본문으로 처리한 기록은 없으며 문서 ID·문장 번호도 없어 수집 품질 판정에서 제외한다. |
| 8 | fetch:https://stackoverflow.com/questions/60283718/difference-between-kafka-idempotent-and-transactional-producer-setup | 판단 불가 | 접근 차단으로 인한 수집 실패는 품질 판정에서 제외한다. | fetch_failures의 https://stackoverflow.com/questions/60283718/difference-between-kafka-idempotent-and-transactional-producer-setup 에 HTTP 403이 기록되어 있다. 본문·문서 ID·문장 번호가 없어 기술 질의의 실제 수집 결과를 검토할 수 없다. |
| 9 | fetch:https://www.indeed.com/q-kafka-apache-jobs.html | 판단 불가 | 출처 적합성과 별개로 접근 차단은 실행 문제로 분리한다. | fetch_failures의 https://www.indeed.com/q-kafka-apache-jobs.html 에 HTTP 403이 기록되어 있다. 실제 본문·문서 ID·문장 번호가 없으므로 채용 목록 선정의 부적합성을 수집 오류의 품질 점수로 중복 처리하지 않는다. |
| 10 | fetch:https://medium.com/@mohanmmohadikar/partitioning-and-sharding-in-mongodb-a-senior-engineers-perspective-3fb7985047c7 | 판단 불가 | 접근 차단으로 인한 수집 실패는 품질 판정에서 제외한다. | fetch_failures의 https://medium.com/@mohanmmohadikar/partitioning-and-sharding-in-mongodb-a-senior-engineers-perspective-3fb7985047c7 에 HTTP 403이 기록되어 있다. 본문·문서 ID·문장 번호가 없어 실제 기술 내용의 수집 유효성은 판단할 수 없다. |
| 11 | fetch:https://rocketreach.co/grw-engineering-architecture-geospatial-profile_b5e37b84f42e6d54 | 판단 불가 | 출처 적합성과 별개로 접근 차단은 실행 문제로 분리한다. | fetch_failures의 https://rocketreach.co/grw-engineering-architecture-geospatial-profile_b5e37b84f42e6d54 에 HTTP 403이 기록되어 있다. 문서 ID·본문·문장 번호가 없으므로 수집 내용의 대체 여부를 판단할 수 없다. |
| 12 | fetch:https://www.investing.com/news/technology-news/uber-expands-into-spanish-tourist-hotspot-1440319 | 판단 불가 | 출처 적합성과 별개로 접근 차단은 실행 문제로 분리한다. | fetch_failures의 https://www.investing.com/news/technology-news/uber-expands-into-spanish-tourist-hotspot-1440319 에 HTTP 403이 기록되어 있다. 실제 기사 본문·문서 ID·문장 번호는 확보되지 않았다. |
| 13 | fetch:https://www.wwt.com | 판단 불가 | 명시된 본문 공백 수집 오류는 실행 문제로 분리한다. | fetch_failures의 https://www.wwt.com 에 본문이 비었다는 실패가 명시되어 있다. 정상 문서로 받아들인 본문이 없으며 문서 ID·문장 번호도 확보되지 않아 품질 판정에서 제외한다. |
| 14 | fetch:https://rocketreach.co/clifford-partitioning-co-ltd-email-format_b4678ca1fc5d6883 | 판단 불가 | 출처 적합성과 별개로 접근 차단은 실행 문제로 분리한다. | fetch_failures의 https://rocketreach.co/clifford-partitioning-co-ltd-email-format_b4678ca1fc5d6883 에 HTTP 403이 기록되어 있다. 문서 ID·실제 본문·문장 번호가 없어 수집 유효성의 품질 판단은 하지 않는다. |
| 15 | fetch:https://www.uber.com/global/en/careers/list/148438 | 판단 불가 | 이동된 대상의 HTTP 오류로 본문을 받지 못한 경우 실행 문제로 분리한다. | fetch_failures의 https://www.uber.com/global/en/careers/list/148438 은 https://jobs.uber.com/en/jobs/148438/ 로 이동한 뒤 HTTP 404를 반환했다. 문서 ID·본문·문장 번호가 없어 수집 품질을 판단할 수 없다. |
| 16 | fetch:https://www.uber.com/global/ne/careers/list/148438 | 판단 불가 | 중복 선정과 별개로 HTTP 오류는 실행 문제로 분리한다. | fetch_failures의 https://www.uber.com/global/ne/careers/list/148438 도 https://jobs.uber.com/en/jobs/148438/ 로 이동한 뒤 HTTP 404를 반환했다. 실제 본문·문서 ID·문장 번호는 없다. |
| 17 | fetch:https://www.instagram.com/reel/DWv9hpGKtVi | 판단 불가 | 명시된 본문 공백 수집 오류는 실행 문제로 분리한다. | fetch_failures의 https://www.instagram.com/reel/DWv9hpGKtVi 에 본문이 비었다는 실패가 기록되어 있다. 빈 내용을 정상 본문으로 취급한 기록은 없고 문서 ID·문장 번호도 없어 실행 문제로 남긴다. |
| 18 | fetch:https://medium.com/@shesh.soft/kafka-idempotent-producer-and-consumer-25c52402ceb9 | 판단 불가 | 접근 차단으로 인한 수집 실패는 품질 판정에서 제외한다. | fetch_failures의 https://medium.com/@shesh.soft/kafka-idempotent-producer-and-consumer-25c52402ceb9 에 HTTP 403이 기록되어 있다. 실제 기술 본문·문서 ID·문장 번호가 없어 수집 결과의 유효성을 판단할 수 없다. |
| 19 | fetch:https://www.thepmrepo.com/job-board/lyft--product-manager-matching-and-fulfillment--0b7fc6fd-f2da-4061-8890-e6de630f6238 | 판단 불가 | 연결 보안 협상 오류는 품질 판정과 분리한다. | fetch_failures의 https://www.thepmrepo.com/job-board/lyft--product-manager-matching-and-fulfillment--0b7fc6fd-f2da-4061-8890-e6de630f6238 에 2회 요청 후 TLS 협상 실패가 기록되어 있다. 본문·문서 ID·문장 번호는 확보되지 않았다. |
| 20 | fetch:https://thepmrepo.com/job-board/lyft--product-manager-matching-and-fulfillment--0b7fc6fd-f2da-4061-8890-e6de630f6238 | 판단 불가 | 연결 보안 협상 오류는 품질 판정과 분리한다. | fetch_failures의 https://thepmrepo.com/job-board/lyft--product-manager-matching-and-fulfillment--0b7fc6fd-f2da-4061-8890-e6de630f6238 에 2회 요청 후 TLS 협상 실패가 기록되어 있다. 중복 출처 선정 문제와 별개로 문서 ID·본문 문장 번호가 없는 실행 오류다. |
| 21 | fetch:https://www.tealhq.com/job/product-manager-matching-fulfillment_7ea1a8d69608734bf535606d6210e9c94c6d2 | 판단 불가 | 대상 소멸에 따른 HTTP 오류는 실행 문제로 분리한다. | fetch_failures의 https://www.tealhq.com/job/product-manager-matching-fulfillment_7ea1a8d69608734bf535606d6210e9c94c6d2 에 HTTP 410이 기록되어 있다. 선택 페이지의 실제 본문·문서 ID·문장 번호가 없어 수집 품질 판정은 하지 않는다. |
