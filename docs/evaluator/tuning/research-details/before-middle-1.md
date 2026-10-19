# 수정 전 Middle 1회 평가 상세

새로 생성한 Research 결과를 평가한 실행이다.

[주요 실험 기록](../research-tuning.md) · [원본 JSON](../../../../.archgen/m7-followup/current-criteria-20261019/research-tuning/before/middle/1-evaluation/research.json) · [당시 평가 기준](../../../../.archgen/m7-followup/current-criteria-20261019/research-tuning/before/middle/1-evaluation/research-criteria.md) · [Trace](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/cfd8c18159d24e32bedd7a6d729344fe)

전체 154건: Pass 67 · Fail 75 · 판단 불가 12. 아래 표에는 모든 Fail과 판단 불가를 생략 없이 기록했다. Pass도 기준별 개수를 표시하며 개별 근거는 원본 JSON에 보존한다.

## 기준별 전체 집계

| 평가 기준 | Pass | Fail | 판단 불가 |
| --- | --- | --- | --- |
| 1-1 평가 초점 반영 | 1 | 0 | 0 |
| 1-2 후보 도출의 타당성 | 4 | 0 | 0 |
| 2-1 후보 검증에 적합한 쿼리 | 4 | 0 | 0 |
| 3-1 검색 결과의 관련성 | 7 | 2 | 0 |
| 4-1 출처 선정의 타당성 | 14 | 52 | 1 |
| 5-1 본문 수집의 유효성 | 35 | 21 | 11 |
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
| 1 | call_C8sKRStIBJ27Tgj8ykKu5POl | Fail | 후보 검증 문서 없이 일반 목록을 근거 탐색 결과로 사용한다. | query-3의 1~10위가 모두 기술 블로그 목록과 그 변형이다. 대표 doc-3dfe7af843e94346be801c63f2514a63, https://www.uber.com/blog/engineering 문장0~28은 공통 메뉴뿐이다. 이를 모두 수집했지만 배정 경쟁 검증용 문서 후보는 없었다. |
| 2 | call_RL9XcrRHB2XAd3CY1U6YpRkY | Fail | 다른 주제의 결과만으로 후보 검증 자료를 확보하지 못했다. | query-4의 추가 검색은 화물 조달 홍보와 운행 허가 소식 두 건뿐이다. doc-5ff9f3b0b30647b59ef42c78830a7bea, https://www.uber.com/blog/rural-king-uber-freight-customer-story 문장7~16은 화물 용량 조달이며 위치 갱신 처리량과 무관하다. |

## 4-1 출처 선정의 타당성

### 당시 문서에 명시된 판정 기준

- Pass: 검색 결과 중 설계 범위와 후보 검증에 관련되고 게시 주체를 식별할 수 있는 문서를 선택한다. 동일 내용의 중복 URL이나 근거가 부족한 목록·홍보 페이지를 불필요하게 우선하지 않는다.
- Fail: 관련성이나 출처를 확인하지 않은 채 무관한·중복된·본문 근거가 없는 문서를 선택하고, 검색 결과에 있던 더 적절한 출처를 뚜렷한 이유 없이 제외한다.

공식 출처가 아니라는 이유만으로 Fail하지 않는다. 이 평가는 저장된 검색 결과에서 실제 선택 가능한 문서를 기준으로 한다.

### 모든 Fail과 판단 불가 원문

| 번호 | 평가 대상 | 판정 | 실제 적용한 기준 원문 | 판단 근거 원문 |
| --- | --- | --- | --- | --- |
| 1 | doc-7faf374a943e4db8869cb042f259cf3a | Fail | 관련성이 부족한 문서를 불필요하게 선택했다. | https://www.uber.com/blog/new-rider-app-architecture 문장19~27·43~91은 앱 가용성·모듈 구조 중심이다. 호출 보존이나 검색·배정 경쟁을 검증할 연결 설명 없이 선택했으며, 같은 검색에 호출 제안 수신 자료가 있었다. |
| 2 | doc-fc4d298a105a45d8961e548dee556bc7 | Fail | 관련성이 부족한 문서를 불필요하게 선택했다. | https://www.uber.com/blog/rewrite-uber-carbon-app 문장16~31·52~85는 앱 재작성 결정과 이관 위험이다. 서버 측 검색 지연·중복 배정·위치 처리·호출 보존 검증과의 연결이 저장되어 있지 않다. |
| 3 | doc-2d58ceca76614f1a8a09c8d5d2c4117c | Fail | 구체적 근거가 부족한 소개 페이지를 불필요하게 선택했다. | https://www.uber.com/blog/uber-technology-day 문장9~11·27~40은 행사 발표 소개다. 검색 결과에 공간 검색·재처리의 구체적 기술 문서가 있는데도 기술 조건을 확인하기 어려운 행사 개요까지 수집했다. |
| 4 | doc-3dfe7af843e94346be801c63f2514a63 | Fail | 본문 근거가 없는 일반 목록을 선택했다. | https://www.uber.com/blog/engineering 문장0~28은 공통 탐색 메뉴다. 게시 주체는 식별되지만 배정 정합성 후보를 검증할 개별 기술 문서가 아니다. |
| 5 | doc-055c931eca024bdfad5614bbb7d9de04 | Fail | 근거 없는 목록·중복 URL을 불필요하게 선택했다. | https://www.uber.com/blog/engineering?id=x 문장0~28은 기본 기술 블로그와 같은 메뉴다. doc-3dfe7af843e94346be801c63f2514a63과 실질적으로 중복이며 배정 경쟁 근거가 없다. |
| 6 | doc-cf1c757f1fd24aff89d37e2bacb5dd4a | Fail | 근거 없는 목록·중복 URL을 불필요하게 선택했다. | https://www.uber.com/blog/engineering?uber_client_name=706 문장0~28은 기본 목록과 같은 메뉴다. 매개변수만 다른 URL에서 배정 정합성의 추가 근거를 기대할 설명이 없다. |
| 7 | doc-f6018185b2d54f5c96c352b958aa9cfd | Fail | 개별 기술 문서 대신 근거가 부족한 목록을 선택했다. | https://www.uber.com/blog/engineering/page/3 문장0~27은 분류·날짜 목록이다. 같은 검색의 수집 처리 기술 문서와 달리 위치 이벤트 처리량의 설계 방법을 확인할 수 없다. |
| 8 | doc-79b1aae50ed44a3d931179047b2b4e16 | Fail | 본문 근거가 없는 일반 목록을 선택했다. | https://www.uber.com/blog/dallas/ride 문장0~28은 일반 메뉴다. 같은 검색의 Cherami·재처리 문서와 달리 호출 보존이나 복구 설계 근거가 없다. |
| 9 | doc-b1ea7b75d4d7433d9ea67a12f2bc1853 | Fail | 범위 밖 기능을 후보와 연결하지 않고 선택했다. | https://www.uber.com/blog/uber-beacon-bluetooth-mobile-app 문장4~8·55~65는 배정 후 승객과 차량의 색상 식별이다. 배정 확정까지라는 범위를 벗어나며 중복 배정 방지와도 다른 문제다. |
| 10 | doc-14602bdc4c1a482fbd1fb1a5226882b3 | Fail | 본문 근거가 없는 일반 목록을 선택했다. | https://www.uber.com/blog/engineering/page/34 문장0~28은 공통 메뉴다. 같은 검색에 실제 공간 검색 문서가 있었지만 이 목록에서는 지연 제어 방법을 확인할 수 없다. |
| 11 | doc-eb1580685764495e94094accdf0fd66e | Fail | 근거 없는 목록·중복 URL을 불필요하게 선택했다. | https://www.uber.com/blog/engineering?id=998638 문장0~28은 기본 기술 블로그 메뉴와 같다. 배정 상태 경쟁에 대한 개별 문서나 추가 정보가 없다. |
| 12 | doc-36f633dd6c924ab7b5f0632d6c3a469c | Fail | 동일 내용의 중복 URL을 불필요하게 선택했다. | http://uber.com/blog/engineering 문장0~28은 doc-3dfe7af843e94346be801c63f2514a63과 같은 메뉴다. 주소 형식만 달라 배정 정합성 조사의 새로운 출처가 되지 않는다. |
| 13 | doc-a5d3c4cd09ed4495aa06f3ca9d8e5b05 | Fail | 근거 없는 목록·중복 URL을 불필요하게 선택했다. | https://www.uber.com/blog/engineering?id=26 문장0~28은 동일한 기술 블로그 메뉴다. 매개변수 변형을 추가 수집할 후보 관련 이유가 없다. |
| 14 | doc-d733dc20a45941abb3ebd84326d04b7a | Fail | 개별 기술 문서 대신 근거가 부족한 목록을 선택했다. | https://www.uber.com/blog/engineering/backend 문장0~21은 분류·날짜 목록이다. 위치 갱신의 수집·적체 제어를 검증할 본문 근거가 없고 같은 검색에 구체적 수집 자료가 있었다. |
| 15 | doc-99633f359a554a31841058e772f8a0c3 | Fail | 개별 기술 문서 대신 근거가 부족한 목록을 선택했다. | https://www.uber.com/blog/engineering/page/2 문장0~27은 분류·날짜 목록이다. 위치 이벤트 처리량과 연결되는 개별 기술 설명이 없다. |
| 16 | doc-a503f98c18bc41238a79a469cf4329c9 | Fail | 근거 없는 지역별 목록을 불필요하게 선택했다. | https://www.uber.com/blog/california/engineering 문장0~28은 일반 메뉴의 지역별 변형이다. 위치 갱신 처리량 후보의 추가 근거가 없다. |
| 17 | doc-71f06aba5075499aac7e75cf24ebf679 | Fail | 근거 없는 목록·중복 URL을 불필요하게 선택했다. | https://www.uber.com/blog/engineering?id=50 문장0~28은 기본 기술 블로그와 같은 메뉴다. 운전자 배정 경쟁 검증용 자료가 아니다. |
| 18 | doc-787c7c85108a439f91a0cbab06d7716e | Fail | 근거 없는 목록·중복 URL을 불필요하게 선택했다. | https://www.uber.com/blog/engineering?id=879 문장0~28은 동일 메뉴다. 배정 정합성을 확인할 새로운 기술 내용이 없다. |
| 19 | doc-8c38ec4263394bf996c7078a9d9d80cb | Fail | 근거 없는 목록·중복 URL을 불필요하게 선택했다. | https://www.uber.com/blog/engineering?id=118%2Cwww.uber.com%2Fnz%2Fen%2Fcareers%2Fdesign%2Cuber.com%2C0.33170733 문장0~28은 공통 메뉴다. 복잡한 매개변수에도 개별 기술 문서 식별이나 후보 관련 정보가 없다. |
| 20 | doc-2292533602934f19920c65f4a1b93983 | Fail | 근거 없는 지역별 목록을 불필요하게 선택했다. | https://www.uber.com/blog/connecticut/engineering 문장0~28은 일반 메뉴다. 지역별 목록을 위치 갱신 처리량 검증 자료로 선택할 근거가 없다. |
| 21 | doc-512f908304384401828eb0266982feaf | Fail | 근거 없는 지역별 목록을 불필요하게 선택했다. | https://www.uber.com/blog/washington/engineering 문장0~28은 일반 메뉴다. 위치 이벤트 수집이나 적체 제어에 관한 추가 정보가 없다. |
| 22 | doc-13c77218cbfa4c5199955f8ab9bec30a | Fail | 본문 근거가 없는 일반 목록을 선택했다. | https://www.uber.com/blog/los-angeles/ride 문장0~28은 공통 메뉴다. 같은 검색의 내구성 큐 자료와 달리 호출 보존·재처리 근거가 없다. |
| 23 | doc-c3c4589f810e48d0a490e5104a9cdd98 | Fail | 본문 근거가 없는 일반 목록을 선택했다. | https://www.uber.com/blog/ride 문장0~28은 공통 메뉴다. 차량 서비스 분류명만으로 요청 보존이나 장애 복구를 검증할 수 없다. |
| 24 | doc-fd8b6c6185ef4b3ea55c5cdf0982b46b | Fail | 근거 없는 목록·중복 URL을 불필요하게 선택했다. | https://www.uber.com/blog/engineering?id=98 문장0~28은 기본 기술 블로그와 같은 메뉴다. 배정 정합성에 대한 추가 기술 근거가 없다. |
| 25 | doc-bdb89abd63934085b0a78ae98d9e0c06 | Fail | 본문 근거가 없는 일반 목록을 선택했다. | https://www.uber.com/blog/washington-dc/ride 문장0~28은 공통 메뉴다. 지역별 차량 서비스 목록에서 호출 보존·복구 방법을 확인할 수 없다. |
| 26 | doc-0df27d9f9d6d42e6a99fbb06aad7098d | Fail | 다른 주제의 문서를 후보와 연결하지 않고 선택했다. | https://www.uber.com/blog/keplergl 문장11~20·35~41은 브라우저 공간 데이터 시각화다. 주변 운전자 검색의 서버 지연이나 위치 갱신 처리와 연결한 선정 설명이 없다. |
| 27 | doc-4baa1028569e4c8e98ea9b7b9bf47aa6 | Fail | 다른 주제의 문서를 후보와 연결하지 않고 선택했다. | https://www.uber.com/blog/nebulagl 문장4~14·25~35는 브라우저 지도 도형 편집이다. 좌표 렌더링 성능은 주변 운전자 검색 지연과 다른 문제이며 전용 근거가 없다. |
| 28 | doc-d01f9210bcc741f0a8784c508985d42c | Fail | 설계 범위와 연결이 부족한 자료를 선택했다. | https://uber.com/blog/uber-big-data-platform 문장3·47~74는 분석용 데이터 레이크와 배치 처리다. 온라인 운전자 위치 반영·주변 검색과의 연결 설명 없이 수집했으며 같은 검색군에 공간 색인 자료가 있었다. |
| 29 | doc-7ad049c3c9ec4ad19e7912b5bfddfcf2 | Fail | 범위 밖 사례를 후보와 연결하지 않고 선택했다. | https://www.uber.com/blog/money-scale-strong-data 문장9~16·44~56은 결제 플랫폼과 계정 정합성이다. 재사용 가능한 기법은 있으나 배정 상태 경쟁으로 전용할 설명이 없고 같은 검색에 직접 관련된 Fulfillment 자료가 있었다. |
| 30 | doc-ae82f4b06dff445284dc21e0ae7f80ff | Fail | 동일 내용의 중복 URL을 불필요하게 선택했다. | https://www.uber.com/blog/money-scale-strong-data?ref=highscalability.com 문장0~125는 doc-7ad049c3c9ec4ad19e7912b5bfddfcf2와 같은 결제 자료다. 추적 매개변수 변형으로 새로운 근거를 추가하지 않는다. |
| 31 | doc-dff4930dfb304f1685ae034d0d3e9bc9 | Fail | 범위 밖 기능을 후보와 연결하지 않고 선택했다. | https://www.uber.com/blog/real-time-earnings-tracker 문장16~35·62~69는 운전자 수입 표시의 데이터 정합성이다. 배정 확정의 원자성과 다른 문제이며 직접 관련된 플랫폼 자료 대신 추가 수집할 이유가 없다. |
| 32 | doc-5ff9f3b0b30647b59ef42c78830a7bea | Fail | 무관한 홍보 사례를 선택했다. | https://www.uber.com/blog/rural-king-uber-freight-customer-story 문장7~21·33~35는 화물 운송 용량 조달·가격 홍보다. 운전자 위치 이벤트 처리량을 검증할 기술 내용이 없다. |
| 33 | doc-a6842314a74d492791191f985c56bc5d | Fail | 구체적 근거가 부족한 발표 자료를 불필요하게 선택했다. | https://www.uber.com/blog/cadence-workflow-joins-the-cloud-native-computing-foundation 문장1~14는 재단 합류와 기능 개요다. 같은 검색에 저장·재시도·격리를 구체적으로 설명하는 Cadence 작업 처리 자료가 있어 이 발표의 추가 근거 가치는 낮다. |
| 34 | doc-3708d7c4945d4df2a1e6eb6352ea61c3 | Fail | 동일 내용의 중복 URL을 불필요하게 선택했다. | https://www.uber.com/blog/uber-big-data-platform?ref=highscalability.com 문장0~80은 doc-d01f9210bcc741f0a8784c508985d42c와 같은 분석 플랫폼 내용이다. 매개변수 변형은 온라인 매칭의 새 근거가 아니다. |
| 35 | doc-b995dcc7c4064144877752c307652e81 | Fail | 동일 내용의 중복 URL을 불필요하게 선택했다. | https://www.uber.com/blog/uber-big-data-platform 문장0~80은 이미 수집한 doc-d01f9210bcc741f0a8784c508985d42c·doc-3708d7c4945d4df2a1e6eb6352ea61c3와 같다. 호스트·매개변수 정규화 없이 중복 수집했다. |
| 36 | doc-14af4c4f0bdc409ebdb2b6613c768eb0 | Fail | 동일 내용의 중복 URL을 불필요하게 선택했다. | https://www.uber.com/blog/visualizing-city-cores-with-h3?ref=highscalability.com 문장0~23은 doc-2023f35e893f49059a9bf5422a05ce31과 같다. 공간 분할의 관련성은 있으나 추적 매개변수 변형을 다시 수집할 이유는 없다. |
| 37 | doc-ebe39aeccb3041c187f2c4b2930e0c76 | Fail | 범위 밖 사례를 후보와 연결하지 않고 선택했다. | https://www.uber.com/blog/high-throughput-processing 문장2~4·24~40·85~86은 결제 계정의 배치 갱신이다. 배정 경쟁·위치 갱신에 적용할 연결 설명 없이 선택했으며 같은 검색에 실제 매칭 플랫폼 자료가 있었다. |
| 38 | doc-8892fc1b258b404193ff2ef7977f8f49 | Fail | 설계 범위와 연결이 부족한 자료를 선택했다. | https://www.uber.com/blog/dynamodb-to-docstore-migration 문장15~34·77~94는 금융 원장 무결성·봉인·이관 처리다. 실시간 배정 확정 문제와 연결한 선정 설명이 없고 같은 검색에 직접 관련된 플랫폼 자료가 있었다. |
| 39 | doc-29d2f725dd5e4f98a5855d045c46d788 | Fail | 다른 주제의 문서를 후보와 연결하지 않고 선택했다. | https://www.uber.com/blog/3d-tiles-loadersgl 문장1~8·21~34는 항공 이동 계획과 브라우저 점군 시각화다. 대용량 공간 데이터라는 공통점만으로 운전자 검색 지연의 근거가 되지 않는다. |
| 40 | doc-5116b7aeb07b41ac859dd3bd57b139e5 | Fail | 다른 주제의 문서를 후보와 연결하지 않고 선택했다. | https://www.uber.com/blog/optimizing-m3 문장3~14·39~71은 관측 지표 수집 지연과 Go 실행 성능 분석이다. 주변 운전자 공간 검색으로 연결한 조사 설명이 없다. |
| 41 | doc-371eb854ab7847f5aea789e9d2f71a3b | Fail | 동일 내용의 중복 URL을 불필요하게 선택했다. | https://www.uber.com/blog/building-ubers-fulfillment-platform?ref=highscalability.com 문장0~91은 doc-4fbae610ec7b41829bf60831f4aeb373과 같다. 본문은 관련되지만 추적 매개변수 변형을 추가 선택할 이유가 없다. |
| 42 | doc-01f841e5ae6b4a06b2985f2010b09f07 | Fail | 설계 범위와 연결이 부족한 자료를 선택했다. | https://www.uber.com/blog/building-ubers-data-lake-batch-data-replication-using-hivesync 문장2~15·46~50은 분석 데이터 레이크의 배치 복제와 수시간 단위 목표다. 온라인 호출·배정 상태로 연결한 설명 없이 정합성 자료로 수집했다. |
| 43 | fetch:https://www.uber.com/blog/research/dynamic-pricing-and-matching-in-ride-hailing-platforms | 판단 불가 | 선정 타당성을 확인할 관련 기록이 부족하면 판단을 유보한다. | https://www.uber.com/blog/research/dynamic-pricing-and-matching-in-ride-hailing-platforms 는 매칭을 지칭하지만 검색 제목은 일반 블로그명이고 요약·선정 설명이 없다. 범위 밖 가격 연구와 매칭 기술의 비중을 판단할 본문도 없으며 수집은 HTTP 404였다. 문서 ID·문장 번호는 없다. |
| 44 | fetch:https://eng.uber.com/blog/apache-hudi-at-uber | Fail | 설계 범위와 연결이 부족한 자료를 선택했다. | https://eng.uber.com/blog/apache-hudi-at-uber 는 query-4의 2위로, 제목상 데이터 레이크 운영 자료다. 온라인 위치 갱신으로 연결한 설명 없이 선택했다. HTTP 404는 별도 실행 오류이며 문서 ID·본문 문장 번호는 없다. |
| 45 | fetch:http://eng.uber.com/blog/apache-hudi-at-uber | Fail | 동일 내용의 중복 URL을 불필요하게 선택했다. | http://eng.uber.com/blog/apache-hudi-at-uber 는 query-4의 3위로 바로 앞 HTTPS 결과와 경로·제목이 같다. 실패 기록에서도 같은 HTTPS 주소로 귀결되어 중복 시도에 해당한다. 문서 ID·본문 문장 번호는 없다. |
| 46 | fetch:https://www.uber.com/blog/search/pinot | Fail | 개별 기술 문서 대신 근거가 부족한 검색 목록을 선택했다. | https://www.uber.com/blog/search/pinot 는 query-2의 검색 목록이다. 같은 결과의 doc-92c97b5b46c24ce8ac6f807347265a02, https://www.uber.com/blog/orders-near-you 문장40~54처럼 직접 확인할 공간 색인 자료가 있었다. 대상 본문은 HTTP 404로 문장 번호가 없다. |
| 47 | fetch:https://www.uber.com/blog/search/data+analytics/page/5 | Fail | 근거가 부족한 일반 검색 목록을 불필요하게 선택했다. | https://www.uber.com/blog/search/data+analytics/page/5 는 query-2의 일반 분석 검색 목록이다. 개별 문서의 검색 지연 관련성을 확인한 설명 없이 선택했다. HTTP 404와 별개인 선별 문제이며 문서 ID·본문 문장 번호는 없다. |
| 48 | fetch:https://www.uber.com/blog/search/data+analytics | Fail | 근거가 부족한 일반 검색 목록을 불필요하게 선택했다. | https://www.uber.com/blog/search/data+analytics 는 query-2의 일반 분석 검색 목록이다. 같은 검색에 구체적인 공간 검색 자료가 있어 이 목록을 본문 근거 대상으로 삼을 이유가 부족하다. HTTP 404였으며 문서 ID·문장 번호는 없다. |
| 49 | fetch:https://www.uber.com/blog/research/driver-surge-pricing | Fail | 명시적으로 제외된 주제의 자료를 후보와 연결하지 않았다. | https://www.uber.com/blog/research/driver-surge-pricing 는 query-2의 가격 연구 결과다. 요금 계산이 제외된 범위에서 주변 검색 지연을 검증할 연결 설명이 없다. HTTP 404는 별도이며 문서 ID·본문 문장 번호는 없다. |
| 50 | fetch:https://eng.uber.com/blog/ride/page/2 | Fail | 본문 근거가 부족한 일반 목록을 선택했다. | https://eng.uber.com/blog/ride/page/2 는 query-5의 차량 서비스 목록이다. 같은 검색에 내구성 큐·재처리 문서가 있는데도 호출 보존 관련 기술성을 확인하지 않고 선택했다. HTTP 404였으며 문서 ID·문장 번호는 없다. |
| 51 | fetch:https://www.uber.com/blog/search/data+analytics/page/2 | Fail | 근거가 부족한 일반 검색 목록을 불필요하게 선택했다. | https://www.uber.com/blog/search/data+analytics/page/2 는 query-2의 분석 검색 목록이다. 다른 목록 페이지와 함께 수집했지만 주변 검색 지연의 개별 근거 문서를 식별한 설명이 없다. HTTP 404였으며 문서 ID·문장 번호는 없다. |
| 52 | fetch:https://eng.uber.com/blog/los-angeles/ride | Fail | 근거 없는 지역별 목록·중복 주소를 불필요하게 선택했다. | https://eng.uber.com/blog/los-angeles/ride 는 query-5의 지역별 차량 서비스 목록이다. 같은 지역의 doc-13c77218cbfa4c5199955f8ab9bec30a도 수집했으나 문장0~28은 메뉴뿐이다. 대상은 HTTP 404로 본문 문장 번호가 없다. |
| 53 | fetch:https://www.uber.com/blog/puc-approves-two-year-license | Fail | 후보 검증과 무관한 자료를 선택했다. | https://www.uber.com/blog/puc-approves-two-year-license 는 query-4 추가 검색의 운행 허가 소식이다. 위치 갱신 처리량이나 적체 제어와 연결할 기술적 선정 근거가 없다. HTTP 404였으며 문서 ID·본문 문장 번호는 없다. |

## 5-1 본문 수집의 유효성

### 당시 문서에 명시된 판정 기준

- Pass: 선택한 문서의 실제 본문을 정상적으로 수집하여 후속 근거 확인에 사용할 수 있다.
- Fail: 본문 대신 검색 요약이나 다른 문서 내용을 수집하고 정상적인 본문으로 처리한다.

판단 불가/실행 오류: 접근 차단·타임아웃 등으로 본문 수집에 실패한 경우는 별도로 기록한다.

### 모든 Fail과 판단 불가 원문

| 번호 | 평가 대상 | 판정 | 실제 적용한 기준 원문 | 판단 근거 원문 |
| --- | --- | --- | --- | --- |
| 1 | doc-3dfe7af843e94346be801c63f2514a63 | Fail | 실제 문서 본문 없이 정상 수집 결과로 처리했다. | https://www.uber.com/blog/engineering 문장0~28은 광고·서비스 분류 등 공통 메뉴뿐이다. 본문 확보 표시가 있으나 후속 기술 근거 확인에 쓸 문서 내용은 없다. |
| 2 | doc-055c931eca024bdfad5614bbb7d9de04 | Fail | 실제 문서 본문 없이 정상 수집 결과로 처리했다. | https://www.uber.com/blog/engineering?id=x 문장0~28은 공통 메뉴다. 본문 확보 표시와 달리 개별 문서나 기술 설명이 수집되지 않았다. |
| 3 | doc-cf1c757f1fd24aff89d37e2bacb5dd4a | Fail | 실제 문서 본문 없이 정상 수집 결과로 처리했다. | https://www.uber.com/blog/engineering?uber_client_name=706 문장0~28은 공통 메뉴다. 정상 수집 목록에 저장되었지만 확인 가능한 기술 본문은 없다. |
| 4 | doc-f6018185b2d54f5c96c352b958aa9cfd | Fail | 실제 문서 본문 없이 정상 수집 결과로 처리했다. | https://www.uber.com/blog/engineering/page/3 문장0~27은 분류·날짜만 남은 목록이다. 기사 제목·본문이나 설계 근거를 확인할 수 없는데 본문 확보로 저장되어 있다. |
| 5 | doc-79b1aae50ed44a3d931179047b2b4e16 | Fail | 실제 문서 본문 없이 정상 수집 결과로 처리했다. | https://www.uber.com/blog/dallas/ride 문장0~28은 공통 메뉴뿐이다. 본문 확보 표시가 있지만 호출 보존을 확인할 기사 내용은 없다. |
| 6 | doc-14602bdc4c1a482fbd1fb1a5226882b3 | Fail | 실제 문서 본문 없이 정상 수집 결과로 처리했다. | https://www.uber.com/blog/engineering/page/34 문장0~28은 공통 메뉴다. 본문 확보 표시와 달리 기사 내용이나 조회 지연의 근거가 없다. |
| 7 | doc-eb1580685764495e94094accdf0fd66e | Fail | 실제 문서 본문 없이 정상 수집 결과로 처리했다. | https://www.uber.com/blog/engineering?id=998638 문장0~28은 공통 메뉴뿐이다. 개별 문서의 실제 본문을 수집했다는 표시는 내용으로 뒷받침되지 않는다. |
| 8 | doc-36f633dd6c924ab7b5f0632d6c3a469c | Fail | 실제 문서 본문 없이 정상 수집 결과로 처리했다. | http://uber.com/blog/engineering 문장0~28은 공통 메뉴다. 정상 수집으로 저장되었지만 후속 기술 근거를 확인할 본문이 없다. |
| 9 | doc-a5d3c4cd09ed4495aa06f3ca9d8e5b05 | Fail | 실제 문서 본문 없이 정상 수집 결과로 처리했다. | https://www.uber.com/blog/engineering?id=26 문장0~28은 공통 메뉴다. 배정 정합성 관련 기사 본문이 없는데 본문 확보 표시가 있다. |
| 10 | doc-d733dc20a45941abb3ebd84326d04b7a | Fail | 실제 문서 본문 없이 정상 수집 결과로 처리했다. | https://www.uber.com/blog/engineering/backend 문장0~21은 분류·날짜 목록뿐이다. 실제 기술 문서의 제목·내용을 확인할 수 없지만 본문 확보로 저장되었다. |
| 11 | doc-99633f359a554a31841058e772f8a0c3 | Fail | 실제 문서 본문 없이 정상 수집 결과로 처리했다. | https://www.uber.com/blog/engineering/page/2 문장0~27은 분류·날짜 목록이다. 처리량 검증에 사용할 실제 문서 본문은 수집되지 않았다. |
| 12 | doc-a503f98c18bc41238a79a469cf4329c9 | Fail | 실제 문서 본문 없이 정상 수집 결과로 처리했다. | https://www.uber.com/blog/california/engineering 문장0~28은 번역된 공통 메뉴다. 기술 기사 본문이 없는데 본문 확보로 저장되었다. |
| 13 | doc-71f06aba5075499aac7e75cf24ebf679 | Fail | 실제 문서 본문 없이 정상 수집 결과로 처리했다. | https://www.uber.com/blog/engineering?id=50 문장0~28은 공통 메뉴다. 정상 수집 표시와 달리 기술 근거를 확인할 본문이 없다. |
| 14 | doc-787c7c85108a439f91a0cbab06d7716e | Fail | 실제 문서 본문 없이 정상 수집 결과로 처리했다. | https://www.uber.com/blog/engineering?id=879 문장0~28은 공통 메뉴다. 기사 본문 대신 탐색 요소만 저장되어 후속 확인에 쓸 수 없다. |
| 15 | doc-8c38ec4263394bf996c7078a9d9d80cb | Fail | 실제 문서 본문 없이 정상 수집 결과로 처리했다. | https://www.uber.com/blog/engineering?id=118%2Cwww.uber.com%2Fnz%2Fen%2Fcareers%2Fdesign%2Cuber.com%2C0.33170733 문장0~28은 공통 메뉴다. 본문 확보 표시가 있지만 개별 기술 문서 내용은 없다. |
| 16 | doc-2292533602934f19920c65f4a1b93983 | Fail | 실제 문서 본문 없이 정상 수집 결과로 처리했다. | https://www.uber.com/blog/connecticut/engineering 문장0~28은 공통 메뉴다. 위치 처리량을 확인할 본문 없이 정상 수집 결과로 저장되었다. |
| 17 | doc-512f908304384401828eb0266982feaf | Fail | 실제 문서 본문 없이 정상 수집 결과로 처리했다. | https://www.uber.com/blog/washington/engineering 문장0~28은 공통 메뉴다. 기술 기사 본문을 확보했다는 표시를 뒷받침할 내용이 없다. |
| 18 | doc-13c77218cbfa4c5199955f8ab9bec30a | Fail | 실제 문서 본문 없이 정상 수집 결과로 처리했다. | https://www.uber.com/blog/los-angeles/ride 문장0~28은 공통 메뉴뿐이다. 정상 수집 목록에 있지만 호출 보존 관련 본문은 없다. |
| 19 | doc-c3c4589f810e48d0a490e5104a9cdd98 | Fail | 실제 문서 본문 없이 정상 수집 결과로 처리했다. | https://www.uber.com/blog/ride 문장0~28은 공통 메뉴다. 개별 문서 본문이 없는데 본문 확보로 저장되었다. |
| 20 | doc-fd8b6c6185ef4b3ea55c5cdf0982b46b | Fail | 실제 문서 본문 없이 정상 수집 결과로 처리했다. | https://www.uber.com/blog/engineering?id=98 문장0~28은 공통 메뉴다. 배정 정합성의 후속 확인에 사용할 실제 기사 내용이 없다. |
| 21 | doc-bdb89abd63934085b0a78ae98d9e0c06 | Fail | 실제 문서 본문 없이 정상 수집 결과로 처리했다. | https://www.uber.com/blog/washington-dc/ride 문장0~28은 공통 메뉴다. 실제 기술 문서 본문 없이 정상 수집으로 저장되었다. |
| 22 | fetch:https://www.uber.com/blog/research/dynamic-pricing-and-matching-in-ride-hailing-platforms | 판단 불가 | HTTP 오류로 본문 수집에 실패하면 품질 판정에서 제외한다. | fetch_failures의 https://www.uber.com/blog/research/dynamic-pricing-and-matching-in-ride-hailing-platforms 요청은 지역별 주소로 이동한 뒤 HTTP 404로 실패했다. 본문·문서 ID·문장 번호가 없으며 정상 본문으로 처리한 기록도 없다. |
| 23 | fetch:https://eng.uber.com/blog/apache-hudi-at-uber | 판단 불가 | HTTP 오류로 본문 수집에 실패하면 품질 판정에서 제외한다. | fetch_failures의 https://eng.uber.com/blog/apache-hudi-at-uber 요청은 HTTP 404로 실패했다. 접근 실패와 내용 수집 품질은 구분하며 본문·문서 ID·문장 번호는 없다. |
| 24 | fetch:http://eng.uber.com/blog/apache-hudi-at-uber | 판단 불가 | HTTP 오류로 본문 수집에 실패하면 품질 판정에서 제외한다. | fetch_failures의 http://eng.uber.com/blog/apache-hudi-at-uber 요청은 HTTPS 주소로 이동한 뒤 HTTP 404로 실패했다. 중복 선정 문제와 별개인 실행 오류이며 본문·문서 ID·문장 번호는 없다. |
| 25 | fetch:https://www.uber.com/blog/search/pinot | 판단 불가 | HTTP 오류로 본문 수집에 실패하면 품질 판정에서 제외한다. | fetch_failures의 https://www.uber.com/blog/search/pinot 요청은 지역별 검색 주소에서 HTTP 404로 실패했다. 본문·문서 ID·문장 번호가 없어 실제 본문 수집의 유효성을 판정할 수 없다. |
| 26 | fetch:https://www.uber.com/blog/search/data+analytics/page/5 | 판단 불가 | HTTP 오류로 본문 수집에 실패하면 품질 판정에서 제외한다. | fetch_failures의 https://www.uber.com/blog/search/data+analytics/page/5 요청은 지역별 주소에서 HTTP 404로 실패했다. 본문·문서 ID·문장 번호가 없고 실패는 정상 수집과 구분되어 있다. |
| 27 | fetch:https://www.uber.com/blog/search/data+analytics | 판단 불가 | HTTP 오류로 본문 수집에 실패하면 품질 판정에서 제외한다. | fetch_failures의 https://www.uber.com/blog/search/data+analytics 요청은 지역별 주소에서 HTTP 404로 실패했다. 본문 수집 결과가 없어 문서 ID·문장 번호도 없다. |
| 28 | fetch:https://www.uber.com/blog/research/driver-surge-pricing | 판단 불가 | HTTP 오류로 본문 수집에 실패하면 품질 판정에서 제외한다. | fetch_failures의 https://www.uber.com/blog/research/driver-surge-pricing 요청은 지역별 주소에서 HTTP 404로 실패했다. 주제 선별 문제와 별개로 실행 오류를 기록하며 본문·문서 ID·문장 번호는 없다. |
| 29 | fetch:https://eng.uber.com/blog/ride/page/2 | 판단 불가 | HTTP 오류로 본문 수집에 실패하면 품질 판정에서 제외한다. | fetch_failures의 https://eng.uber.com/blog/ride/page/2 요청은 HTTP 404로 실패했다. 실제 본문이 없고 문서 ID·문장 번호도 없어 수집 내용의 품질은 판단하지 않는다. |
| 30 | fetch:https://www.uber.com/blog/search/data+analytics/page/2 | 판단 불가 | HTTP 오류로 본문 수집에 실패하면 품질 판정에서 제외한다. | fetch_failures의 https://www.uber.com/blog/search/data+analytics/page/2 요청은 지역별 주소에서 HTTP 404로 실패했다. 본문·문서 ID·문장 번호가 없으며 정상 수집으로 처리하지 않았다. |
| 31 | fetch:https://eng.uber.com/blog/los-angeles/ride | 판단 불가 | HTTP 오류로 본문 수집에 실패하면 품질 판정에서 제외한다. | fetch_failures의 https://eng.uber.com/blog/los-angeles/ride 요청은 HTTP 404로 실패했다. 다른 호스트의 유사 페이지 본문으로 이 실패를 대체하지 않으며 대상 문서 ID·문장 번호는 없다. |
| 32 | fetch:https://www.uber.com/blog/puc-approves-two-year-license | 판단 불가 | HTTP 오류로 본문 수집에 실패하면 품질 판정에서 제외한다. | fetch_failures의 https://www.uber.com/blog/puc-approves-two-year-license 요청은 지역별 주소에서 HTTP 404로 실패했다. 무관한 출처 선정과 실행 오류를 구분하며 본문·문서 ID·문장 번호는 없다. |
