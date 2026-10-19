# 수정 후 Middle 2회 평가 상세

새로 생성한 Research 결과를 평가한 실행이다.

[주요 실험 기록](../research-tuning.md) · [원본 JSON](../../../../.archgen/m7-followup/current-criteria-20261019/research-tuning/after/middle/2-evaluation/research.json) · [당시 평가 기준](../../../../.archgen/m7-followup/current-criteria-20261019/research-tuning/after/middle/2-evaluation/research-criteria.md) · [Trace](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/e9cf8be100204e169d71c28dcea0d882)

전체 137건: Pass 98 · Fail 35 · 판단 불가 4. 아래 표에는 모든 Fail과 판단 불가를 생략 없이 기록했다. Pass도 기준별 개수를 표시하며 개별 근거는 원본 JSON에 보존한다.

## 기준별 전체 집계

| 평가 기준 | Pass | Fail | 판단 불가 |
| --- | --- | --- | --- |
| 1-1 평가 초점 반영 | 1 | 0 | 0 |
| 1-2 후보 도출의 타당성 | 4 | 0 | 0 |
| 2-1 후보 검증에 적합한 쿼리 | 4 | 0 | 0 |
| 3-1 검색 결과의 관련성 | 7 | 1 | 0 |
| 4-1 출처 선정의 타당성 | 27 | 32 | 0 |
| 5-1 본문 수집의 유효성 | 53 | 2 | 4 |
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
| 1 | call_fZOJbjLpDMVBIa4wb4ewnSpQ | Fail | 검색 문제에 맞는 문서 후보 없이 무관한 결과를 후속 수집 대상으로 취급하면 실패다. | query-2는 주변 검색의 GEOSEARCH 복잡도와 성능을 찾았으나 결과는 SCAN·XADD·INCR 등으로, 공간 검색 문서가 없다. doc-ee7e6bb32f9841d79f9e072aa643fb43, https://redis.io/docs/latest/commands/scan 등 모두 수집 대상으로 삼았다. 이후 별도 재검색으로 보완했지만 이 호출의 관련성은 낮다. |

## 4-1 출처 선정의 타당성

### 당시 문서에 명시된 판정 기준

- Pass: 검색 결과 중 설계 범위와 후보 검증에 관련되고 게시 주체를 식별할 수 있는 문서를 선택한다. 동일 내용의 중복 URL이나 근거가 부족한 목록·홍보 페이지를 불필요하게 우선하지 않는다.
- Fail: 관련성이나 출처를 확인하지 않은 채 무관한·중복된·본문 근거가 없는 문서를 선택하고, 검색 결과에 있던 더 적절한 출처를 뚜렷한 이유 없이 제외한다.

공식 출처가 아니라는 이유만으로 Fail하지 않는다. 이 평가는 저장된 검색 결과에서 실제 선택 가능한 문서를 기준으로 한다.

### 모든 Fail과 판단 불가 원문

| 번호 | 평가 대상 | 판정 | 실제 적용한 기준 원문 | 판단 근거 원문 |
| --- | --- | --- | --- | --- |
| 1 | doc-fad27d79ec424af79a034ba4475f37a5 | Fail | 관련성 없는 목록 페이지를 불필요하게 선택하면 실패다. | doc-fad27d79ec424af79a034ba4475f37a5, https://techbytes.app/posts , 문장 0–20은 일반 기술 뉴스 목록이다. 같은 검색의 매칭 관련 기사와 달리 네 평가 초점을 검증할 근거를 식별하지 못한 채 선택했다. |
| 2 | doc-0df4d985c8914fe8b071c7942ca3731a | Fail | 후보 검증과 연결되지 않는 문서를 선택하면 실패다. | doc-0df4d985c8914fe8b071c7942ca3731a, https://finance.yahoo.com/news/uber-expands-women-driver-matching-190849377.html , 문장 1–13은 여성 운전자 선호 기능과 소송 기사다. 대기시간 언급은 있으나 검색 지연이나 배정 동시성의 기술 근거와 연결되지 않는다. |
| 3 | doc-ee7e6bb32f9841d79f9e072aa643fb43 | Fail | 검색 문제와 관련성을 확인하지 않은 문서 선택은 실패다. | doc-ee7e6bb32f9841d79f9e072aa643fb43, https://redis.io/docs/latest/commands/scan , 문장 8–14는 키·컬렉션 순회 설명이다. 주변 운전자 공간 검색 검증에 이를 사용할 이유가 없고, 후속 검색에는 직접적인 GEOSEARCH 문서가 있었다. |
| 4 | doc-62bf149003f24636948165ee676fd77f | Fail | 구체적인 후보 검증과 연결되지 않는 문서 선택은 실패다. | doc-62bf149003f24636948165ee676fd77f, https://redis.io/docs/latest/commands/incr , 문장 3–8은 정수 증가 연산이다. 운전자 가용 상태와 배정 확정의 경쟁이나 주변 검색 지연을 검증하는 용도가 기록에 없다. |
| 5 | doc-618630542680470584fc6684aebb9fd4 | Fail | 같은 본문의 중복 URL을 불필요하게 추가 선택하면 실패다. | doc-618630542680470584fc6684aebb9fd4, https://www.postgresql.org/docs/current/explicit-locking.html#EXPLICIT-LOCKING , 문장 0–123은 이미 선택한 doc-98b6b70467c84240b78cdff84ae37f00과 동일하다. 앵커별 추가 수집의 필요성이 없다. |
| 6 | doc-0c602eb1375847bca355dc3ea21f2a5a | Fail | 같은 본문의 중복 URL을 불필요하게 추가 선택하면 실패다. | doc-0c602eb1375847bca355dc3ea21f2a5a, https://www.postgresql.org/docs/current/explicit-locking.html#LOCKING-DEADLOCKS , 문장 0–123은 기존 잠금 문서와 동일하다. 교착 설명도 기존 본문 문장 104–106에 있어 추가 URL의 이득이 없다. |
| 7 | doc-c780da977e374cf6b2966402828295f6 | Fail | 설계 범위와 후보 검증에 연결되지 않는 자료 선택은 실패다. | doc-c780da977e374cf6b2966402828295f6, https://www.uber.com/blog/jupiter-batch-ingestion-platform , 문장 9–26·63–64는 외부 광고 신호와 마케팅 배치 수집이다. 실시간 위치 인덱스나 호출 보존에 적용할 연결 근거 없이 선택했다. |
| 8 | doc-4a6c5288248d4e778b1c15b076bfaeb2 | Fail | 실질적으로 중복된 문서를 비교 목적 없이 반복 선택하면 실패다. | doc-4a6c5288248d4e778b1c15b076bfaeb2, https://kafka.apache.org/21/javadoc/org/apache/kafka/clients/producer/KafkaProducer.html , 문장 6–46의 핵심 내용은 먼저 선택한 1.0 문서와 중복된다. 버전 차이 검증 계획 없이 여러 버전을 함께 수집했다. |
| 9 | doc-46fa7e432c904abdb580bb15b397bf3d | Fail | 실질적으로 중복된 문서를 비교 목적 없이 반복 선택하면 실패다. | doc-46fa7e432c904abdb580bb15b397bf3d, https://kafka.apache.org/20/javadoc/org/apache/kafka/clients/producer/KafkaProducer.html , 문장 9–49는 다른 생산자 버전의 배치·승인·멱등성 설명과 중복된다. 이 버전을 추가 조사해야 할 이유가 없다. |
| 10 | doc-a3d955feb40941bdb03ad469d50a2198 | Fail | 설계 범위와 무관한 문서를 선택하면 실패다. | doc-a3d955feb40941bdb03ad469d50a2198, https://www.businessinsider.com/guides/tech/how-to-contact-uber , 문장 3–41은 고객지원 연락 방법이다. 차량 매칭 시스템의 네 평가 초점을 검증할 기술 자료가 아니다. |
| 11 | doc-64df6ec08c464dd681cc423b57376d7c | Fail | 무관한 자료와 동일 본문 중복을 불필요하게 선택하면 실패다. | doc-64df6ec08c464dd681cc423b57376d7c, https://www.businessinsider.com/reference/how-to-contact-uber , 문장 0–41은 고객지원 기사이며 doc-a3d955feb40941bdb03ad469d50a2198과 동일하다. 관련성과 중복 제거 모두 충족하지 못한다. |
| 12 | doc-50ddbd20301b4b9d8d1b8bf0b69fc654 | Fail | 무관한 자료와 동일 본문 중복을 불필요하게 선택하면 실패다. | doc-50ddbd20301b4b9d8d1b8bf0b69fc654, https://www.businessinsider.com/guides/tech/how-to-contact-uber?op=1 , 문장 0–41은 이미 수집한 고객지원 기사와 동일하다. 매개변수만 다른 세 번째 URL을 선택할 이유가 없다. |
| 13 | doc-132b1c28f9454b47a3ca33cf647e59fd | Fail | 같은 본문의 중복 URL을 불필요하게 추가 선택하면 실패다. | doc-132b1c28f9454b47a3ca33cf647e59fd, https://www.postgresql.org/docs/current/explicit-locking.html#LOCKING-TABLES , 문장 0–123은 기존 잠금 문서와 동일하다. 표 잠금 절도 이미 확보돼 있으며 앵커별 반복 수집 이유가 없다. |
| 14 | doc-2990b0a0756049da9d9387b0e107d7aa | Fail | 같은 본문의 중복 URL을 불필요하게 추가 선택하면 실패다. | doc-2990b0a0756049da9d9387b0e107d7aa, https://www.postgresql.org/docs/current/explicit-locking.html#LOCKING-PAGES , 문장 0–123은 기존 문서와 동일하다. 문장 103도 페이지 잠금은 일반적으로 개발자가 신경 쓸 필요가 없다고 설명한다. |
| 15 | doc-d31d99ce169f4070bce50b5cb90436b0 | Fail | 같은 본문의 중복 URL을 불필요하게 추가 선택하면 실패다. | doc-d31d99ce169f4070bce50b5cb90436b0, http://www.postgresql.org/docs/current/interactive/explicit-locking.html , 문장 0–123은 기존 잠금 문서와 동일하다. 주소 형식만 다른 문서를 추가 수집할 근거가 없다. |
| 16 | doc-ca6ef8a3fcf2470d814db880cd964e7a | Fail | 개별 기술 근거가 없는 목록 페이지를 불필요하게 선택하면 실패다. | doc-ca6ef8a3fcf2470d814db880cd964e7a, https://www.uber.com/blog/engineering/page/2 , 문장 0–27은 분류·날짜 목록이다. 같은 검색에 개별 수집·역압 기사가 있는데도 후보 검증용 본문이 없는 목록까지 선택했다. |
| 17 | doc-088bbcda54c64135b49064e8d06ab611 | Fail | 개별 기술 근거가 없는 목록 페이지를 불필요하게 선택하면 실패다. | doc-088bbcda54c64135b49064e8d06ab611, https://www.uber.com/blog/engineering/page/3 , 문장 0–27은 분류·날짜 목록이다. 위치 갱신이나 호출 처리의 구체적 근거를 식별하지 못한 목록을 추가 수집했다. |
| 18 | doc-5594a71cc1b5400aa4b51fa65e28cc55 | Fail | 실질적으로 중복된 문서를 비교 목적 없이 반복 선택하면 실패다. | doc-5594a71cc1b5400aa4b51fa65e28cc55, https://kafka.apache.org/11/javadoc/org/apache/kafka/clients/producer/KafkaProducer.html , 문장 9–49는 기존 생산자 문서들과 중복된다. 버전 비교 목적이 없어 추가 선정의 타당성이 낮다. |
| 19 | doc-de7cc1a9ff7a4368a3c6491c5febf525 | Fail | 실질적으로 중복된 문서를 비교 목적 없이 반복 선택하면 실패다. | doc-de7cc1a9ff7a4368a3c6491c5febf525, https://kafka.apache.org/31/javadoc/org/apache/kafka/clients/producer/KafkaProducer.html , 문장 7–47의 핵심 승인·버퍼·멱등성 설명은 이미 확보했다. 다섯 생산자 버전을 함께 선택할 비교 근거가 없다. |
| 20 | doc-5d7ede54da884df8a31b4e1c07965dcf | Fail | 설계 범위와 무관한 문서를 선택하면 실패다. | doc-5d7ede54da884df8a31b4e1c07965dcf, https://www.cnbc.com/2014/07/10/uber-driver-kidnaps-rider-leads-high-speed-chase-in-dc.html , 문장 0–6은 운행 중 범죄 사건이다. 매칭 이전 시스템의 네 평가 초점과 무관하다. |
| 21 | doc-09494c62f0cd44418c803204f55ebee7 | Fail | 설계 범위와 무관한 목록을 선택하면 실패다. | doc-09494c62f0cd44418c803204f55ebee7, https://jobseekers.cafe , 문장 0–25는 농업 장비 운전원 채용과 구인 사이트 소개다. 차량 매칭 시스템 검증에 관련되지 않는다. |
| 22 | doc-70ad056e743442789236c34e0dffbb32 | Fail | 설계 범위와 무관한 목록을 선택하면 실패다. | doc-70ad056e743442789236c34e0dffbb32, https://bayoulifemag.com/previous-issues , 문장 0은 잡지 과월호 목록이다. 검색 결과의 제목과 주소만으로도 매칭 설계와 관련성이 확인되지 않는다. |
| 23 | doc-961847c6dabd40a688c1b6969fc98fea | Fail | 같은 본문의 중복 URL을 불필요하게 추가 선택하면 실패다. | doc-961847c6dabd40a688c1b6969fc98fea, https://www.postgresql.org/docs/current/explicit-locking.html#LOCKING-ROWS , 문장 75–83을 포함한 본문이 doc-98b6b70467c84240b78cdff84ae37f00과 동일하다. 관련 내용이지만 별도 수집할 필요는 없다. |
| 24 | doc-e66b55f68ded4f3ba6e1a18b65c20d9d | Fail | 같은 본문의 중복 URL을 불필요하게 추가 선택하면 실패다. | doc-e66b55f68ded4f3ba6e1a18b65c20d9d, https://www.postgresql.org/docs/current/explicit-locking.html#ADVISORY-LOCKS , 문장 0–123은 기존 잠금 문서와 동일하다. 앵커가 달라도 독립 근거가 추가되지 않았다. |
| 25 | doc-9fe195af478340c9b2e57f3619a6590c | Fail | 같은 본문의 중복 URL을 불필요하게 추가 선택하면 실패다. | doc-9fe195af478340c9b2e57f3619a6590c, https://www.postgresql.org/docs/current/explicit-locking.html#ROW-LOCK-COMPATIBILITY , 문장 0–123은 기존 문서와 동일하다. 잠금 충돌 표도 이미 확보해 중복 선택이다. |
| 26 | doc-5acb4356956348fa9c56fcdc5194411c | Fail | 개별 기술 근거가 없는 목록 페이지를 불필요하게 선택하면 실패다. | doc-5acb4356956348fa9c56fcdc5194411c, https://www.uber.com/blog/engineering/backend , 문장 0–21은 분류·날짜 목록이다. 같은 검색의 구체적인 기술 기사 대신 별도 근거가 없는 분류 페이지까지 선택했다. |
| 27 | doc-21a48383b7a04b6daabeab6abe24cf9f | Fail | 설계 범위와 후보 검증에 연결되지 않는 문서를 선택하면 실패다. | doc-21a48383b7a04b6daabeab6abe24cf9f, https://www.uber.com/blog/marmaray-hadoop-ingestion-open-source , 문장 23–28·35–39는 분석용 데이터 레이크 수집과 파생 데이터 배포다. 실시간 위치 반영이나 호출 처리에 적용할 연결 근거 없이 선택했다. |
| 28 | doc-cdc1427fafdd4f5ca6f71b0635f16719 | Fail | 설계 범위와 후보 검증에 연결되지 않는 문서를 선택하면 실패다. | doc-cdc1427fafdd4f5ca6f71b0635f16719, https://www.uber.com/blog/restaurant-manager , 문장 13–25·35–43은 음식점 매출·평점 분석 대시보드다. 문장 74–80의 성능도 분석 시스템 조건으로, 매칭 조사에 선정할 연결 설명이 없다. |
| 29 | doc-2727d98397734781a7c49c0f5f5967c8 | Fail | 설계 범위와 무관한 목록을 선택하면 실패다. | doc-2727d98397734781a7c49c0f5f5967c8, https://xboxera.com/category/playstation , 문장 0–5는 게임 소식 목록이다. 검색 제목과 주소에도 차량 매칭 검증의 관련성이 없다. |
| 30 | doc-3ea3cdee71ac453086b019cb25898834 | Fail | 관련성 없는 홍보·목록 페이지를 선택하면 실패다. | doc-3ea3cdee71ac453086b019cb25898834, https://www.uber.com/blog/what-pride-means-to-us 는 검색 단계에서도 일반 소식 제목이었다. 수집된 문장 0–28도 제품 분류 안내뿐으로, 후보 검증용 기술 출처로 고를 근거가 없다. |
| 31 | fetch:https://eng.uber.com/blog/high-throughput-processing | Fail | 범위 밖 주제의 문서를 후보 검증에 연결할 근거 없이 선택하면 실패다. | https://eng.uber.com/blog/high-throughput-processing 는 검색 call_ki6iGiBao3817kD3Yv4ijkjT의 6위로 결제 계정 처리 기사다. brief에서 결제를 제외했고, 공통 처리 기법을 전용하려는 선정 근거도 없다. 문서 ID·본문 문장은 없으며 404 오류와는 별도 판정이다. |
| 32 | fetch:https://www.instagram.com/reel/DaIYdx7zKeH | Fail | 관련성이나 게시 주체를 확인하지 못한 자료를 선택하면 실패다. | https://www.instagram.com/reel/DaIYdx7zKeH 는 검색 call_rCfuSNKlOO5ypBgEb7Ohk3Mg의 3위에서 플랫폼명만 표시됐다. 주제·게시자가 확인되지 않는데 수집 대상으로 선택했고 본문도 비었다. 문서 ID·문장 번호는 없다. |

## 5-1 본문 수집의 유효성

### 당시 문서에 명시된 판정 기준

- Pass: 선택한 문서의 실제 본문을 정상적으로 수집하여 후속 근거 확인에 사용할 수 있다.
- Fail: 본문 대신 검색 요약이나 다른 문서 내용을 수집하고 정상적인 본문으로 처리한다.

판단 불가/실행 오류: 접근 차단·타임아웃 등으로 본문 수집에 실패한 경우는 별도로 기록한다.

### 모든 Fail과 판단 불가 원문

| 번호 | 평가 대상 | 판정 | 실제 적용한 기준 원문 | 판단 근거 원문 |
| --- | --- | --- | --- | --- |
| 1 | doc-3ea3cdee71ac453086b019cb25898834 | Fail | 요청 기사 대신 다른 페이지의 안내 내용을 정상 본문으로 처리하면 실패다. | doc-3ea3cdee71ac453086b019cb25898834, https://www.uber.com/blog/what-pride-means-to-us , 문장 0–28은 요청 경로의 기사 대신 일반 제품·뉴스 분류 안내다. 오류 표기 없이 정상 수집 문서로 저장돼 요청 기사 본문 확보로 볼 수 없다. |
| 2 | doc-5c9dfba35bab4d01b35eef8b102faf1d | Fail | 실제 내용 대신 안내문만 수집하고 정상 본문으로 처리하면 실패다. | doc-5c9dfba35bab4d01b35eef8b102faf1d, https://www.youtube.com/watch?v=SWicoZakcIM , 문장 0–1은 저작권·판매 책임 안내뿐이다. 강의 설명이나 자막 없이 정상 문서로 저장돼 배차 설계의 실제 내용을 확인할 수 없다. |
| 3 | fetch:https://eng.uber.com/blog/high-throughput-processing | 판단 불가 | 접근 실패 등 실행 오류는 품질 실패와 구분하고 판정에서 제외한다. | fetch_failures의 https://eng.uber.com/blog/high-throughput-processing 요청은 1회 시도 후 HTTP 404로 실패했다. 실제 본문·문서 ID·문장 번호가 없어 수집 유효성을 판정할 수 없다. |
| 4 | fetch:https://medium.com/groupon-eng/scaling-millions-of-geospatial-queries-per-minute-using-redis-7c05bcf6b4db | 판단 불가 | 접근 차단 등 실행 오류는 품질 실패와 구분하고 판정에서 제외한다. | fetch_failures의 https://medium.com/groupon-eng/scaling-millions-of-geospatial-queries-per-minute-using-redis-7c05bcf6b4db 요청은 1회 시도 후 HTTP 403으로 차단됐다. 실제 본문·문서 ID·문장 번호가 없어 판정 불가다. |
| 5 | fetch:https://medium.com/codetodeploy/uber-architecture-part-5-the-dispatch-engine-and-map-rendering-64ac669fa698 | 판단 불가 | 접근 차단 등 실행 오류는 품질 실패와 구분하고 판정에서 제외한다. | fetch_failures의 https://medium.com/codetodeploy/uber-architecture-part-5-the-dispatch-engine-and-map-rendering-64ac669fa698 요청은 1회 시도 후 HTTP 403으로 차단됐다. 실제 본문·문서 ID·문장 번호가 없어 판정 불가다. |
| 6 | fetch:https://www.instagram.com/reel/DaIYdx7zKeH | 판단 불가 | 본문 수집 실패를 명시한 실행 오류는 정상 본문 오인과 구분한다. | fetch_failures의 https://www.instagram.com/reel/DaIYdx7zKeH 는 본문이 비어 있다고 실패 처리됐다. 빈 내용을 정상 본문으로 사용한 기록은 없고 문서 ID·문장 번호도 없어 수집 품질 판정에서 제외한다. |
