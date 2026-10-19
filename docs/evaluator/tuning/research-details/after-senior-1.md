# 수정 후 Senior 1회 평가 상세

새로 생성한 Research 결과를 평가한 실행이다.

[주요 실험 기록](../research-tuning.md) · [원본 JSON](../../../../.archgen/m7-followup/current-criteria-20261019/research-tuning/after/senior/1-evaluation/research.json) · [당시 평가 기준](../../../../.archgen/m7-followup/current-criteria-20261019/research-tuning/after/senior/1-evaluation/research-criteria.md) · [Trace](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/648cc8b2e8294b6bb5abe64f41189e6b)

전체 107건: Pass 84 · Fail 17 · 판단 불가 6. 아래 표에는 모든 Fail과 판단 불가를 생략 없이 기록했다. Pass도 기준별 개수를 표시하며 개별 근거는 원본 JSON에 보존한다.

## 기준별 전체 집계

| 평가 기준 | Pass | Fail | 판단 불가 |
| --- | --- | --- | --- |
| 1-1 평가 초점 반영 | 1 | 0 | 0 |
| 1-2 후보 도출의 타당성 | 5 | 0 | 0 |
| 2-1 후보 검증에 적합한 쿼리 | 5 | 0 | 0 |
| 3-1 검색 결과의 관련성 | 7 | 1 | 0 |
| 4-1 출처 선정의 타당성 | 29 | 14 | 0 |
| 5-1 본문 수집의 유효성 | 35 | 2 | 6 |
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
| 1 | call_MyAHqkzLQO1meUbqY3F4czul | Fail | 검증 가능한 후보가 없는 무관한 결과를 선별 없이 후속 수집 대상으로 취급했다. | 이 query-5 실행의 1–9위는 민족 소개, 웹 서버, 재단·개발 도구, 복제 제품 페이지로 치우쳤다. https://en.wikipedia.org/wiki/Apache와 https://httpd.apache.org/download.cgi 등도 실제 수집했다. doc-b50c7ea424e6439694d2b1ecc86e6cd1 문장 1–8은 Kafka 요청 보존과 무관하다. 후속 재검색의 회복은 별도 실행으로 평가한다. |

## 4-1 출처 선정의 타당성

### 당시 문서에 명시된 판정 기준

- Pass: 검색 결과 중 설계 범위와 후보 검증에 관련되고 게시 주체를 식별할 수 있는 문서를 선택한다. 동일 내용의 중복 URL이나 근거가 부족한 목록·홍보 페이지를 불필요하게 우선하지 않는다.
- Fail: 관련성이나 출처를 확인하지 않은 채 무관한·중복된·본문 근거가 없는 문서를 선택하고, 검색 결과에 있던 더 적절한 출처를 뚜렷한 이유 없이 제외한다.

공식 출처가 아니라는 이유만으로 Fail하지 않는다. 이 평가는 저장된 검색 결과에서 실제 선택 가능한 문서를 기준으로 한다.

### 모든 Fail과 판단 불가 원문

| 번호 | 평가 대상 | 판정 | 실제 적용한 기준 원문 | 판단 근거 원문 |
| --- | --- | --- | --- | --- |
| 1 | doc-b50c7ea424e6439694d2b1ecc86e6cd1 | Fail | 제목·내용상 무관한 문서를 본문 수집 대상으로 선택했다. | 초기 query-5의 1위 https://en.wikipedia.org/wiki/Apache는 민족 소개 문서다. 문장 1–8은 인구·언어·역사를 다루며 Kafka 복제나 호출 재처리를 검증하지 못한다. 출처는 식별되지만 관련성이 없다. |
| 2 | doc-257d17c97c7c44a8afadf23b6fb4f591 | Fail | 후보의 설계 문제를 검증할 근거가 부족한 제품 홍보 페이지를 선택했다. | 초기 query-5의 2위 https://www.ibm.com/products/data-replication은 기업 데이터 복제 제품 페이지다. 문장 0–18은 제품 기능·지원 대상·고객 사례이며 배차 요청 확인 응답, 오프셋 복구, 멱등 처리의 조건을 제시하지 않는다. |
| 3 | doc-ee843903131c4b7cbcdecaeb7a62b5be | Fail | 후보와 무관한 기술의 일반 소개를 선택했다. | 초기 query-5의 3위 https://www.geeksforgeeks.org/linux-unix/what-is-apache-server는 웹 서버 소개다. 문장 0–5·17–25의 HTTP 처리 설명은 Kafka 기반 호출 보존·재처리 문제와 연결되지 않는다. |
| 4 | doc-f29e7bea971f4d8798be1e7055969ac3 | Fail | 공식 출처라도 후보와 무관한 문서를 선택하면 실패다. | 초기 query-5의 4위 https://httpd.apache.org는 Apache 웹 서버 홈페이지다. 문장 0–11은 서버 소개·릴리스·설치 안내로, Kafka 요청 내구성이나 재처리 근거가 아니다. |
| 5 | doc-3562c739879c495f899cb2a7f4a6915f | Fail | 관련성이 없는 다른 시스템의 소개 문서를 선택했다. | 초기 query-5의 5위 https://en.wikipedia.org/wiki/Apache_HTTP_Server는 웹 서버 백과사전 문서다. 문장 1–4·33–50은 웹 서버 기능과 성능이며, 계획한 Kafka 복제·오프셋·재전달 검증과 무관하다. |
| 6 | doc-f3f97e527f4d4e15acfebba6cb3728ca | Fail | 후보 검증 본문이 없는 무관한 다운로드 페이지를 선택했다. | 초기 query-5의 6위 https://httpd.apache.org/download.cgi는 웹 서버 배포 파일 안내다. 문장 0–11·15–28에 Kafka 또는 배차 요청 보존 설계의 근거가 없다. |
| 7 | doc-f0ab73559e1d4fed9c29dc79d549d55c | Fail | 구체적 근거가 부족한 일반 소개·목록을 더 적절한 문서와 구별하지 않고 선택했다. | query-6의 5위 https://eng.uber.com은 기술 블로그 홈페이지다. 문장 0–16은 일반 원칙이고 이후는 여러 무관한 글의 목록이다. 같은 결과 6·7위에는 Gairos와 이행 플랫폼의 구체적 문서가 있어 홈페이지 자체의 수집 필요성이 약하다. |
| 8 | doc-adbe96975f1d477f937f2c4b1d4543e5 | Fail | 후보의 기술적 근거가 없는 일반 조직 홍보 페이지를 선택했다. | 초기 query-5의 7위 https://www.apache.org는 재단 홈페이지다. 문장 0–8은 재단·커뮤니티·후원 소개이며 Kafka 복제, 오프셋 또는 호출 재처리의 조건을 설명하지 않는다. |
| 9 | doc-21665141719948cba1a313a7d940b240 | Fail | 설계 범위와 무관한 제품의 배포 페이지를 선택했다. | 초기 query-5의 9위 https://netbeans.apache.org/front/main/download는 NetBeans 배포 안내다. 문장 0–4의 릴리스 주기·빌드 정보는 차량 매칭 후보 검증과 무관하다. |
| 10 | doc-93f62e7ecba44e379f27f92b89e29b63 | Fail | 검색 결과에 더 적절한 출처가 있는데 명백히 무관한 문서를 선택했다. | query-6의 9위 https://www.careoregonadvantage.org/about-us/agent-resources는 보험 모집인 자료다. 문장 0–12는 교육·영업·보험 안내다. 같은 결과의 Uber 기술 글·인터뷰와 달리 설계 범위나 NFR 검증과 연결되지 않는다. |
| 11 | doc-9047f4ed545446d294c63fd69e0be43e | Fail | 설계 문제와 무관한 일반 제품 뉴스를 선택했다. | query-6의 10위인 doc-9047f4ed545446d294c63fd69e0be43e는 https://hk.finance.yahoo.com의 Gemini 언어 지원 기사다. 문장 0–4는 음성 대화·앱 연동 소개이며 주변 검색, 배정, 위치 수집 확장과 무관하다. |
| 12 | doc-72caa1a5391a486595d6d8c4d11cbac6 | Fail | 동음 명칭을 가진 무관한 회사 정보 페이지를 선택했다. | query-5 재검색의 6위 https://tracxn.com/d/venture-capital/acks/__DcNgXQleXxIdwoYvZD8Aod_8n4gfySqgapryu1S-2wc는 투자회사 정보다. 문장 0–4의 Acks는 Kafka 설정이 아니다. 같은 결과 1–5위에 관련 기술 출처가 있었다. |
| 13 | fetch:https://www.instagram.com/popular/uber-dispatch-system-architecture-diagram | Fail | 작성 주체와 본문 근거가 불분명한 목록 페이지를 불필요하게 선택했다. | query-6의 2위 https://www.instagram.com/popular/uber-dispatch-system-architecture-diagram은 개별 기술 문서가 아닌 인기 항목 목록 경로다. 검색 기록에 구체적 작성자·근거가 없고, 같은 결과에 기술 글과 Uber 공식 문서·인터뷰가 있었다. 수집 본문도 없어 문장 번호는 없다. |
| 14 | fetch:https://www.britannica.com/topic/Apache-people | Fail | 출처의 신뢰도와 무관하게 설계 주제와 관계없는 문서를 선택했다. | 초기 query-5의 8위 https://www.britannica.com/topic/Apache-people는 제목·경로상 민족의 역사·문화 문서다. Kafka 확인 응답·복제·재처리와 무관하다. 403으로 본문 문장 번호는 없지만 선정의 무관련성은 검색 기록에서 확인된다. |

## 5-1 본문 수집의 유효성

### 당시 문서에 명시된 판정 기준

- Pass: 선택한 문서의 실제 본문을 정상적으로 수집하여 후속 근거 확인에 사용할 수 있다.
- Fail: 본문 대신 검색 요약이나 다른 문서 내용을 수집하고 정상적인 본문으로 처리한다.

판단 불가/실행 오류: 접근 차단·타임아웃 등으로 본문 수집에 실패한 경우는 별도로 기록한다.

### 모든 Fail과 판단 불가 원문

| 번호 | 평가 대상 | 판정 | 실제 적용한 기준 원문 | 판단 근거 원문 |
| --- | --- | --- | --- | --- |
| 1 | doc-b2321e3e2202402482c836d54f7e39cc | Fail | 실제 기술 본문이 아닌 공통 안내만을 정상 수집 문서로 저장했다. | https://wherobots.com/discover/h3의 저장 문장 0은 건너뛰기 링크와 제휴 안내뿐이다. H3 설명 본문이 전혀 없는데 정상 fetched 항목으로 기록됐다. 별도의 접근 오류 기록도 없어 정상 본문 수집으로 인정할 수 없다. |
| 2 | doc-762c6533eef54e9d9f0edabbe33b2ddc | Fail | 발표 본문 대신 플랫폼 공통 안내를 정상 수집 항목으로 저장했다. | https://www.youtube.com/watch?v=M3o3KIJuyaw의 문장 0–1은 저작권·사업자·상품 책임 안내뿐이다. H3 발표 설명이나 자막은 없으며 별도 수집 실패가 아닌 정상 fetched 항목으로 기록돼 후속 기술 근거로 사용할 수 없다. |
| 3 | fetch:https://medium.com/codetodeploy/uber-architecture-part-5-the-dispatch-engine-and-map-rendering-64ac669fa698 | 판단 불가 | 접근 차단으로 인한 수집 실패는 실행 오류로 분리한다. | fetch_failures의 https://medium.com/codetodeploy/uber-architecture-part-5-the-dispatch-engine-and-map-rendering-64ac669fa698에 1회 요청의 HTTP 403이 기록됐다. 실제 본문과 문장 번호가 없어 수집 품질을 판정할 수 없으며 정상 수집으로 가장한 기록은 없다. |
| 4 | fetch:https://docs.redhat.com/en/documentation/red_hat_streams_for_apache_kafka/2.7/html/kafka_configuration_tuning/con-producer-config-properties-str | 판단 불가 | 접근 차단은 품질 실패와 구분해 실행 오류로 기록한다. | fetch_failures의 https://docs.redhat.com/en/documentation/red_hat_streams_for_apache_kafka/2.7/html/kafka_configuration_tuning/con-producer-config-properties-str에 HTTP 403이 기록됐다. 본문·문장 번호가 없으며 실패를 정상 본문으로 처리한 정황은 없다. |
| 5 | fetch:https://www.instagram.com/popular/uber-dispatch-system-architecture-diagram | 판단 불가 | 명시적으로 기록된 본문 수집 실패는 실행 오류로 분리한다. | fetch_failures의 https://www.instagram.com/popular/uber-dispatch-system-architecture-diagram에는 본문이 비어 있다는 실패가 저장됐다. 본문 문장 번호가 없어 유효한 내용의 수집 여부를 판정할 수 없다. 출처 선정의 부적합성과는 별개다. |
| 6 | fetch:https://medium.com/@anjalimishraa17/high-level-design-part-7-design-uber-3645afc8396b | 판단 불가 | 접근 차단으로 본문을 확보하지 못한 경우 실행 오류로 기록한다. | fetch_failures의 https://medium.com/@anjalimishraa17/high-level-design-part-7-design-uber-3645afc8396b에 1회 요청의 HTTP 403이 있다. 실제 본문·문장 번호가 없으므로 판단 불가이며 다른 내용을 정상 본문으로 대신 저장한 기록은 없다. |
| 7 | fetch:https://www.britannica.com/topic/Apache-people | 판단 불가 | 출처 선정 실패와 접근 차단에 의한 실행 오류를 구분한다. | fetch_failures의 https://www.britannica.com/topic/Apache-people에 HTTP 403이 기록됐다. 실제 본문·문장 번호가 없어 본문 수집의 품질은 판정 불가다. 검색 제목상 주제가 무관하다는 선정 실패와는 별도다. |
| 8 | fetch:https://kafka.apache.org/22/generated/producer_config.html | 판단 불가 | 본문이 비어 있다고 명시된 수집 실패는 실행 오류로 분리한다. | fetch_failures의 https://kafka.apache.org/22/generated/producer_config.html에 빈 본문 실패가 기록됐다. 실제 본문과 문장 번호가 없고 정상 문서로 대체 처리하지 않았으므로 품질 실패 점수를 부여하지 않는다. |
