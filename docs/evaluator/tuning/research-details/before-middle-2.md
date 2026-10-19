# 수정 전 Middle 2회 평가 상세

새로 생성한 Research 결과를 평가한 실행이다.

[주요 실험 기록](../research-tuning.md) · [원본 JSON](../../../../.archgen/m7-followup/current-criteria-20261019/research-tuning/before/middle/2-evaluation/research.json) · [당시 평가 기준](../../../../.archgen/m7-followup/current-criteria-20261019/research-tuning/before/middle/2-evaluation/research-criteria.md) · [Trace](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/5e4a184b746b408aaf8d19add4f45653)

전체 125건: Pass 64 · Fail 35 · 판단 불가 26. 아래 표에는 모든 Fail과 판단 불가를 생략 없이 기록했다. Pass도 기준별 개수를 표시하며 개별 근거는 원본 JSON에 보존한다.

## 기준별 전체 집계

| 평가 기준 | Pass | Fail | 판단 불가 |
| --- | --- | --- | --- |
| 1-1 평가 초점 반영 | 1 | 0 | 0 |
| 1-2 후보 도출의 타당성 | 5 | 0 | 0 |
| 2-1 후보 검증에 적합한 쿼리 | 5 | 0 | 0 |
| 3-1 검색 결과의 관련성 | 8 | 2 | 0 |
| 4-1 출처 선정의 타당성 | 17 | 33 | 1 |
| 5-1 본문 수집의 유효성 | 26 | 0 | 25 |
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
| 1 | call_QPaJZ2FCbyrdWA8zbaGMzyGd | Fail | 반환 결과에 후보 검증에 사용할 관련 문서 후보가 없다. | query-3에 유일하게 반환된 URL https://www.uber.com/blog/engineering?id=879는 일반 분류 페이지다. 문서 doc-71da9c64c298497190c3c9a7a15974c1의 문장 0~28도 메뉴뿐이며 중복 배정·동시성 자료를 식별하지 못한다. 검색 서비스 오류 기록은 없다. |
| 2 | call_sTJJevk1CdJ5tqQUst0sW6jR | Fail | 반환 결과가 다른 주제여서 후보 검증용 문서가 없다. | query-3의 후속 검색은 행사 이용약관인 https://www.uber.com/blog/preds-experience-terms-conditions 한 건만 반환했다. 배정 일관성이나 동시성 관련 후보가 없으며 검색 결과 문장 번호는 미부여다. 이후 수집의 404 오류는 별도 실행 오류다. |

## 4-1 출처 선정의 타당성

### 당시 문서에 명시된 판정 기준

- Pass: 검색 결과 중 설계 범위와 후보 검증에 관련되고 게시 주체를 식별할 수 있는 문서를 선택한다. 동일 내용의 중복 URL이나 근거가 부족한 목록·홍보 페이지를 불필요하게 우선하지 않는다.
- Fail: 관련성이나 출처를 확인하지 않은 채 무관한·중복된·본문 근거가 없는 문서를 선택하고, 검색 결과에 있던 더 적절한 출처를 뚜렷한 이유 없이 제외한다.

공식 출처가 아니라는 이유만으로 Fail하지 않는다. 이 평가는 저장된 검색 결과에서 실제 선택 가능한 문서를 기준으로 한다.

### 모든 Fail과 판단 불가 원문

| 번호 | 평가 대상 | 판정 | 실제 적용한 기준 원문 | 판단 근거 원문 |
| --- | --- | --- | --- | --- |
| 1 | doc-4d1159d0a28e42719842e47a326c30bd | Fail | 설계 범위 밖의 문서를 관련성 설명 없이 수집 대상으로 선택했다. | 대상 URL https://www.uber.com/blog/uber-beacon-bluetooth-mobile-app의 문장 55~65는 배정 수락 이후 색상으로 승객과 차량을 식별하는 기능이다. 호출 접수부터 배정 확정까지의 평가 초점과 다르며, 같은 검색의 호출 제안 표시 문서보다 이 자료가 필요한 이유가 없다. |
| 2 | doc-7a4e23b626e04b0db897baec221838ac | Fail | 일반적인 다른 설계 주제를 후보 검증과 연결하지 않고 선택했다. | 대상 URL https://www.uber.com/blog/driver-app-ribs-architecture?ref=highscalability.com의 문장 15·59·96~104는 앱 모듈화와 개발 조직의 확장·절충이 중심이다. 주변 검색 지연, 중복 배정, 위치 수집 또는 요청 보존을 검증하는 데 이 일반 앱 구조가 필요한 연결 설명은 없다. |
| 3 | doc-71da9c64c298497190c3c9a7a15974c1 | Fail | 후보 검증 본문이 없는 일반 페이지를 선택했다. | 대상 URL https://www.uber.com/blog/engineering?id=879는 query-3의 유일한 일반 분류 결과다. 문장 0~28은 메뉴이고 중복 배정이나 원자적 예약 관련 문서가 아니다. 관련성 확인 없이 일관성 조사 대상으로 수집했다. |
| 4 | doc-fd219b48e92546e0b94c15da59d68c72 | Fail | 개별 기술 문서 대신 근거가 부족한 목록 페이지를 불필요하게 선택했다. | 대상 URL https://www.uber.com/blog/engineering/page/3의 문장 0~27은 분류·날짜 목록이다. query-4에는 역압과 수집 관련 개별 기사도 있었지만 이 목록을 후보 검증용으로 추가 수집할 이유는 기록되지 않았다. |
| 5 | doc-4ac3babc39c04be587ba03f64022f05c | Fail | 개별 근거 없이 일반 목록 페이지를 선택했다. | 대상 URL https://www.uber.com/blog/engineering의 문장 0~28은 사이트 메뉴다. query-5의 H3 개별 글과 달리 공간 샤딩·핫스폿을 확인할 특정 본문이 없으며, 유사한 분류 URL도 반복 수집했다. |
| 6 | doc-c4596d512eb3456780528294f37358d2 | Fail | 동일 내용의 중복 URL을 불필요하게 선택했다. | 대상 URL https://www.uber.com/blog/engineering?id=x의 문장 0~28은 doc-4ac3babc39c04be587ba03f64022f05c와 같은 메뉴다. query-5에서 별도 기술 근거가 식별되지 않는 매개변수 변형을 추가 수집할 이유가 없다. |
| 7 | doc-699f164ac483416cbd3bbe11389af59c | Fail | 관련 기술 본문이 확인되지 않는 분류 페이지를 선택했다. | 대상 URL https://www.uber.com/blog/engineering/backend의 문장 0~21은 분류·날짜 목록이다. query-4의 위치 갱신 처리량에 대한 개별 문서가 아니며, 이를 근거 수집 대상으로 삼을 이유가 없다. |
| 8 | doc-f5e600b345fe48f595e65d381a53bb8a | Fail | 근거가 부족한 목록 페이지를 불필요하게 선택했다. | 대상 URL https://www.uber.com/blog/engineering/page/2의 문장 0~27은 분류·날짜 목록이다. query-4에 개별 수집·역압 기사도 반환됐지만 이 목록을 위치 갱신 후보 검증에 사용할 연결 설명은 없다. |
| 9 | doc-04d29c34c6df4518b7c2f9a6f7f57909 | Fail | 동일 내용의 중복 URL을 불필요하게 선택했다. | 대상 URL http://uber.com/blog/engineering의 문장 0~28은 다른 일반 엔지니어링 URL들과 같은 메뉴다. query-5의 공간 확장 자료로서 별도 내용이 없는데도 프로토콜·호스트 변형을 추가 수집했다. |
| 10 | doc-d53a3ecb5622414f820328f9db95274d | Fail | 동일 내용의 중복 URL을 불필요하게 선택했다. | 대상 URL https://www.uber.com/blog/engineering?id=998638의 문장 0~28은 일반 메뉴이며 다른 분류 URL과 동일하다. query-5의 공간 샤딩·핫스폿 관련 개별 본문을 식별하지 못한 선택이다. |
| 11 | doc-02d0878587dc46e5a9a5bd6c76370a62 | Fail | 관련 근거가 없는 중복 페이지를 선택했다. | 대상 URL https://www.uber.com/blog/engineering?uber_client_name=706의 문장 0~28은 동일한 사이트 메뉴다. query-5의 확장성 후보와 연결되는 내용이나 매개변수 변형을 추가 수집할 이유가 없다. |
| 12 | doc-0f94d6be97c24a05a03987ecdff6a210 | Fail | 개별 기술 근거 없는 일반 페이지를 선택했다. | 대상 URL https://www.uber.com/blog/new-york/engineering의 문장 0~28은 일반 메뉴다. query-4의 위치 수집 처리량과 연결되지 않으며, 지역 경로가 다른 엔지니어링 목록을 추가 수집할 필요도 설명되지 않았다. |
| 13 | doc-a4136470d49048ed86f0b7ea40b943a8 | Fail | 설계 범위와 다른 처리 경로의 문서를 연결 설명 없이 선택했다. | 대상 URL https://www.uber.com/blog/streamific-hadoop-ingestion의 문장 4·22~29·74~77은 Hadoop 분석 수집 경로다. 매칭용 최신 위치 인덱스 반영과의 연결이 없으며, 같은 query-4에 반환된 역압 자료와 달리 온라인 매칭 범위에 적용할 이유가 기록되지 않았다. |
| 14 | doc-80ead8d5d6444b849b450a6468acb949 | Fail | 개별 근거 없는 중복 URL을 불필요하게 선택했다. | 대상 URL https://www.uber.com/blog/engineering?id=50의 문장 0~28은 일반 메뉴다. query-5의 다른 엔지니어링 매개변수 URL들과 동일한 내용이며 공간 확장성 검증에 추가되는 근거가 없다. |
| 15 | doc-375186f9d6474ebd85df25a00dd46848 | Fail | 개별 근거 없는 중복 URL을 불필요하게 선택했다. | 대상 URL https://www.uber.com/blog/engineering?id=26의 문장 0~28은 다른 엔지니어링 목록과 같은 메뉴다. query-5의 공간 분할·핫스폿 관련 기술 본문을 확인할 선택이 아니다. |
| 16 | doc-1a2ef1c5a9284c7ab3a9f86abe922ba3 | Fail | 관련성 없는 매개변수 변형과 중복 페이지를 선택했다. | 대상 URL https://www.uber.com/blog/engineering?id=118%2Cwww.uber.com%2Fnz%2Fen%2Fcareers%2Fdesign%2Cuber.com%2C0.33170733의 문장 0~28은 일반 메뉴다. query-5에서 이 복잡한 매개변수가 공간 확장 관련 개별 문서를 가리킨다는 근거는 없다. |
| 17 | doc-2d22d1736b8e4531873ad7bff96449a1 | Fail | 개별 기술 근거가 없는 목록 페이지를 선택했다. | 대상 URL https://www.uber.com/blog/engineering/page/34의 문장 0~28은 일반 메뉴다. query-4에는 개별 역압·수집 기사도 있었지만 이 페이지가 위치 갱신 처리량 근거를 제공한다는 설명은 없다. |
| 18 | doc-c93ada97bdb94ec88ae713e73332cc69 | Fail | 관련 근거가 없는 중복 매개변수 URL을 선택했다. | 대상 URL https://www.uber.com/blog/engineering?countryiso2=us%252525252525252525252525252525252525252525252525252525252525252525255Cu0022%3F의 문장 0~28은 동일한 사이트 메뉴다. query-5의 확장성 검증에 필요한 개별 본문이 식별되지 않는다. |
| 19 | doc-1680a8b3f8a942a6bd6a54c2d9cb9621 | 판단 불가 | 관련 제목은 있으나 게시 주체 확인에 필요한 기록이 부족하다. | 대상 URL https://www.youtube.com/watch?v=8wDRlS3vJvc의 검색 제목은 차량 위치 인덱스 설계에 관련된다. 그러나 채널·작성자 기록이 없고 수집된 문장 0~1도 플랫폼 법적 고지뿐이다. 선정 당시 출처 식별의 적절성은 확정할 수 없다. |
| 20 | doc-18a830c2bf98476e8b7ee2b39df5b5f3 | Fail | 온라인 매칭 범위와 다른 분석 시스템 문서를 연결 설명 없이 선택했다. | 대상 URL https://www.uber.com/blog/uber-big-data-platform의 문장 3~5·19~23·65~80은 분석 데이터 웨어하우스·레이크가 중심이다. 같은 검색 순위 5에 실시간 위치 색인 수집 글이 있었는데도 이 분석 플랫폼이 매칭 위치 갱신 검증에 필요한 이유는 없다. |
| 21 | doc-2eb6ac6d43744c698df0a2bc69b8bfa9 | Fail | 설계 범위와 다른 데이터 처리 경로를 관련성 설명 없이 선택했다. | 대상 URL https://www.uber.com/blog/from-batch-to-streaming-accelerating-data-freshness-in-ubers-data-lake의 문장 2~13·48~56은 분석·학습용 데이터 레이크의 분 단위 최신성을 다룬다. 매칭용 위치 인덱스의 온라인 갱신과 연결되지 않으며 같은 검색에 더 직접적인 실시간 색인 글이 있다. |
| 22 | doc-80c4653f7fd4441387323d1f35933c1a | Fail | 범위 밖의 분석 수집 주제를 후보 검증과 연결하지 않고 선택했다. | 대상 URL https://www.uber.com/blog/dbevents-ingestion-framework의 문장 10~18·25~35·75~80은 데이터 레이크로의 변경 수집과 분 단위 최신성을 다룬다. 주변 검색용 최신 위치 상태와의 연결 없이 넓은 데이터 수집 주제로 선택됐다. |
| 23 | doc-c727918541b44f6caf8e75e4338d668b | Fail | 설계 범위 밖의 분석 파이프라인을 연결 설명 없이 선택했다. | 대상 URL https://www.uber.com/blog/marmaray-hadoop-ingestion-open-source의 문장 13~17·23~24·70~86은 Hadoop 분석 수집과 파생 데이터 배포를 다룬다. 매칭 위치 갱신 처리 경로와의 연결이 없고, 같은 검색에 직접 관련된 실시간 위치 색인 글도 반환됐다. |
| 24 | doc-301b272e88c745f0b34486917381216e | Fail | 조사 초점과 다른 기능의 문서를 연결 설명 없이 선택했다. | 대상 URL https://www.uber.com/blog/presto-on-apache-kafka-at-uber-scale의 문장 21~39·89~92는 Kafka 사건의 임시 분석·장애 진단 조회가 중심이다. 위치 갱신 수신·매칭 인덱스 처리량 검증과 연결되지 않으며 같은 검색의 실시간 색인 수집 글보다 우선할 근거가 없다. |
| 25 | doc-44dcdeb610f74a52bef3167b38d32469 | Fail | 평가 초점과 연결되지 않는 다른 품질 주제의 문서를 선택했다. | 대상 URL https://www.uber.com/blog/securing-kafka-infrastructure-at-uber의 문장 5~38은 인증·인가·암호화가 중심이다. rider·driver 사건을 언급하는 문장 4만으로 위치 처리량이나 요청 보존·재처리 검증에 적합해지지는 않으며 보안 후보도 계획에 없다. |
| 26 | fetch:https://www.uber.com/blog/search/pinot | Fail | 관련 개별 문서가 있는데 근거가 부족한 검색 목록을 불필요하게 선택했다. | query-2의 순위 3인 https://www.uber.com/blog/search/pinot는 검색 목록이다. 같은 결과의 순위 1·2에 공간 조회 개별 글이 있었고 목록 추가 수집의 필요성은 없다. 문서 ID·문장 번호는 없으며 이후 404는 선정 품질과 별도다. |
| 27 | fetch:https://eng.uber.com/blog/apache-hudi-at-uber | Fail | 설계 범위와 다른 주제의 문서를 연결 설명 없이 선택했다. | query-4의 순위 1인 https://eng.uber.com/blog/apache-hudi-at-uber는 제목부터 대규모 데이터 레이크 운영 주제다. 온라인 위치 갱신·매칭 인덱스와 연결한 선정 이유가 없다. 문서 ID·본문 문장 번호는 없으며 404 오류 자체를 실패 사유로 삼지 않았다. |
| 28 | fetch:http://eng.uber.com/blog/apache-hudi-at-uber | Fail | 동일 내용의 중복 URL을 불필요하게 선택했다. | query-4의 순위 2인 http://eng.uber.com/blog/apache-hudi-at-uber는 순위 1의 HTTPS 문서와 제목·경로가 같다. 별도 내용이나 재시도 목적의 설명 없이 중복 수집 대상으로 선택했다. 문서 ID·문장 번호는 없고, 오류 기록의 최종 URL도 HTTPS로 동일하다. |
| 29 | fetch:https://www.uber.com/blog/search/data+analytics/page/5 | Fail | 관련 개별 문서 대신 광범위한 목록을 불필요하게 추가 선택했다. | query-2의 순위 4인 https://www.uber.com/blog/search/data+analytics/page/5는 데이터 분석 검색 목록이다. 주변 검색 지연의 개별 기술 근거가 식별되지 않고 같은 결과에는 공간 조회 기사도 있다. 문서 ID·문장 번호는 없으며 404는 별도 실행 오류다. |
| 30 | fetch:https://www.uber.com/blog/search/data+analytics | Fail | 후보 검증 관련성이 부족한 일반 검색 목록을 선택했다. | query-2의 순위 5인 https://www.uber.com/blog/search/data+analytics는 넓은 데이터 분석 목록이다. 주변 운전자 검색의 지연·공간 인덱스 자료로 이 목록이 필요한 설명 없이 개별 기사들과 함께 수집했다. 문서 ID·문장 번호는 없다. |
| 31 | fetch:https://www.uber.com/blog/search/data+analytics/page/2 | Fail | 근거가 부족한 목록 페이지를 불필요하게 선택했다. | query-2의 순위 6인 https://www.uber.com/blog/search/data+analytics/page/2는 분석 검색 목록의 추가 페이지다. 관련 개별 공간 조회 글이 이미 반환됐고 이 페이지에서 검토할 특정 문서를 식별한 기록이 없다. 문서 ID·문장 번호는 없다. |
| 32 | fetch:https://www.uber.com/blog/research | Fail | 후보 검증 본문이 식별되지 않는 일반 페이지를 선택했다. | query-4의 순위 4인 https://www.uber.com/blog/research는 일반 엔지니어링 페이지 제목으로 반환됐다. 위치 갱신 수집에 관한 개별 본문 후보가 아니며 선정 이유도 없다. 문서 ID·문장 번호는 없고 404 오류와는 구분한 판정이다. |
| 33 | fetch:https://www.uber.com/blog/preds-experience-terms-conditions | Fail | 명백히 다른 주제의 문서를 관련성 확인 없이 선택했다. | query-3의 후속 검색에서 반환된 https://www.uber.com/blog/preds-experience-terms-conditions는 행사 이용약관이다. 운전자 중복 배정이나 일관성과 연결되지 않는다. 문서 ID·문장 번호는 없으며 수집의 404 여부와 무관하게 선정이 부적절하다. |
| 34 | fetch:https://www.instagram.com/reel/DWv9hpGKtVi | Fail | 관련 내용과 게시 주체가 확인되지 않은 문서를 선택했다. | call_qkYRCJee7qtTMpJDSoDgnsl6의 순위 4인 https://www.instagram.com/reel/DWv9hpGKtVi는 제목이 플랫폼명뿐이고 게시자·내용 요약도 없다. 같은 결과에 공식 H3와 차량 호출 설계 글이 있는데 이 영상을 선택할 관련성 근거가 없다. 문서 ID·문장 번호는 없다. |

## 5-1 본문 수집의 유효성

### 당시 문서에 명시된 판정 기준

- Pass: 선택한 문서의 실제 본문을 정상적으로 수집하여 후속 근거 확인에 사용할 수 있다.
- Fail: 본문 대신 검색 요약이나 다른 문서 내용을 수집하고 정상적인 본문으로 처리한다.

판단 불가/실행 오류: 접근 차단·타임아웃 등으로 본문 수집에 실패한 경우는 별도로 기록한다.

### 모든 Fail과 판단 불가 원문

| 번호 | 평가 대상 | 판정 | 실제 적용한 기준 원문 | 판단 근거 원문 |
| --- | --- | --- | --- | --- |
| 1 | doc-71da9c64c298497190c3c9a7a15974c1 | 판단 불가 | 메뉴 외 본문이 없어 수집 유효성을 확인할 수 없다. | 대상 URL https://www.uber.com/blog/engineering?id=879의 문장 0~28은 사이트 메뉴뿐이다. 접근 오류 기록은 없지만 기술 본문도 없고, 이를 정상 기술 근거로 사용한 Research 기록도 없어 대체 본문 오인에 따른 실패까지는 확정하지 않는다. |
| 2 | doc-fd219b48e92546e0b94c15da59d68c72 | 판단 불가 | 목록 표지 정보만 있어 기술 본문 수집을 확인할 수 없다. | 대상 URL https://www.uber.com/blog/engineering/page/3의 문장 0~27은 분류와 날짜뿐이다. 검증할 기술 본문이 없으며, 다른 문서나 검색 요약을 정상 본문으로 사용했다고 확인되는 기록도 없다. |
| 3 | doc-4ac3babc39c04be587ba03f64022f05c | 판단 불가 | 사이트 메뉴만 수집돼 기술 본문 확보 여부를 확인할 수 없다. | 대상 URL https://www.uber.com/blog/engineering의 문장 0~28은 메뉴다. 근거 확인에 사용할 기사 본문이 없으나 이를 정상 기술 본문으로 사용한 기록도 없어, 선정 부적절성과 별개로 수집 유효성은 판단을 유보한다. |
| 4 | doc-c4596d512eb3456780528294f37358d2 | 판단 불가 | 메뉴만 남아 실제 기술 본문 수집을 확인할 수 없다. | 대상 URL https://www.uber.com/blog/engineering?id=x의 문장 0~28은 일반 메뉴다. 별도 기사 본문이나 접근 실패 원인이 없으며, 이 메뉴를 기술 근거로 정상 취급한 Research 기록도 없다. |
| 5 | doc-699f164ac483416cbd3bbe11389af59c | 판단 불가 | 분류·날짜 정보만 있어 기술 본문 확보를 확인할 수 없다. | 대상 URL https://www.uber.com/blog/engineering/backend의 문장 0~21에는 기술 설명 없이 분류와 날짜만 있다. 추출의 유효한 기사 본문을 확인할 수 없고 이를 기술 근거로 사용한 기록도 없다. |
| 6 | doc-f5e600b345fe48f595e65d381a53bb8a | 판단 불가 | 목록 표지 정보만 있어 기술 본문 수집을 확인할 수 없다. | 대상 URL https://www.uber.com/blog/engineering/page/2의 문장 0~27은 분류·날짜뿐이다. 개별 기사 본문이 없고 정상 기술 본문으로 취급했다는 기록도 없어 수집 유효성 판정을 유보한다. |
| 7 | doc-04d29c34c6df4518b7c2f9a6f7f57909 | 판단 불가 | 메뉴 외 본문이 없어 기술 근거 수집을 확인할 수 없다. | 대상 URL http://uber.com/blog/engineering의 문장 0~28은 다른 일반 엔지니어링 URL과 같은 메뉴다. 기술 본문이나 명시적 접근 오류가 없고, 메뉴를 기술 근거로 사용한 기록도 없다. |
| 8 | doc-d53a3ecb5622414f820328f9db95274d | 판단 불가 | 사이트 메뉴만 있어 실제 기술 본문 확보를 확인할 수 없다. | 대상 URL https://www.uber.com/blog/engineering?id=998638의 문장 0~28은 메뉴다. 별도 기술 본문이 수집되지 않았으며, 이를 정상 기술 자료로 처리한 Research 기록도 없어 수집 유효성은 확정하지 않는다. |
| 9 | doc-02d0878587dc46e5a9a5bd6c76370a62 | 판단 불가 | 메뉴만 수집되어 기술 본문 유효성을 확인할 수 없다. | 대상 URL https://www.uber.com/blog/engineering?uber_client_name=706의 문장 0~28은 일반 메뉴다. 기술 본문도 접근 실패 원인도 없고, 이를 후보의 실제 기술 근거로 사용한 기록도 없다. |
| 10 | doc-0f94d6be97c24a05a03987ecdff6a210 | 판단 불가 | 사이트 메뉴만 있어 기사 본문 수집을 확인할 수 없다. | 대상 URL https://www.uber.com/blog/new-york/engineering의 문장 0~28은 일반 메뉴다. 기술 본문이 없으며 다른 문서 내용을 정상 근거로 취급한 기록도 없어, 선정 문제와 구분해 수집 유효성은 유보한다. |
| 11 | doc-80ead8d5d6444b849b450a6468acb949 | 판단 불가 | 메뉴 외 본문이 없어 기술 본문 확보 여부를 확인할 수 없다. | 대상 URL https://www.uber.com/blog/engineering?id=50의 문장 0~28은 일반 메뉴다. 개별 기술 본문이 없고 이 내용을 정상 기술 근거로 사용했다는 기록도 없다. |
| 12 | doc-375186f9d6474ebd85df25a00dd46848 | 판단 불가 | 메뉴만 남아 실제 기술 본문 수집을 확인할 수 없다. | 대상 URL https://www.uber.com/blog/engineering?id=26의 문장 0~28은 일반 사이트 메뉴다. 기술 설명도 명시적 접근 오류도 없고, 이를 기술 근거로 정상 처리한 기록도 없다. |
| 13 | doc-1a2ef1c5a9284c7ab3a9f86abe922ba3 | 판단 불가 | 메뉴만 수집되어 기술 본문 유효성을 확인할 수 없다. | 대상 URL https://www.uber.com/blog/engineering?id=118%2Cwww.uber.com%2Fnz%2Fen%2Fcareers%2Fdesign%2Cuber.com%2C0.33170733의 문장 0~28은 일반 메뉴다. 후보 검증 본문이 없고 이를 정상 기술 근거로 사용한 기록도 없다. |
| 14 | doc-2d22d1736b8e4531873ad7bff96449a1 | 판단 불가 | 사이트 메뉴만 있어 기술 본문 수집을 확인할 수 없다. | 대상 URL https://www.uber.com/blog/engineering/page/34의 문장 0~28은 일반 메뉴다. 검증 가능한 기사 본문이 없지만 이 메뉴를 기술적 근거로 정상 사용했다는 기록도 없다. |
| 15 | doc-c93ada97bdb94ec88ae713e73332cc69 | 판단 불가 | 메뉴만 남아 기술 본문 확보 여부를 확인할 수 없다. | 대상 URL https://www.uber.com/blog/engineering?countryiso2=us%252525252525252525252525252525252525252525252525252525252525252525255Cu0022%3F의 문장 0~28은 일반 메뉴다. 기술 본문이나 대체 본문을 정상 사용했다는 기록이 없다. |
| 16 | doc-1680a8b3f8a942a6bd6a54c2d9cb9621 | 판단 불가 | 영상 내용·자막이 없어 본문 수집 성공을 확인할 수 없다. | 대상 URL https://www.youtube.com/watch?v=8wDRlS3vJvc의 문장 0~1은 플랫폼 법적 고지뿐이다. 설계 영상의 자막이나 내용은 없으며 원인도 기록되지 않았다. 이를 정상 기술 본문으로 활용한 흔적은 없어 추출 불충분으로 판단을 유보한다. |
| 17 | fetch:https://www.uber.com/blog/search/pinot | 판단 불가 | 접근 오류로 본문 수집에 실패한 경우 품질 실패와 구분한다. | fetch_failures에서 https://www.uber.com/blog/search/pinot 요청이 지역 경로로 이동한 뒤 HTTP 404로 실패했다. 문서 ID·본문·문장 번호가 없으며 수집 성공으로 처리된 기록도 없다. 실행 오류로 판정에서 제외한다. |
| 18 | fetch:https://eng.uber.com/blog/apache-hudi-at-uber | 판단 불가 | 접근 오류로 본문을 확보하지 못하면 실행 오류로 구분한다. | fetch_failures에 https://eng.uber.com/blog/apache-hudi-at-uber의 HTTP 404가 기록됐다. 문서 ID·실제 본문·문장 번호가 없으므로 수집 내용의 유효성을 판정할 수 없다. |
| 19 | fetch:http://eng.uber.com/blog/apache-hudi-at-uber | 판단 불가 | 접근 오류로 본문을 확보하지 못하면 실행 오류로 구분한다. | fetch_failures에서 http://eng.uber.com/blog/apache-hudi-at-uber 요청의 최종 URL이 https://eng.uber.com/blog/apache-hudi-at-uber이며 HTTP 404로 실패했다. 문서 ID·본문·문장 번호가 없어 수집 유효성은 판단할 수 없다. |
| 20 | fetch:https://www.uber.com/blog/search/data+analytics/page/5 | 판단 불가 | 접근 오류는 정상 본문 오인과 구분해 기록한다. | fetch_failures에 https://www.uber.com/blog/search/data+analytics/page/5 요청이 지역 경로에서 HTTP 404로 실패했다고 기록됐다. 문서 ID·본문·문장 번호가 없으며 실행 오류로 분리한다. |
| 21 | fetch:https://www.uber.com/blog/search/data+analytics | 판단 불가 | 접근 오류로 본문을 확보하지 못하면 실행 오류로 구분한다. | fetch_failures에 https://www.uber.com/blog/search/data+analytics의 지역 경로 이동 후 HTTP 404가 기록됐다. 문서 ID·본문·문장 번호가 없어 후속 근거로 쓸 수 있는 수집 결과가 없다. |
| 22 | fetch:https://www.uber.com/blog/search/data+analytics/page/2 | 판단 불가 | 접근 오류는 수집 품질 실패와 구분한다. | fetch_failures에 https://www.uber.com/blog/search/data+analytics/page/2의 지역 경로 이동 후 HTTP 404가 기록됐다. 문서 ID·본문·문장 번호가 없으며, 다른 내용을 정상 본문으로 처리한 사례는 아니다. |
| 23 | fetch:https://www.uber.com/blog/research | 판단 불가 | 접근 오류로 본문 수집에 실패한 경우 실행 오류로 구분한다. | fetch_failures에 https://www.uber.com/blog/research 요청이 지역 경로에서 HTTP 404로 실패했다고 기록됐다. 문서 ID·본문·문장 번호가 없으므로 정상 본문 수집의 유효성을 판정할 수 없다. |
| 24 | fetch:https://www.uber.com/blog/preds-experience-terms-conditions | 판단 불가 | 접근 오류는 출처 선정 부적절성과 별도로 기록한다. | fetch_failures에 https://www.uber.com/blog/preds-experience-terms-conditions 요청이 지역 경로에서 HTTP 404로 실패했다고 기록됐다. 문서 ID·본문·문장 번호가 없다. 약관 선정은 부적절하지만 수집 오류 자체를 품질 실패로 중복 판정하지 않는다. |
| 25 | fetch:https://www.instagram.com/reel/DWv9hpGKtVi | 판단 불가 | 빈 본문으로 수집에 실패한 경우 실행 오류로 구분한다. | fetch_failures에 https://www.instagram.com/reel/DWv9hpGKtVi의 본문이 비어 수집에 실패했다고 기록됐다. 차단 등 원인은 특정되지 않았고 문서 ID·문장 번호도 없다. 빈 결과를 정상 본문으로 사용한 기록은 없다. |
