# 최초 진단 Middle 평가 상세

3-1은 검색 호출 연결 보정 전 판정이다. 원본 이력으로 보존하며, 보정 후 3-1을 대신할 유효 결과로 사용하지 않는다.

[주요 실험 기록](../research-tuning.md) · [원본 JSON](../../../../.archgen/m7-followup/current-criteria-20261019/baseline/middle/research.json) · [당시 평가 기준](../../../../.archgen/m7-followup/current-criteria-20261019/baseline/middle/research-criteria.md) · [Trace](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/0d44655da5f648338cea714308b2bd84)

전체 186건: Pass 82 · Fail 86 · 판단 불가 18. 아래 표에는 모든 Fail과 판단 불가를 생략 없이 기록했다. Pass도 기준별 개수를 표시하며 개별 근거는 원본 JSON에 보존한다.

## 기준별 전체 집계

| 평가 기준 | Pass | Fail | 판단 불가 |
| --- | --- | --- | --- |
| 1-1 평가 초점 반영 | 1 | 0 | 0 |
| 1-2 후보 도출의 타당성 | 5 | 0 | 0 |
| 2-1 후보 검증에 적합한 쿼리 | 5 | 0 | 0 |
| 3-1 검색 결과의 관련성 | 9 | 2 | 0 |
| 4-1 출처 선정의 타당성 | 24 | 55 | 2 |
| 5-1 본문 수집의 유효성 | 36 | 29 | 16 |
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
| 1 | call_lhvocnqAx6ZoPwSFNx4hzsx9 | Fail | 검색 결과의 관련성: 중복 배정 검증 후보 없이 목록·다른 주제를 수집 대상으로 처리하면 실패한다. | 첫 query-3 결과 1–9위는 기술 블로그 목록의 변형 URL이고, 10위 doc-a33ba1c544794b1896f809f6433d4f03, https://www.uber.com/blog/uber-beacon-bluetooth-mobile-app 는 문장 4–8·55–65에서 배정 후 차량 식별을 다룬다. 운전자 배정 경쟁·일관성을 검토할 후보가 없는데 이 결과들을 본문 수집 대상으로 처리했다. 후속 재검색은 별도로 평가했다. |
| 2 | call_KxAxxVNPhSOA9DEZaYqOtHN6 | Fail | 검색 결과의 관련성: 요청 보존·재처리 후보 없이 일반 목록을 수집 대상으로 처리하면 실패한다. | 첫 query-6의 9개 결과는 지역별 이용 안내 목록이다. 예를 들어 doc-edc4df92293841cf9849c46e64d63b86, https://www.uber.com/blog/dallas/ride 문장 0–28은 공통 메뉴뿐이다. 내구성·재처리 문서 후보가 없는데 목록 전체를 수집했다. 이후 장애 관련 재검색의 성과와 구분했다. |

## 4-1 출처 선정의 타당성

### 당시 문서에 명시된 판정 기준

- Pass: 검색 결과 중 설계 범위와 후보 검증에 관련되고 게시 주체를 식별할 수 있는 문서를 선택한다. 동일 내용의 중복 URL이나 근거가 부족한 목록·홍보 페이지를 불필요하게 우선하지 않는다.
- Fail: 관련성이나 출처를 확인하지 않은 채 무관한·중복된·본문 근거가 없는 문서를 선택하고, 검색 결과에 있던 더 적절한 출처를 뚜렷한 이유 없이 제외한다.

공식 출처가 아니라는 이유만으로 Fail하지 않는다. 이 평가는 저장된 검색 결과에서 실제 선택 가능한 문서를 기준으로 한다.

### 모든 Fail과 판단 불가 원문

| 번호 | 평가 대상 | 판정 | 실제 적용한 기준 원문 | 판단 근거 원문 |
| --- | --- | --- | --- | --- |
| 1 | doc-dad219859d0d4ad980cce5ced4298a12 | Fail | 출처 선정의 타당성: 평가 초점과 무관한 문서를 불필요하게 선택하면 실패한다. | https://www.uber.com/blog/new-rider-app-architecture 문장 19–27·43–92는 모바일 코드 격리와 앱 구조를 다룬다. 주변 검색·배정 경쟁·위치 처리·서버 호출 보존을 검증하는 문서가 아니며, 같은 query-1에 배차 이벤트 문서도 있었다. |
| 2 | doc-9b0e784a39fe4e3eb94030e14d4aa502 | Fail | 출처 선정의 타당성: 동일 내용의 중복 URL을 불필요하게 선택하면 실패한다. | https://www.uber.com/blog/new-rider-app-architecture?ref=highscalability.com 문장 0–117은 doc-dad219859d0d4ad980cce5ced4298a12와 같다. 추적 매개변수만 다른 모바일 구조 문서를 중복 수집할 조사상 이유가 기록되지 않았다. |
| 3 | doc-707353c9b07f4ea6bc334b3a5ebd392d | Fail | 출처 선정의 타당성: 동일 내용의 중복 URL을 불필요하게 선택하면 실패한다. | https://www.uber.com/blog/visualizing-city-cores-with-h3?ref=highscalability.com 문장 0–23은 정규 URL의 doc-b411fee3bdd94700a5ab36d96530dc90와 같다. H3 관련성은 있지만 두 주소를 별도 본문 대상으로 선택할 이유는 없다. |
| 4 | doc-3b0b5d3924c840fd8b5885b728801186 | Fail | 출처 선정의 타당성: 근거가 부족한 일반 목록을 불필요하게 우선하면 실패한다. | https://www.uber.com/blog/engineering 은 검색 제목부터 일반 목록이며 문장 0–28도 공통 메뉴다. 같은 저장 검색 결과에 Ringpop·배차 이벤트 등 구체적 기술 문서가 있는데 이 목록을 후보 검증용 본문 대상으로 선택했다. |
| 5 | doc-3b403bbf3c274014a3e9e04969044347 | Fail | 출처 선정의 타당성: 중복된 일반 목록을 불필요하게 선택하면 실패한다. | https://www.uber.com/blog/engineering?id=98 문장 0–28은 doc-3b0b5d3924c840fd8b5885b728801186와 같은 메뉴다. 검색 결과에서도 동일 목록 제목이며 매개변수별 수집이 후보 검증에 기여할 이유가 없다. |
| 6 | doc-da098015abff4c81a72696fe1176ec44 | Fail | 출처 선정의 타당성: 중복된 일반 목록을 불필요하게 선택하면 실패한다. | https://www.uber.com/blog/engineering?id=118%2Cwww.uber.com%2Fnz%2Fen%2Fcareers%2Fdesign%2Cuber.com%2C0.33170733 문장 0–28은 공통 메뉴뿐이다. 복잡한 매개변수가 붙은 동일 목록이며 매칭 품질 문제를 검증할 문서가 아니다. |
| 7 | doc-a7a8732e11064134964b57c39ff0aa47 | Fail | 출처 선정의 타당성: 근거가 부족한 목록을 불필요하게 선택하면 실패한다. | https://www.uber.com/blog/engineering/backend 문장 0–21은 분류·날짜·문서 수 목록이다. query-4에는 수집 구조를 설명하는 구체적 기술 문서가 있었으므로 이 분류 페이지를 처리량 근거 수집 대상으로 택한 타당성이 없다. |
| 8 | doc-79d799681dc14af7a707a0315c384adf | Fail | 출처 선정의 타당성: 무관한 일반 목록을 선택하면 실패한다. | https://www.uber.com/blog?id=510%2Cwww.uber.com%2Fin%2Fte%2Fcareers%2Flocations%2Cuber.com%2C0.75416136 문장 0–28은 공통 메뉴다. 검색 제목도 전체 소식 목록으로 위치 처리량이나 매칭 설계와의 연결이 없다. |
| 9 | doc-f4d8c30df1904b5d9e03dda8431bf8ea | Fail | 출처 선정의 타당성: 근거가 부족한 목록을 불필요하게 선택하면 실패한다. | https://www.uber.com/blog/engineering/page/2 문장 0–27은 문서 수·분류·날짜만 제공한다. 구체적 시스템 동작이나 처리량 제약을 확인할 본문이 아닌 일반 페이지를 선택했다. |
| 10 | doc-cff0f76369ae489b9cb6d28c4da4334d | Fail | 출처 선정의 타당성: 동일 내용의 중복 URL을 불필요하게 선택하면 실패한다. | https://www.uber.com/blog/gairos-scalability?ref=highscalability.com 문장 0–112는 doc-1834e25af4c045f397d45af0afc0641d와 같다. 처리량·핫스팟 관련성은 있으나 정규 URL과 별도로 수집할 이유가 기록되지 않았다. |
| 11 | doc-edc4df92293841cf9849c46e64d63b86 | Fail | 출처 선정의 타당성: 무관한 이용 안내 목록을 선택하면 실패한다. | https://www.uber.com/blog/dallas/ride 문장 0–28은 공통 메뉴다. 지역별 이용 안내는 피크 호출의 내구성·재처리 설계와 관련되지 않는다. |
| 12 | doc-e9f17a4556f44f12b22cc94bed25d985 | Fail | 출처 선정의 타당성: 무관한 이용 안내 목록을 선택하면 실패한다. | https://www.uber.com/blog/los-angeles/ride 문장 0–28은 공통 메뉴이며 다른 지역 목록과도 같다. 호출 보존·복구를 검증할 출처가 아니다. |
| 13 | doc-6af00c3270d4492fa029100048121d6f | Fail | 출처 선정의 타당성: 무관한 이용 안내 목록을 선택하면 실패한다. | https://www.uber.com/blog/ride/page/2 문장 0–28은 공통 메뉴다. 일반 이용 안내의 다음 페이지를 내구성 있는 호출 처리의 본문 대상으로 선택할 연결 근거가 없다. |
| 14 | doc-c7f90177356443cc8868074931173c12 | Fail | 출처 선정의 타당성: 설계 범위·평가 초점과 연결되지 않는 문서를 불필요하게 선택하면 실패한다. | https://www.uber.com/blog/uber-central 문장 18–27·29–43은 기업 이용자 귀속·청구 연계·웹 화면 개발을 중심으로 한다. 호출 기능은 언급하지만 주변 검색, 중복 배정, 위치 처리, 피크 보존의 설계 근거는 아니며 청구는 제외 범위다. |
| 15 | doc-76ebc758f451486598da0af29e9f119e | Fail | 출처 선정의 타당성: 평가 초점과 무관한 문서를 불필요하게 선택하면 실패한다. | https://www.uber.com/blog/rewrite-uber-carbon-app 문장 21–51·53–85는 앱 재작성의 제품·조직·모바일 구조 문제를 다룬다. 운전자 위치 수집이나 배정 상태의 서버 처리 설계와 연결되는 출처를 선택한 것이 아니다. |
| 16 | doc-c7667164e7634c8cbf17cc8ad6e9d0d5 | Fail | 출처 선정의 타당성: 구체적 근거가 부족한 행사 소개를 불필요하게 선택하면 실패한다. | https://www.uber.com/blog/uber-technology-day 문장 8–29·38–41은 발표 목록과 행사 요약이다. 피크 대응·데이터 처리 발표를 소개하지만 해당 설계 방법의 본문은 없으며 저장 검색 결과에는 직접적인 기술 문서가 있었다. |
| 17 | doc-75eec65b040448f19944ec29a5b67c37 | Fail | 출처 선정의 타당성: 근거가 부족한 일반 목록을 불필요하게 선택하면 실패한다. | https://www.uber.com/blog/engineering/page/41 문장 0–28은 공통 메뉴다. 주변 검색 지연을 확인할 개별 문서가 아니라 기술 블로그 목록을 선택했다. |
| 18 | doc-4330be8697154dec9ea557fb7085258a | Fail | 출처 선정의 타당성: 중복된 일반 목록을 불필요하게 선택하면 실패한다. | https://www.uber.com/blog/engineering?id=879 문장 0–28은 다른 기술 블로그 목록 주소와 같은 메뉴다. 배정 일관성의 근거가 없는 변형 URL을 추가 수집했다. |
| 19 | doc-abb21fcae90147b69bfd22869f85e6e4 | Fail | 출처 선정의 타당성: 중복된 일반 목록을 불필요하게 선택하면 실패한다. | https://www.uber.com/blog/engineering?countryiso2=us%252525252525252525252525252525252525252525252525252525252525252525255Cu0022%3F 문장 0–28은 공통 메뉴다. 동일 목록의 매개변수 변형을 배정 검증 대상으로 선택할 이유가 없다. |
| 20 | doc-f2411d5fe5aa4999bb92084f4e19bd35 | Fail | 출처 선정의 타당성: 중복된 일반 목록을 불필요하게 선택하면 실패한다. | https://www.uber.com/blog/engineering?id=x 문장 0–28은 공통 메뉴다. 검색 결과의 동일 목록 제목과 URL 형태만으로도 개별 배정 기술 문서가 아님을 알 수 있다. |
| 21 | doc-c501f2f29d464fdfbabddc325fbc53b4 | Fail | 출처 선정의 타당성: 근거가 부족한 지역별 목록을 불필요하게 선택하면 실패한다. | https://www.uber.com/blog/michigan/engineering 문장 0–28은 공통 메뉴다. 지역별 기술 분류 목록은 위치 갱신 처리량을 검증하는 개별 문서가 아니다. |
| 22 | doc-5614714cc0df43a5844748af912b09dc | Fail | 출처 선정의 타당성: 무관한 일반 목록을 선택하면 실패한다. | https://www.uber.com/blog?id=_msv%2B_23_&userId=_msv%2B_31_66466376737414242232424201 문장 0–28은 공통 메뉴다. 전체 소식 목록의 매개변수 변형이며 위치 처리의 설계 근거가 없다. |
| 23 | doc-d5a9381613e34073b6cbdc0095f4e102 | Fail | 출처 선정의 타당성: 근거가 부족한 지역별 목록을 불필요하게 선택하면 실패한다. | https://www.uber.com/blog/washington/engineering 문장 0–28은 공통 메뉴다. 처리량 검증 문서 대신 지역별 분류 목록을 추가 선택했다. |
| 24 | doc-c59858d504f540699e67ac113300403b | Fail | 출처 선정의 타당성: 근거가 부족한 일반 목록을 불필요하게 선택하면 실패한다. | https://uber.com/blog/engineering/page/23 문장 0–28은 공통 메뉴다. query-5의 Ringpop처럼 직접 관련된 문서가 있는데도 일반 목록을 별도 수집 대상으로 선택했다. |
| 25 | doc-6b00432c5a8441348230076abd79f667 | Fail | 출처 선정의 타당성: 무관한 이용 안내 목록을 선택하면 실패한다. | http://uber.com/blog/ride 문장 0–28은 공통 메뉴다. 호출 보존·재처리 문제를 확인할 기술 문서가 아닌 일반 이용 안내 목록이다. |
| 26 | doc-bc43ed1f2533479dbfdd68fd823a4bb1 | Fail | 출처 선정의 타당성: 무관한 이용 안내 목록을 선택하면 실패한다. | https://www.uber.com/blog/florida/ride 문장 0–28은 다른 지역 목록과 같은 메뉴다. 피크 호출 처리의 검증 자료로 선택할 관련성이 없다. |
| 27 | doc-3bac691cad824cc998e23987151b6975 | Fail | 출처 선정의 타당성: 무관한 이용 안내 목록을 선택하면 실패한다. | https://www.uber.com/blog/arizona/ride 문장 0–28은 공통 메뉴다. 지역 이용 안내는 서버 요청 내구성·복구 방식과 연결되지 않는다. |
| 28 | doc-6ac783d1116742d4bef966220274bf11 | Fail | 출처 선정의 타당성: 제외 범위의 동작을 중심으로 한 문서를 불필요하게 선택하면 실패한다. | https://www.uber.com/blog/driver-app-optimistic-mode 문장 8–18·60–67·76–83은 운행 시작·종료의 오프라인 낙관 처리다. 서버에서 접수한 호출의 피크 보존과 다르며, 원문도 예측 가능한 응답이라는 조건을 둔다. 범위 밖 운행 처리 자료를 선택했다. |
| 29 | doc-6f3a7b2d040f44f08c48bf775d7dbc16 | Fail | 출처 선정의 타당성: 중복된 일반 목록을 불필요하게 선택하면 실패한다. | https://www.uber.com/blog/engineering?id=26 문장 0–28은 공통 메뉴다. 다른 기술 목록 주소와 중복되며 배정 상태 전이에 관한 문서가 아니다. |
| 30 | doc-4692e25f93bf4abb8852f47471e1b813 | Fail | 출처 선정의 타당성: 중복된 일반 목록을 불필요하게 선택하면 실패한다. | https://www.uber.com/blog/engineering?uber_client_name=706 문장 0–28은 공통 메뉴다. 클라이언트 매개변수만 다른 목록을 별도 일관성 검증 출처로 수집했다. |
| 31 | doc-ba60911657394893b00ef5653d2f43c4 | Fail | 출처 선정의 타당성: 중복된 일반 목록을 불필요하게 선택하면 실패한다. | https://www.uber.com/blog/engineering?id=72 문장 0–28은 공통 메뉴다. 동일 목록 변형을 중복 선택했으며 중복 배정 방지의 기술적 근거가 없다. |
| 32 | doc-9ee80077898c4014a52d0fa70127fd76 | Fail | 출처 선정의 타당성: 근거가 부족한 지역별 목록을 불필요하게 선택하면 실패한다. | https://www.uber.com/blog/connecticut/engineering 문장 0–28은 공통 메뉴다. 위치 수집 처리량의 자료가 아니라 다른 지역 목록의 반복이다. |
| 33 | doc-cf1994194f704db3ac19114e0f0b771c | Fail | 출처 선정의 타당성: 무관한 이용 안내 목록을 선택하면 실패한다. | https://www.uber.com/blog/austin/ride 문장 0–28은 공통 메뉴다. 피크 호출 보존·복구를 설명하지 않는 지역별 이용 안내 목록이다. |
| 34 | doc-de4a210a3918482c91a6c2e13fa568b0 | Fail | 출처 선정의 타당성: 무관한 이용 안내 목록을 선택하면 실패한다. | https://www.uber.com/blog/new-orleans/ride 문장 0–28은 공통 메뉴다. 다른 지역 목록과 같은 내용으로 호출 내구성 검증에 기여하지 않는다. |
| 35 | doc-141a9600f2ff4cfaaa02f8cfb8891565 | Fail | 출처 선정의 타당성: 무관한 이용 안내 목록을 선택하면 실패한다. | https://www.uber.com/blog/new-york/ride 문장 0–28은 공통 메뉴다. 요청 보존·재처리 설계 자료가 아닌 지역별 목록을 선택했다. |
| 36 | doc-a33ba1c544794b1896f809f6433d4f03 | Fail | 출처 선정의 타당성: 다른 의미의 매칭을 다루는 문서를 선택하면 실패한다. | https://www.uber.com/blog/uber-beacon-bluetooth-mobile-app 문장 4–8·55–65는 이미 배정된 승객과 운전자의 색상 식별·승차 지점 동기화를 다룬다. 동시 호출에 대한 중복 배정 방지와는 다른 문제이며 배정 확정 이후의 내용이다. |
| 37 | doc-388948f98ba1434997c3f49ae32fa22c | Fail | 출처 선정의 타당성: 범위와 다른 품질 문제의 문서를 불필요하게 선택하면 실패한다. | https://www.uber.com/blog/uber-eats-trip-optimization 문장 7–18·75–94는 음식 준비·주차·대기 상태 추론으로 배송 출발 시점을 최적화한다. 차량 호출의 검색 지연·배정 경쟁·위치 갱신 처리량 문제와 다르며 공식 출처라는 이유만으로 선택하기에는 관련성이 부족하다. |
| 38 | doc-f38eef1fd5384386ad8f7962aeb19f67 | Fail | 출처 선정의 타당성: 동일 내용의 중복 URL을 불필요하게 선택하면 실패한다. | https://www.uber.com/blog/gatewayuberapi?ref=highscalability.com 문장 0–107은 doc-67e4d7253e724262ba57a8431f008b9a와 같다. 게이트웨이 확장 관련성은 있으나 정규 URL과 중복 수집할 이유는 기록되지 않았다. |
| 39 | doc-094a6689cbb84310993374907ca4da14 | 판단 불가 | 출처 선정의 타당성: 관련성과 게시 주체 확인 기록이 부족하면 판단을 보류한다. | https://www.youtube.com/watch?v=R_wWbHqpQTg 의 검색 제목은 실시간 지도 처리와 관련되지만 채널·영상 제작자 정보가 없다. doc-094a6689cbb84310993374907ca4da14 문장 0–1도 플랫폼 법적 고지뿐이어서 게시 주체 확인 여부를 판단할 수 없다. |
| 40 | doc-54bfe10bb43a46d79d732d06e26cb23a | Fail | 출처 선정의 타당성: 동일 내용의 중복 URL을 불필요하게 선택하면 실패한다. | https://www.uber.com/us/en/blog/orders-near-you 문장 0–100은 doc-47ee67ffbe4e4709bd1d7662d307c44c와 같다. 지역 경로만 다른 동일 기사를 별도 수집할 필요성이 기록되지 않았다. |
| 41 | doc-3676d05a7cf44b808593ca5b7e910a48 | 판단 불가 | 출처 선정의 타당성: 게시 주체 확인 기록이 부족하면 판단을 보류한다. | https://www.youtube.com/watch?v=GyPq2joHZv4&xstg=CAMSBhUDzO3xHw%3D%3D 의 검색 제목에는 매칭 대기 시간과 발표자 이름이 있지만 영상 채널·게시 주체는 없다. doc-3676d05a7cf44b808593ca5b7e910a48 문장 0–1도 법적 고지뿐이어서 출처 확인의 타당성을 확정할 수 없다. |
| 42 | doc-2ba024323ac641b8b81329d2758e9c70 | Fail | 출처 선정의 타당성: 제외 범위의 홍보성 문서를 선택하면 실패한다. | https://markets.businessinsider.com/news/stocks/data-consistency-and-scalability-in-high-concurrency-payment-systems-examined-in-yue-qi-s-research-1036087745 문장 0–12·18–20은 결제 시스템 연구의 보도자료다. brief가 제외한 결제 문제이며 운전자 배정 경쟁을 검증하지 않는다. 저장 검색 결과에는 매칭 관련 출처가 있었다. |
| 43 | doc-591936568726441a82624644743ade5e | Fail | 출처 선정의 타당성: 다른 주제의 일반 뉴스를 선택하면 실패한다. | https://finance.yahoo.com/news/uber-expands-women-driver-matching-190849377.html 문장 1–13은 여성 운전자 선택 기능과 법적 분쟁을 다룬다. 동시 배정의 상태 전이·일관성 설계를 검증할 기술 문서가 아니다. |
| 44 | fetch:https://www.uber.com/blog/case-study-first-step | Fail | 출처 선정의 타당성: 무관한 사례·홍보 문서를 선택하면 실패한다. | query-5 결과 5위 https://www.uber.com/blog/case-study-first-step 는 인력 업체와의 이용 기회 제공 사례로 표시된다. 같은 결과의 Ringpop과 달리 공간 분할·매칭 확장의 기술 자료가 아니다. HTTP 404는 별도 실행 오류이며 본문 문장 번호는 없다. |
| 45 | fetch:https://www.uber.com/blog/search/data+analytics/page/5 | Fail | 출처 선정의 타당성: 관련 개별 문서 대신 근거가 부족한 검색 목록을 선택하면 실패한다. | 첫 query-2 결과 7위 https://www.uber.com/blog/search/data+analytics/page/5 는 블로그 검색 목록이다. 같은 결과에 공간 인덱스 기술 기사가 있는데 일반 검색의 여러 페이지를 수집할 이유가 없다. HTTP 404로 본문·문장 번호는 없다. |
| 46 | fetch:https://www.uber.com/blog/search/data+analytics | Fail | 출처 선정의 타당성: 관련 개별 문서 대신 근거가 부족한 검색 목록을 선택하면 실패한다. | 첫 query-2 결과 8위 https://www.uber.com/blog/search/data+analytics 는 검색 목록이지 주변 운전자 조회의 기술 본문이 아니다. 구체적 기술 문서와 함께 불필요하게 선택했다. HTTP 404로 본문·문장 번호는 없다. |
| 47 | fetch:https://www.uber.com/blog/search/pinot | Fail | 출처 선정의 타당성: 관련 개별 문서 대신 근거가 부족한 검색 목록을 선택하면 실패한다. | 첫 query-2 결과 9위 https://www.uber.com/blog/search/pinot 는 기술 이름에 대한 검색 목록이다. 같은 결과의 공간 검색 기사보다 본문 근거가 부족한 목록을 추가 선택한 필요성이 없다. HTTP 404로 본문·문장 번호는 없다. |
| 48 | fetch:https://www.uber.com/blog/search/data+analytics/page/2 | Fail | 출처 선정의 타당성: 관련 개별 문서 대신 근거가 부족한 검색 목록을 선택하면 실패한다. | 첫 query-2 결과 10위 https://www.uber.com/blog/search/data+analytics/page/2 는 다른 검색 목록의 페이지 변형이다. 후보 검증용 개별 기술 문서가 아닌 목록을 반복 선택했다. HTTP 404로 본문·문장 번호는 없다. |
| 49 | fetch:https://www.uber.com/blog/piloting-estimated-earnings-per-active-hour-on-trip-requests | Fail | 출처 선정의 타당성: 품질 문제와 무관한 제품 안내를 선택하면 실패한다. | 후속 query-6 결과 6위 https://www.uber.com/blog/piloting-estimated-earnings-per-active-hour-on-trip-requests 는 호출 화면의 예상 수입 안내다. 같은 결과의 저장소·과부하 기술 문서와 달리 호출 보존·재처리를 검증하지 않는다. HTTP 404로 본문 문장 번호는 없다. |
| 50 | fetch:https://www.indeed.com/q-low-latency-programming-jobs.html | Fail | 출처 선정의 타당성: 무관한 채용 목록을 선택하면 실패한다. | 후속 query-2 결과 5위 https://www.indeed.com/q-low-latency-programming-jobs.html 는 저지연 개발 채용 목록이다. 주변 운전자 검색 설계 기사가 같은 결과에 있는데 무관한 목록을 선택했다. HTTP 403으로 본문·문장 번호는 없다. |
| 51 | fetch:https://www.indeed.com/q-ultra-low-latency-engineer-jobs.html | Fail | 출처 선정의 타당성: 무관한 채용 목록을 선택하면 실패한다. | 후속 query-2 결과 6위 https://www.indeed.com/q-ultra-low-latency-engineer-jobs.html 는 초저지연 기술자 채용 목록으로 차량 매칭의 검색 비용·제약을 확인할 자료가 아니다. HTTP 403은 별도 오류이며 본문 문장 번호는 없다. |
| 52 | fetch:https://www.instagram.com/reel/DamH0TfTAUJ | Fail | 출처 선정의 타당성: 게시 주체·기술 근거가 불분명한 단편 자료를 불필요하게 선택하면 실패한다. | 후속 query-3 결과 4위 https://www.instagram.com/reel/DamH0TfTAUJ 는 두 운전자의 동일 호출 수락에 관한 단편 제목뿐이며 작성 주체나 동시성 설계 설명이 없다. 저장 결과의 공식 매칭 자료보다 선정 근거가 부족하다. 수집은 빈 본문으로 실패해 문장 번호가 없다. |
| 53 | fetch:https://www.indeed.com/q-low-latency-engineer-jobs.html | Fail | 출처 선정의 타당성: 무관한 채용 목록을 선택하면 실패한다. | 후속 query-2 결과 7위 https://www.indeed.com/q-low-latency-engineer-jobs.html 는 채용 목록으로 주변 검색의 지연 설계 근거가 아니다. HTTP 403으로 본문·문장 번호는 없다. |
| 54 | fetch:https://www.indeed.com/q-low-latency-trading-engineer-jobs.html | Fail | 출처 선정의 타당성: 다른 산업의 채용 목록을 선택하면 실패한다. | 후속 query-2 결과 8위 https://www.indeed.com/q-low-latency-trading-engineer-jobs.html 는 거래 분야 채용 목록이다. 차량 주변 검색과 무관하며 동일 결과의 관련 설계 기사보다 선택 타당성이 없다. HTTP 403으로 본문 문장 번호는 없다. |
| 55 | fetch:https://www.indeed.com/companies/compare/Spark-Driver-1-vs-Uber-Drivers-7be24e9345f68158-606df48903ca7443 | Fail | 출처 선정의 타당성: 고용 비교 자료를 시스템 설계 출처로 선택하면 실패한다. | 후속 query-3 결과 7위 https://www.indeed.com/companies/compare/Spark-Driver-1-vs-Uber-Drivers-7be24e9345f68158-606df48903ca7443 는 운전자 고용 환경 비교다. 배정 상태의 일관성과 관련되지 않는다. HTTP 403으로 본문·문장 번호는 없다. |
| 56 | fetch:https://www.indeed.com/cmp/Uber/salaries/Driver/California?period=WEEKLY | Fail | 출처 선정의 타당성: 급여 정보를 시스템 설계 출처로 선택하면 실패한다. | 후속 query-3 결과 8위 https://www.indeed.com/cmp/Uber/salaries/Driver/California?period=WEEKLY 는 지역별 운전자 급여 자료다. 중복 배정 방지·상태 전이의 기술 근거가 아니다. HTTP 403으로 본문 문장 번호는 없다. |
| 57 | fetch:https://www.indeed.com/cmp/Uber/salaries/Driver/Knoxville-TN | Fail | 출처 선정의 타당성: 급여 정보를 시스템 설계 출처로 선택하면 실패한다. | 후속 query-3 결과 9위 https://www.indeed.com/cmp/Uber/salaries/Driver/Knoxville-TN 는 운전자 급여 정보로 배정 일관성과 무관하다. 같은 결과에 매칭 관련 자료가 있었다. HTTP 403으로 본문·문장 번호는 없다. |

## 5-1 본문 수집의 유효성

### 당시 문서에 명시된 판정 기준

- Pass: 선택한 문서의 실제 본문을 정상적으로 수집하여 후속 근거 확인에 사용할 수 있다.
- Fail: 본문 대신 검색 요약이나 다른 문서 내용을 수집하고 정상적인 본문으로 처리한다.

판단 불가/실행 오류: 접근 차단·타임아웃 등으로 본문 수집에 실패한 경우는 별도로 기록한다.

### 모든 Fail과 판단 불가 원문

| 번호 | 평가 대상 | 판정 | 실제 적용한 기준 원문 | 판단 근거 원문 |
| --- | --- | --- | --- | --- |
| 1 | doc-3b0b5d3924c840fd8b5885b728801186 | Fail | 본문 수집의 유효성: 공통 메뉴를 기술 본문 대신 수집 결과로 처리하면 실패한다. | https://www.uber.com/blog/engineering 문장 0–28은 광고·이용·음식·사업 등의 공통 메뉴뿐이다. 후보 검증용 기술 본문이나 문서 목록 내용이 없는데 fetched에 수집 결과로 기록됐고 별도 접근 오류는 없다. |
| 2 | doc-3b403bbf3c274014a3e9e04969044347 | Fail | 본문 수집의 유효성: 공통 메뉴를 본문 대신 수집 결과로 처리하면 실패한다. | https://www.uber.com/blog/engineering?id=98 문장 0–28은 공통 메뉴만 반복한다. 개별 기술 내용이 없는 비본문 추출 결과를 정상 수집 문서와 함께 기록했다. |
| 3 | doc-da098015abff4c81a72696fe1176ec44 | Fail | 본문 수집의 유효성: 공통 메뉴를 본문 대신 수집 결과로 처리하면 실패한다. | https://www.uber.com/blog/engineering?id=118%2Cwww.uber.com%2Fnz%2Fen%2Fcareers%2Fdesign%2Cuber.com%2C0.33170733 문장 0–28은 사이트 공통 메뉴다. 실제 기술 본문이 없고 수집 장애로 별도 분류되지 않았다. |
| 4 | doc-a7a8732e11064134964b57c39ff0aa47 | Fail | 본문 수집의 유효성: 분류·날짜 조각만으로 정상 기술 본문을 대체하면 실패한다. | https://www.uber.com/blog/engineering/backend 문장 0–21은 분류명·문서 수·날짜만 있다. 기사 내용이나 유효한 근거 설명 없이 메타데이터 조각만 수집 결과로 남았다. |
| 5 | doc-79d799681dc14af7a707a0315c384adf | Fail | 본문 수집의 유효성: 공통 메뉴를 본문 대신 수집 결과로 처리하면 실패한다. | https://www.uber.com/blog?id=510%2Cwww.uber.com%2Fin%2Fte%2Fcareers%2Flocations%2Cuber.com%2C0.75416136 문장 0–28은 사이트 공통 메뉴뿐이다. 후속 근거 확인에 사용할 본문이 수집되지 않았다. |
| 6 | doc-f4d8c30df1904b5d9e03dda8431bf8ea | Fail | 본문 수집의 유효성: 분류·날짜 조각만으로 정상 기술 본문을 대체하면 실패한다. | https://www.uber.com/blog/engineering/page/2 문장 0–27에는 분류·날짜·기사 수만 있다. 기술 설명이나 실제 기사 내용이 없는 목록 추출 조각을 수집 결과로 처리했다. |
| 7 | doc-edc4df92293841cf9849c46e64d63b86 | Fail | 본문 수집의 유효성: 공통 메뉴를 본문 대신 수집 결과로 처리하면 실패한다. | https://www.uber.com/blog/dallas/ride 문장 0–28은 공통 메뉴뿐이다. 선택 URL의 실질 내용이 없이 비본문이 fetched에 기록됐으며 별도 실행 오류는 없다. |
| 8 | doc-e9f17a4556f44f12b22cc94bed25d985 | Fail | 본문 수집의 유효성: 공통 메뉴를 본문 대신 수집 결과로 처리하면 실패한다. | https://www.uber.com/blog/los-angeles/ride 문장 0–28은 사이트 메뉴다. 지역 페이지의 실질 내용이나 후보 검증용 본문은 수집되지 않았다. |
| 9 | doc-6af00c3270d4492fa029100048121d6f | Fail | 본문 수집의 유효성: 공통 메뉴를 본문 대신 수집 결과로 처리하면 실패한다. | https://www.uber.com/blog/ride/page/2 문장 0–28은 공통 메뉴만 반복한다. 실제 페이지 내용 없이 비본문 추출 결과를 수집 문서로 처리했다. |
| 10 | doc-75eec65b040448f19944ec29a5b67c37 | Fail | 본문 수집의 유효성: 공통 메뉴를 본문 대신 수집 결과로 처리하면 실패한다. | https://www.uber.com/blog/engineering/page/41 문장 0–28은 공통 메뉴다. 기술 본문이나 해당 목록의 실질 내용 없이 수집 문서로 기록됐다. |
| 11 | doc-4330be8697154dec9ea557fb7085258a | Fail | 본문 수집의 유효성: 공통 메뉴를 본문 대신 수집 결과로 처리하면 실패한다. | https://www.uber.com/blog/engineering?id=879 문장 0–28은 공통 메뉴만 제공한다. 후속 근거 확인에 쓸 실제 기술 본문이 없다. |
| 12 | doc-abb21fcae90147b69bfd22869f85e6e4 | Fail | 본문 수집의 유효성: 공통 메뉴를 본문 대신 수집 결과로 처리하면 실패한다. | https://www.uber.com/blog/engineering?countryiso2=us%252525252525252525252525252525252525252525252525252525252525252525255Cu0022%3F 문장 0–28은 사이트 메뉴다. 실제 기사 내용이 없는데 정상 수집 결과와 함께 기록됐다. |
| 13 | doc-f2411d5fe5aa4999bb92084f4e19bd35 | Fail | 본문 수집의 유효성: 공통 메뉴를 본문 대신 수집 결과로 처리하면 실패한다. | https://www.uber.com/blog/engineering?id=x 문장 0–28은 공통 메뉴다. 기술 본문 수집이 아닌 반복적인 비본문 추출이다. |
| 14 | doc-c501f2f29d464fdfbabddc325fbc53b4 | Fail | 본문 수집의 유효성: 공통 메뉴를 본문 대신 수집 결과로 처리하면 실패한다. | https://www.uber.com/blog/michigan/engineering 문장 0–28은 사이트 공통 메뉴뿐이다. 선택 페이지의 실질 내용이나 기술 근거는 확보되지 않았다. |
| 15 | doc-5614714cc0df43a5844748af912b09dc | Fail | 본문 수집의 유효성: 공통 메뉴를 본문 대신 수집 결과로 처리하면 실패한다. | https://www.uber.com/blog?id=_msv%2B_23_&userId=_msv%2B_31_66466376737414242232424201 문장 0–28은 공통 메뉴다. 실제 소식 본문이 없이 수집 결과로 처리됐다. |
| 16 | doc-d5a9381613e34073b6cbdc0095f4e102 | Fail | 본문 수집의 유효성: 공통 메뉴를 본문 대신 수집 결과로 처리하면 실패한다. | https://www.uber.com/blog/washington/engineering 문장 0–28은 공통 메뉴다. 정상적인 기술 본문이 수집되지 않았고 접근 오류로 별도 분류된 기록도 없다. |
| 17 | doc-c59858d504f540699e67ac113300403b | Fail | 본문 수집의 유효성: 공통 메뉴를 본문 대신 수집 결과로 처리하면 실패한다. | https://uber.com/blog/engineering/page/23 문장 0–28은 공통 메뉴만 반복한다. 후보 검증에 쓸 실제 본문이 없다. |
| 18 | doc-6b00432c5a8441348230076abd79f667 | Fail | 본문 수집의 유효성: 공통 메뉴를 본문 대신 수집 결과로 처리하면 실패한다. | http://uber.com/blog/ride 문장 0–28은 사이트 공통 메뉴다. 선택한 페이지의 실질 내용 없이 비본문을 수집 결과로 기록했다. |
| 19 | doc-bc43ed1f2533479dbfdd68fd823a4bb1 | Fail | 본문 수집의 유효성: 공통 메뉴를 본문 대신 수집 결과로 처리하면 실패한다. | https://www.uber.com/blog/florida/ride 문장 0–28은 공통 메뉴다. 지역별 안내의 본문이나 기술 근거는 수집되지 않았다. |
| 20 | doc-3bac691cad824cc998e23987151b6975 | Fail | 본문 수집의 유효성: 공통 메뉴를 본문 대신 수집 결과로 처리하면 실패한다. | https://www.uber.com/blog/arizona/ride 문장 0–28은 공통 메뉴만 있다. 별도 실패로 분류하지 않고 실질 본문 없는 결과를 문서로 기록했다. |
| 21 | doc-6f3a7b2d040f44f08c48bf775d7dbc16 | Fail | 본문 수집의 유효성: 공통 메뉴를 본문 대신 수집 결과로 처리하면 실패한다. | https://www.uber.com/blog/engineering?id=26 문장 0–28은 공통 메뉴다. 실질적인 기술 설명 없이 문서 수집 결과로 남았다. |
| 22 | doc-4692e25f93bf4abb8852f47471e1b813 | Fail | 본문 수집의 유효성: 공통 메뉴를 본문 대신 수집 결과로 처리하면 실패한다. | https://www.uber.com/blog/engineering?uber_client_name=706 문장 0–28은 공통 메뉴뿐이다. 후속 기술 근거 확인에 사용할 본문이 아니다. |
| 23 | doc-ba60911657394893b00ef5653d2f43c4 | Fail | 본문 수집의 유효성: 공통 메뉴를 본문 대신 수집 결과로 처리하면 실패한다. | https://www.uber.com/blog/engineering?id=72 문장 0–28은 사이트 메뉴만 반복한다. 실제 기술 본문을 확보한 결과로 볼 수 없다. |
| 24 | doc-9ee80077898c4014a52d0fa70127fd76 | Fail | 본문 수집의 유효성: 공통 메뉴를 본문 대신 수집 결과로 처리하면 실패한다. | https://www.uber.com/blog/connecticut/engineering 문장 0–28은 공통 메뉴다. 해당 페이지의 실질 내용이 아닌 비본문만 수집됐다. |
| 25 | doc-cf1994194f704db3ac19114e0f0b771c | Fail | 본문 수집의 유효성: 공통 메뉴를 본문 대신 수집 결과로 처리하면 실패한다. | https://www.uber.com/blog/austin/ride 문장 0–28은 공통 메뉴다. 해당 페이지의 실질 본문 없이 수집 결과로 처리됐다. |
| 26 | doc-de4a210a3918482c91a6c2e13fa568b0 | Fail | 본문 수집의 유효성: 공통 메뉴를 본문 대신 수집 결과로 처리하면 실패한다. | https://www.uber.com/blog/new-orleans/ride 문장 0–28은 공통 메뉴뿐이다. 후보 검증에 사용할 실제 내용이 수집되지 않았다. |
| 27 | doc-141a9600f2ff4cfaaa02f8cfb8891565 | Fail | 본문 수집의 유효성: 공통 메뉴를 본문 대신 수집 결과로 처리하면 실패한다. | https://www.uber.com/blog/new-york/ride 문장 0–28은 사이트 공통 메뉴다. 실질 본문이나 기술 설명 없이 문서 수집 결과로 남았다. |
| 28 | doc-094a6689cbb84310993374907ca4da14 | Fail | 본문 수집의 유효성: 법적 고지 등 비본문만 정상 문서 결과로 기록하면 실패한다. | https://www.youtube.com/watch?v=R_wWbHqpQTg 문장 0–1은 플랫폼 법적 고지뿐이다. 영상 설명·자막·기술 내용이 없는데 fetched 문서로 기록됐다. 접근 차단이나 타임아웃으로 별도 분류된 기록은 없어 원인을 임의로 만들지 않았다. |
| 29 | doc-3676d05a7cf44b808593ca5b7e910a48 | Fail | 본문 수집의 유효성: 법적 고지 등 비본문만 정상 문서 결과로 기록하면 실패한다. | https://www.youtube.com/watch?v=GyPq2joHZv4&xstg=CAMSBhUDzO3xHw%3D%3D 문장 0–1은 플랫폼 고지뿐이다. 발표의 설명·자막·기술 내용이 없이 fetched에 기록됐으며 별도 접근 장애 기록은 없다. |
| 30 | fetch:https://www.uber.com/blog/research/dynamic-pricing-and-matching-in-ride-hailing-platforms | 판단 불가 | 본문 수집의 유효성: HTTP 오류로 본문 확보에 실패한 경우 품질 실패와 구분한다. | fetch_failures의 https://www.uber.com/blog/research/dynamic-pricing-and-matching-in-ride-hailing-platforms 는 지역 경로로 이동한 뒤 HTTP 404가 발생했다. 본문과 문장 번호가 없으며 다른 내용을 정상 본문으로 대체한 기록도 없다. 실행 오류로 판단을 보류한다. |
| 31 | fetch:https://www.uber.com/blog/case-study-first-step | 판단 불가 | 본문 수집의 유효성: HTTP 오류는 선정 품질과 별도 기록한다. | https://www.uber.com/blog/case-study-first-step 는 fetch_failures에 HTTP 404로 기록됐다. 실제 본문·문장 번호가 없어 수집 유효성은 판단할 수 없다. 무관한 출처를 선택한 문제는 4-1에서 별도로 판정했다. |
| 32 | fetch:https://www.uber.com/blog/search/data+analytics/page/5 | 판단 불가 | 본문 수집의 유효성: HTTP 오류로 본문이 없으면 실행 오류로 구분한다. | https://www.uber.com/blog/search/data+analytics/page/5 는 지역 경로에서 HTTP 404로 실패했다. fetch_failures만 있고 본문·문장 번호가 없으므로 수집 품질 판정을 보류한다. |
| 33 | fetch:https://www.uber.com/blog/search/data+analytics | 판단 불가 | 본문 수집의 유효성: HTTP 오류로 본문이 없으면 실행 오류로 구분한다. | https://www.uber.com/blog/search/data+analytics 는 fetch_failures에 HTTP 404로 기록됐다. 본문·문장 번호가 없으며 실패를 정상적인 기술 본문으로 처리한 기록은 없다. |
| 34 | fetch:https://www.uber.com/blog/search/pinot | 판단 불가 | 본문 수집의 유효성: HTTP 오류로 본문이 없으면 실행 오류로 구분한다. | https://www.uber.com/blog/search/pinot 는 지역 경로로 이동한 뒤 HTTP 404로 실패했다. 실제 본문과 문장 번호가 없어 수집 유효성을 판정할 수 없다. |
| 35 | fetch:https://www.uber.com/blog/search/data+analytics/page/2 | 판단 불가 | 본문 수집의 유효성: HTTP 오류로 본문이 없으면 실행 오류로 구분한다. | https://www.uber.com/blog/search/data+analytics/page/2 는 fetch_failures에 HTTP 404로 남았다. 본문·문장 번호가 없으므로 출처 선정 실패와 별개인 실행 오류로 처리한다. |
| 36 | fetch:https://medium.com/algomart/uber-system-design-handling-massive-scale-with-low-latency-bb87bf7572dd | 판단 불가 | 본문 수집의 유효성: 접근 차단은 품질 실패와 구분한다. | https://medium.com/algomart/uber-system-design-handling-massive-scale-with-low-latency-bb87bf7572dd 는 HTTP 403으로 실패했다. fetch_failures에 접근 오류만 있으며 본문·문장 번호가 없어 수집 내용을 평가할 수 없다. |
| 37 | fetch:https://www.uber.com/blog/piloting-estimated-earnings-per-active-hour-on-trip-requests | 판단 불가 | 본문 수집의 유효성: HTTP 오류는 선정 품질과 별도 기록한다. | https://www.uber.com/blog/piloting-estimated-earnings-per-active-hour-on-trip-requests 는 지역 경로에서 HTTP 404로 실패했다. 본문·문장 번호가 없어 수집 품질은 판단 불가이며 선정 관련성은 별도 판정했다. |
| 38 | fetch:https://www.indeed.com/q-low-latency-programming-jobs.html | 판단 불가 | 본문 수집의 유효성: 접근 차단은 선정 실패와 구분한다. | https://www.indeed.com/q-low-latency-programming-jobs.html 는 fetch_failures에 HTTP 403으로 기록됐다. 본문·문장 번호가 없으므로 수집 유효성은 판단 불가다. 채용 목록 선정의 부적절함과 구분한다. |
| 39 | fetch:https://www.indeed.com/q-ultra-low-latency-engineer-jobs.html | 판단 불가 | 본문 수집의 유효성: 접근 차단은 선정 실패와 구분한다. | https://www.indeed.com/q-ultra-low-latency-engineer-jobs.html 는 HTTP 403으로 수집에 실패했다. 실제 본문·문장 번호가 없어 수집 품질은 판단할 수 없다. |
| 40 | fetch:https://www.instagram.com/reel/DamH0TfTAUJ | 판단 불가 | 본문 수집의 유효성: 빈 본문으로 명시된 수집 실패는 실행 오류로 구분한다. | https://www.instagram.com/reel/DamH0TfTAUJ 는 fetch_failures에 본문이 비어 있다고 명시됐다. 문장 번호가 없고 정상 본문으로 대체 처리한 기록도 없어 수집 유효성은 판단 불가다. 빈 본문의 원인은 추정하지 않았다. |
| 41 | fetch:https://www.indeed.com/q-low-latency-engineer-jobs.html | 판단 불가 | 본문 수집의 유효성: 접근 차단은 선정 실패와 구분한다. | https://www.indeed.com/q-low-latency-engineer-jobs.html 는 HTTP 403으로 실패했다. fetch_failures 외에 실제 본문·문장 번호가 없어 수집 내용을 평가할 수 없다. |
| 42 | fetch:https://www.indeed.com/q-low-latency-trading-engineer-jobs.html | 판단 불가 | 본문 수집의 유효성: 접근 차단은 선정 실패와 구분한다. | https://www.indeed.com/q-low-latency-trading-engineer-jobs.html 는 HTTP 403으로 실패했다. 본문·문장 번호가 없어 수집 품질은 판단 불가이며 다른 산업의 채용 목록 선정 문제와 구분한다. |
| 43 | fetch:https://www.indeed.com/companies/compare/Spark-Driver-1-vs-Uber-Drivers-7be24e9345f68158-606df48903ca7443 | 판단 불가 | 본문 수집의 유효성: 접근 차단은 선정 실패와 구분한다. | https://www.indeed.com/companies/compare/Spark-Driver-1-vs-Uber-Drivers-7be24e9345f68158-606df48903ca7443 는 HTTP 403으로 실패했다. 실제 본문·문장 번호가 없으므로 수집 유효성을 판정하지 않는다. |
| 44 | fetch:https://www.indeed.com/cmp/Uber/salaries/Driver/California?period=WEEKLY | 판단 불가 | 본문 수집의 유효성: 접근 차단은 선정 실패와 구분한다. | https://www.indeed.com/cmp/Uber/salaries/Driver/California?period=WEEKLY 는 fetch_failures에 HTTP 403으로 기록됐다. 본문·문장 번호가 없어 수집 품질은 판단 불가다. 급여 자료 선정의 부적절함은 별도다. |
| 45 | fetch:https://www.indeed.com/cmp/Uber/salaries/Driver/Knoxville-TN | 판단 불가 | 본문 수집의 유효성: 접근 차단은 선정 실패와 구분한다. | https://www.indeed.com/cmp/Uber/salaries/Driver/Knoxville-TN 는 HTTP 403으로 수집에 실패했다. 실제 본문·문장 번호가 없어 수집 내용의 유효성은 판단할 수 없다. |
