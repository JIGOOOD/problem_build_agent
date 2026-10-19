# 수정 전 Senior 1회 평가 상세

새로 생성한 Research 결과를 평가한 실행이다.

[주요 실험 기록](../research-tuning.md) · [원본 JSON](../../../../.archgen/m7-followup/current-criteria-20261019/research-tuning/before/senior/1-evaluation-retry/research.json) · [당시 평가 기준](../../../../.archgen/m7-followup/current-criteria-20261019/research-tuning/before/senior/1-evaluation-retry/research-criteria.md) · [Trace](https://jp.cloud.langfuse.com/project/cmvdm67ux000ead0gx7mf5grb/traces/059911f13fc845f9b87d0e2cd9acddd5)

전체 223건: Pass 137 · Fail 65 · 판단 불가 21. 아래 표에는 모든 Fail과 판단 불가를 생략 없이 기록했다. Pass도 기준별 개수를 표시하며 개별 근거는 원본 JSON에 보존한다.

## 기준별 전체 집계

| 평가 기준 | Pass | Fail | 판단 불가 |
| --- | --- | --- | --- |
| 1-1 평가 초점 반영 | 1 | 0 | 0 |
| 1-2 후보 도출의 타당성 | 5 | 0 | 0 |
| 2-1 후보 검증에 적합한 쿼리 | 5 | 0 | 0 |
| 3-1 검색 결과의 관련성 | 12 | 0 | 0 |
| 4-1 출처 선정의 타당성 | 42 | 53 | 4 |
| 5-1 본문 수집의 유효성 | 70 | 12 | 17 |
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
| 1 | doc-8a00fa301fb3471aa99aa3e6ce5817a2 | Fail | 후보 검증과 무관한 자료를 수집 대상으로 선택했다. | query-1 결과 1위의 주식 분석을 선택했다. doc-8a00fa301fb3471aa99aa3e6ce5817a2 문장 1~7·37~58은 실적·투자 전망이며, 검색 지연이나 배정 경합 등 후보를 검증할 시스템 근거가 아니다. |
| 2 | doc-a8158c83a8f144a1acb661fae33dc460 | Fail | 범위와 다른 홍보 자료를 불필요하게 선택했다. | doc-a8158c83a8f144a1acb661fae33dc460 문장 1·3~4·14~19는 다른 업체의 다음 날 배송 일정 기능을 홍보한다. 즉시 차량 호출의 검색 성능·배정 원자성·요청 보존을 검증할 설계 근거가 없다. |
| 3 | doc-80a3aa3a1be847ddb396f9aa5123b8f1 | Fail | 관련성을 확인할 수 없는 업체 목록을 선택했다. | query-2 결과 1위의 지도 업체 페이지를 선택했다. URL https://www.mapquest.com/us/oklahoma/driver-dispatch-425362787 는 기술 문서가 아니며, doc-80a3aa3a1be847ddb396f9aa5123b8f1 문장 0~2는 접근 확인 화면뿐이다. |
| 4 | doc-606219b6c23b438bb951086db28cce90 | Fail | 후보 검증과 무관한 문서를 선택했다. | doc-606219b6c23b438bb951086db28cce90 문장 0~7은 지리공간 산업의 정책·규제 동향이다. 게시 단체는 식별되지만 차량 매칭의 검색·경합·위치 처리·호출 복구 방법과 연결되지 않는다. |
| 5 | doc-59e2059d3c104865bf24fc6e1dfd8cd9 | Fail | 동일 단어만 겹치는 무관한 문서를 선택했다. | doc-59e2059d3c104865bf24fc6e1dfd8cd9 문장 0~4·25~33은 고령 운전자의 페달 오조작 방지 장치와 지원 신청 안내다. 운전자 중복 배정이나 시스템 동시성 제어와 무관하다. |
| 6 | doc-d92cdd1b58df4a7da064a5c76dc508d1 | Fail | 기술 본문이 없는 목록·구독 안내를 선택했다. | doc-d92cdd1b58df4a7da064a5c76dc508d1 문장 1·4~7·12~14는 기술 블로그의 피드 생성과 구독 상품 안내다. 위치 이벤트 처리량이나 배압 설계의 본문 근거가 아니다. |
| 7 | doc-33e6c7ddc08241c4a3b085d17052c749 | Fail | 동일 내용의 중복 URL을 불필요하게 선택했다. | doc-33e6c7ddc08241c4a3b085d17052c749 문장 0~82가 doc-d4ec5d9dcf33493499c8686b74b77b4f와 동일하다. query-4 결과 2~3위의 지역 경로 차이만 있는 자료를 모두 수집할 추가 이유가 기록되지 않았다. |
| 8 | doc-8eb203a9f6154047b98b990a683de8fa | 판단 불가 | 출처 식별 기록이 부족하면 판단을 유보한다. | query-6 결과 3위의 https://www.youtube.com/watch?v=KujbNuRRJJY 제목은 분할·핫스폿과 관련되지만 게시 채널이 저장되지 않았다. doc-8eb203a9f6154047b98b990a683de8fa 문장 0~1도 플랫폼 하단 정보뿐이어서 게시 주체를 확인할 수 없다. |
| 9 | doc-3916bfcd663e46e4abed8a0fcac06389 | Fail | 후보 검증 근거가 없는 다른 서비스 홍보를 선택했다. | doc-3916bfcd663e46e4abed8a0fcac06389 문장 1~12는 배송 업체의 운전자 평가 점수 기능을 홍보한다. 점수의 서비스상 일관성은 배정 상태의 동시성 일관성과 다르며, 핵심 후보를 검증하지 못한다. |
| 10 | doc-8db30fecebd14906b5f2957f483fe8c2 | Fail | 설계 범위와 무관한 여행 페이지를 선택했다. | query-1 결과 5위는 박물관 여행 안내다. doc-8db30fecebd14906b5f2957f483fe8c2 문장 0~11도 여행지·관광지·맛집 추천이며, 차량 매칭 시스템의 품질 문제와 관련되지 않는다. |
| 11 | doc-db030eea5c404a42af033b05e59db723 | Fail | 검색 지연 검증과 무관한 사건 기사를 선택했다. | doc-db030eea5c404a42af033b05e59db723 문장 0~10은 승객 영상 방송과 운전자 이용 정지 사건이다. 배차 검색이나 요청 처리 지연을 다루지 않으며, 기사 매체 이름의 배차 관련 단어만 겹친다. |
| 12 | doc-43e51b0c07a84415abb403dafcd8ffa4 | Fail | 관련 설계 근거가 없는 일반 목록을 선택했다. | query-2 결과 6위의 패키지 공개일 목록을 선택했다. doc-43e51b0c07a84415abb403dafcd8ffa4 문장 0~1은 R 패키지 목록으로, 주변 운전자 검색 지연의 설계 방법이나 제약을 제공하지 않는다. |
| 13 | doc-1751f9bc802147e1ba246d91221f061d | Fail | 후보 검증과 무관한 운전자 정책 기사를 선택했다. | doc-1751f9bc802147e1ba246d91221f061d 문장 9~49는 운전자 계정 정지 사유다. 동시 호출의 중복 배정 방지나 트랜잭션 상태 전이를 검증할 자료가 아니다. |
| 14 | doc-d6f57c568c9d40baa43b2f818c609f6e | Fail | 무관하면서 실질적으로 중복된 문서를 선택했다. | doc-d6f57c568c9d40baa43b2f818c609f6e 문장 0~49는 운전자 계정 정지 정책이며, doc-1751f9bc802147e1ba246d91221f061d와 대부분 동일하다. 배정 경합 조사와 관련 없고 중복 수집 이유도 없다. |
| 15 | doc-6aedcff2283d4e4f95010d35ecd2cc3b | Fail | 다른 동작의 중복 방지 자료를 관련성 확인 없이 선택했다. | doc-6aedcff2283d4e4f95010d35ecd2cc3b 문장 5~10은 로그인 세션 수 제한 설정이다. 운전자 예약·수락의 원자적 배정과는 다른 문제이며, 후보에 적용할 동시성 보장을 설명하지 않는다. |
| 16 | doc-b00037a15a6845318727e24f436f8c9e | Fail | 기술 본문이 없는 상품 분류 페이지를 선택했다. | query-4 결과 4위의 운전자 상품 분류 페이지다. doc-b00037a15a6845318727e24f436f8c9e 문장 0~28은 공통 메뉴뿐이며, 위치 업데이트 처리량이나 배압 근거가 없다. |
| 17 | doc-b0cc15b68e554e34b99056f9bbf81f52 | Fail | 본문 근거가 없는 중복 지역 페이지를 선택했다. | doc-b0cc15b68e554e34b99056f9bbf81f52 문장 0~28은 doc-b00037a15a6845318727e24f436f8c9e와 같은 공통 메뉴다. 지역 경로만 다른 상품 분류 페이지를 추가로 선택할 후보 검증상의 이유가 없다. |
| 18 | doc-c57fb755d3b24c0fa8379eecde24f954 | Fail | 본문 근거가 없는 중복 지역 페이지를 선택했다. | doc-c57fb755d3b24c0fa8379eecde24f954 문장 0~28은 다른 운전자 상품 지역 페이지와 동일하다. 위치 이벤트 수집의 방법·제약을 제공하지 않는 중복 분류 페이지다. |
| 19 | doc-fb4bb9353acf48269309dad64a083739 | Fail | 기술 문서가 아닌 업체 디렉터리를 선택했다. | query-6 결과 6위의 https://www.mapquest.com/us/georgia/geospatial-engineering-consulting-llc-536993443 는 업체 지도 페이지다. doc-fb4bb9353acf48269309dad64a083739 문장 0~2도 접근 확인 화면이며 확장 설계 근거가 없다. |
| 20 | doc-7f36cd41adfd4e049e1615f4cfa80841 | Fail | 후보 검증과 무관한 숙박 목록을 선택했다. | doc-7f36cd41adfd4e049e1615f4cfa80841 문장 0~5·43~58은 호텔 검색과 숙소 추천이다. 차량 호출 접수·배정 및 위치 갱신의 시스템 품질을 조사하는 자료가 아니다. |
| 21 | doc-6155fd2885274e49af182492830a2d1c | Fail | 특정 관련 문서가 아닌 일반 저장소 첫 화면을 선택했다. | doc-6155fd2885274e49af182492830a2d1c 문장 0~21은 연구 저장소 소개와 최근 업로드 목록이다. 주변 운전자 검색 지연과 연결되는 논문이나 기술 문서를 특정하지 않았다. |
| 22 | doc-3ce8c8728c784943b7f664855efa1cc8 | Fail | 설계 문제와 무관한 기관 첫 화면을 선택했다. | doc-3ce8c8728c784943b7f664855efa1cc8 문장 0~29는 대학 모금·전공·학사 일정 안내다. 차량 매칭이나 검색 지연을 다루는 자료가 아니다. |
| 23 | doc-b6cc0f211eeb47bd9545d1519e2d2e6e | Fail | 설계 문제와 무관한 학사 안내를 선택했다. | doc-b6cc0f211eeb47bd9545d1519e2d2e6e 문장 0~22·23~45는 대학 교육과정과 학사 일정이다. query-2의 지리공간 검색 지연과 관련되지 않는다. |
| 24 | doc-dc99d12fc00b47ba890052b6740fe937 | Fail | 검색 단어만 겹치는 다른 분야의 홍보 기사를 선택했다. | doc-dc99d12fc00b47ba890052b6740fe937 문장 1~13은 탄약 제조 기술의 사업화다. 업체명에 동시성 관련 단어가 있어도 운전자 배정의 동시성 제어와는 무관하다. |
| 25 | doc-3c0efdf572bc4d01a4ae67f465cc4819 | Fail | 본문 근거가 없는 중복 지역 페이지를 선택했다. | doc-3c0efdf572bc4d01a4ae67f465cc4819 문장 0~28은 기존 운전자 상품 지역 페이지들과 같은 메뉴다. query-4에서 처리량 검증에 사용할 추가 내용 없이 중복 수집했다. |
| 26 | doc-9f91f4d2b47c4b3abafcc311d8e84e73 | Fail | 본문 근거가 없는 중복 지역 페이지를 선택했다. | doc-9f91f4d2b47c4b3abafcc311d8e84e73 문장 0~28은 동일 상품 분류 메뉴다. 다른 지역 경로와 구별되는 위치 처리 설계 근거가 없어 선택이 정당화되지 않는다. |
| 27 | doc-761e96099ac742a09fdc13316cfbf78f | Fail | 후보 검증과 무관한 조직 사건 기사를 선택했다. | doc-761e96099ac742a09fdc13316cfbf78f 문장 0~15는 직장 내 괴롭힘 의혹 조사와 인력 구성이다. 요청 보존·복구·재시도 방법과 관련되지 않는다. |
| 28 | doc-86397b40a3bd43a5bb30e3d716fff70f | Fail | 기술 조사와 무관한 주식 분석을 선택했다. | doc-86397b40a3bd43a5bb30e3d716fff70f 문장 20~31은 우버 주식의 실적·부채·투자 의견이다. 피크 호출의 보존이나 재처리 보장에 대한 근거가 없다. |
| 29 | doc-a334d6a0170747ceb9711dad98d354d4 | Fail | 기술적 부하 집중과 무관한 투자 기사를 선택했다. | doc-a334d6a0170747ceb9711dad98d354d4 문장 10~37은 투자 유망 종목과 주가 전망이다. 투자 관심 지역을 뜻하는 표현은 시스템 핫스폿·분할 문제와 관련되지 않는다. |
| 30 | doc-45d444007e224b0389dcad904bcf5224 | Fail | 후보 검증과 무관한 여행 안내를 선택했다. | doc-45d444007e224b0389dcad904bcf5224 문장 0~10·141~174는 관광 일정과 교통 이용 안내다. 호출 시스템의 검색·배정·위치 갱신 구조를 다루지 않는다. |
| 31 | doc-92f159da6e88474bad153a7782144ce9 | Fail | 설계 문제와 무관한 기관 첫 화면을 선택했다. | doc-92f159da6e88474bad153a7782144ce9 문장 0~14는 대학 생활·장학금·지역 안내다. 주변 운전자 검색 지연 후보와 연결되지 않는다. |
| 32 | doc-f3c56244a9b44550a61f29d2024d7ba4 | Fail | 후보 검증과 무관한 재무 분석을 선택했다. | doc-f3c56244a9b44550a61f29d2024d7ba4 문장 5~23·37~49는 실적과 투자 판단이다. 전체 운행 건수 언급만으로 호출 보존·재처리 방식이나 제약을 검증할 수 없다. |
| 33 | doc-b5031af4c990460e98aab6423c62c7b6 | Fail | 관련 기술 본문이 없는 일반 블로그 목록을 선택했다. | doc-b5031af4c990460e98aab6423c62c7b6 문장 0~85는 창업·마케팅·행사 게시물 목록이다. 위치 인덱스 확장과 지역별 부하 집중에 관련되는 특정 문서를 선택하지 않았다. |
| 34 | doc-38101cf01afc46acae81c4eba48e781b | Fail | 더 적절한 개별 기술 문서가 있는데 본문 없는 분류 페이지를 추가 선택했다. | query-3 재검색 결과 1~2위의 구체적 재설계 글과 달리, 3위 doc-38101cf01afc46acae81c4eba48e781b 문장 0~28은 공통 메뉴뿐이다. 일관성 검증용 본문이 없는 분류 페이지의 추가 선택 이유가 없다. |
| 35 | doc-90bf1b355f77403ea39d75f4dd5526cf | Fail | 관련 기술 문서 대신 기업 정보·뉴스 집계 페이지를 선택했다. | query-2 재검색 결과 3위의 제목과 URL은 기업 프로필이다. doc-90bf1b355f77403ea39d75f4dd5526cf 문장 1~10은 조직 정보와 뉴스 집계로, 같은 결과 1위의 배차 설계 글보다 후보 검증 출처가 불명확하다. |
| 36 | doc-29a8b144466849cb86e151e2d533e8d1 | 판단 불가 | 관련성은 보이나 게시 주체 확인 자료가 부족하다. | query-5 재검색 결과 1위의 https://www.youtube.com/watch?v=DY2AR8Wzg3Y 제목은 우버의 대규모 요청과 관련된다. 그러나 채널 정보가 없고 doc-29a8b144466849cb86e151e2d533e8d1 문장 0~1도 하단 정보여서 출처 식별 조건을 판단할 수 없다. |
| 37 | doc-b3f94afcc5d649f58c43d7526a5e765f | 판단 불가 | 관련성은 보이나 게시 주체 확인 자료가 부족하다. | query-5 재검색 결과 3위의 https://www.youtube.com/watch?v=7JQX79_6oZ4 제목은 분산 시스템 재시도와 관련된다. 게시 채널은 없고 doc-b3f94afcc5d649f58c43d7526a5e765f 문장 0~1만으로는 원 게시자를 확인할 수 없다. |
| 38 | doc-6bf5f58001ab4dc888d13df029e74631 | Fail | 후보 검증 근거가 부족한 다른 업체 소개를 선택했다. | doc-6bf5f58001ab4dc888d13df029e74631 문장 0~5는 배송 신생기업의 간단한 사업 소개다. 실시간 운전자 관리라는 표현만 있고 검색 지연이나 상태 제어의 방법·제약이 없다. |
| 39 | doc-2e5ea68069c4451e8077b9c37773d865 | Fail | 시스템 설계와 무관한 인력·비용 기사를 선택했다. | doc-2e5ea68069c4451e8077b9c37773d865 문장 1~8은 아마존 배송사의 배차 담당자 비용 삭감이다. 사람의 배차 업무와 고용 문제이지 주변 운전자 검색 지연의 기술 근거가 아니다. |
| 40 | doc-964bed68d8934ff7bf9471d4b8ad9be7 | Fail | 명시적으로 제외된 기능의 제품별 운영 문서를 선택했다. | doc-964bed68d8934ff7bf9471d4b8ad9be7 문장 1~6·19~27·40~46은 구독·청구 결제 재시도와 일 단위 일정이다. brief.scope에서 제외한 결제 기능이며 호출 보존·멱등 배정의 공통 설계 방법을 제공하지 않는다. |
| 41 | doc-0674f867864d436bb3d204d3a70b001b | Fail | 차량 매칭 후보와 연결되지 않는 프로토콜 발표를 선택했다. | doc-0674f867864d436bb3d204d3a70b001b 문장 0~16·25~31은 MCP 규격 변경이다. 무상태 처리와 재요청 용어가 있어도 호출 보존·차량 배정의 내결함성 검증과 연결할 근거가 기록되지 않았다. |
| 42 | doc-6d93b1caa77e4a3baaee78e0cc6961de | 판단 불가 | 관련성은 보이나 게시 주체 확인 자료가 부족하다. | query-6 재검색 결과 6위의 https://www.youtube.com/watch?v=R_wWbHqpQTg 제목은 우버 실시간 지도와 관련된다. 채널 정보가 없고 doc-6d93b1caa77e4a3baaee78e0cc6961de 문장 0~1은 플랫폼 하단 정보뿐이다. |
| 43 | doc-f6c24f1fab0441039c58ebde236c04f5 | Fail | 후보 검증 근거가 없는 다른 업종 홍보를 선택했다. | doc-f6c24f1fab0441039c58ebde236c04f5 문장 0~15는 항만 트럭 운전자의 강제 배차와 자율 선택 기능을 홍보한다. 차량 호출 시스템의 검색 지연·위치 처리·배정 경합 기법과 무관하다. |
| 44 | doc-81d97545b7354a46ab84016b2de28c29 | Fail | 설계 범위 밖의 다른 처리 문제를 선택했다. | doc-81d97545b7354a46ab84016b2de28c29 문장 5~20·104~110은 분기 사용자 수의 정확한 집계와 장기 역산 처리다. 위치 검색 인덱스나 실시간 차량 매칭 작업의 확장 문제와 다르다. |
| 45 | doc-5737ab19c8eb424fb35a6b56813da01d | Fail | 실시간 매칭 범위와 다른 분석 저장소 문제를 선택했다. | doc-5737ab19c8eb424fb35a6b56813da01d 문장 4~12·24~42는 Hadoop 분석 테이블의 파일 위치 인덱스와 대량 초기 적재를 다룬다. 운전자 공간 검색이나 배정 상태 분할과 연결할 선정 근거가 없다. |
| 46 | doc-1e515c782db544909be93fab7426b913 | Fail | 같은 용어를 쓰는 무관한 제품 발표를 선택했다. | doc-1e515c782db544909be93fab7426b913 문장 7~9·22~39는 건설 현장 인력 메시지 작성과 발송 기능이다. 차량 매칭의 배차 처리나 위치 인덱스 확장과 관련되지 않는다. |
| 47 | fetch:https://www.kkday.com/ko/product/33859-belgium-bruges-day-tour-from-amsterdam | Fail | 설계 범위와 무관한 상품 페이지를 선택했다. | query-1 결과 6위의 대상 URL은 브뤼헤 관광 상품이다. 검색 제목에서 차량 매칭 시스템이나 후보 검증과 관련되지 않음이 드러난다. 접근 차단으로 본문·문장 번호는 없다. |
| 48 | fetch:https://www.ilsos.gov/content/dam/departments/index/register/volume50/register_volume50_24.pdf | Fail | 관련성과 본문 존재를 확인하지 못한 문서를 선택했다. | query-2 결과 4위의 대상 URL은 검색 제목부터 문서 부재로 표시되며 주변 운전자 검색과 연결되는 설명도 없다. 이를 수집 대상으로 삼을 근거가 부족하다. 본문·문장 번호는 없다. |
| 49 | fetch:https://scalablehuman.com/2022/08/21/how-does-partitioning-work-when-requests-are-being-routed/feed | Fail | 기술 본문 대신 댓글 피드 URL을 불필요하게 선택했다. | query-6 결과 5위의 대상 URL과 검색 제목은 분할 글 자체가 아닌 댓글 피드다. 확장 방법의 실제 본문을 확보할 대상으로 부적절하며, 저장된 오류도 빈 본문이다. 문장 번호는 없다. |
| 50 | fetch:https://ca.indeed.com/q-documentation-manager-l-mississauga,-on-jobs.html | Fail | 설계 범위와 무관한 채용 목록을 선택했다. | query-1 결과 7위의 대상 URL은 문서 관리자 채용 목록이다. 호출 접수·주변 검색·배정과 연결되는 기술 자료가 아니다. 접근 차단으로 본문·문장 번호는 없다. |
| 51 | fetch:https://intl.its.go.kr/file/088fa543-4fe0-451c-bced-bf3b80ce8ce7_221027_2022%E1%84%82%E1%85%A7%E1%86%AB%20%E1%84%8C%E1%85%A628%E1%84%92%E1%85%AC%20LA%20ITS%20%E1%84%89%E1%85%A6%E1%84%80%E1%85%A8%E1%84%8E%E1%85%A9%E1%86%BC%E1%84%92%E1%85%AC%20%E1%84%80%E1%85%A7%E1%86%AF%E1%84%80%E1%85%AA%E1%84%87%E1%85%A9%E1%84%80%E1%85%A9%E1%84%89%E1%85%A5_V1.2(%E1%84%80%E1%85%B5%E1%84%8B%E1%85%A5%E1%86%B8%E1%84%87%E1%85%A2%E1%84%91%E1%85%A9%E1%84%8B%E1%85%AD%E1%86%BC).pdf | Fail | 후보 검증과의 연결을 확인하지 않은 일반 행사 보고서를 선택했다. | query-1 결과 8위의 대상 URL은 ITS 총회 결과보고서다. 저장된 검색 제목에는 차량 매칭의 구체적 품질 문제나 설계 방법과의 연결이 없다. 빈 본문 오류가 기록됐으며 문장 번호는 없다. |
| 52 | fetch:https://www.indeed.com/cmp/Uber-Drivers/reviews?fjobtitle=Driver&fcountry=US&floc=State+College%2C+PA&sort=helpfulness&ftext=driver | Fail | 후보 검증 근거가 부족한 근무 후기 목록을 선택했다. | query-3 결과 7위의 대상 URL은 특정 지역 운전자 근무 후기다. 같은 결과 1위의 배정 상태 설계 자료와 달리 중복 배정의 동시성 제어를 검토할 기술 근거가 없다. 본문·문장 번호는 없다. |
| 53 | fetch:https://kr.investing.com/news/stock-market-news/article-1588263 | Fail | 후보 검증과 무관한 시장 뉴스를 선택했다. | query-5 결과 7위의 대상 URL은 테슬라 로보택시 운행 허가 기사다. 호출 요청 보존·복구·멱등 재처리 방법과 관련되지 않는다. 접근 차단으로 본문·문장 번호는 없다. |
| 54 | fetch:https://ca.indeed.com/career-advice/career-development/horizontal-vs-vertical-scaling | Fail | 후보의 구체적 설계 문제를 검증하기 어려운 일반 소개를 선택했다. | query-6 결과 8위의 대상 URL은 수평·수직 확장의 정의 비교 안내다. 같은 결과의 구체적인 분할·핫스폿 자료와 달리 위치 인덱스나 매칭 작업의 제약을 검토할 선정 근거가 부족하다. 본문·문장 번호는 없다. |
| 55 | fetch:https://rocketreach.co/t-kartor-geospatial-ab-it-department_b4550bf4fc915885 | Fail | 기술 본문 없는 조직 디렉터리를 선택했다. | query-6 결과 9위의 대상 URL은 지리공간 업체의 IT 부서 정보다. 공간 인덱스 분할이나 지역별 부하 집중을 다루는 문서가 아니다. 접근 차단으로 본문·문장 번호는 없다. |
| 56 | fetch:https://www.instagram.com/reel/DWv9hpGKtVi | Fail | 관련성과 게시 주체를 확인하지 않은 대상을 선택했다. | query-2 재검색 결과 2위의 대상 URL은 플랫폼 이름만 제목으로 저장됐다. 게시자와 검색 지연 관련 내용이 확인되지 않은 상태에서 선택했고, 본문도 비어 있어 문장 번호가 없다. |
| 57 | fetch:https://www.instagram.com/reel/DaIYdx7zKeH | Fail | 관련성과 게시 주체를 확인하지 않은 대상을 선택했다. | query-4 재검색 결과 1위의 대상 URL은 플랫폼 이름 외에 작성자·주제 설명이 없다. 위치 갱신 처리량을 검증할 근거를 확인하지 않고 선택했다. 빈 본문 오류로 문장 번호도 없다. |

## 5-1 본문 수집의 유효성

### 당시 문서에 명시된 판정 기준

- Pass: 선택한 문서의 실제 본문을 정상적으로 수집하여 후속 근거 확인에 사용할 수 있다.
- Fail: 본문 대신 검색 요약이나 다른 문서 내용을 수집하고 정상적인 본문으로 처리한다.

판단 불가/실행 오류: 접근 차단·타임아웃 등으로 본문 수집에 실패한 경우는 별도로 기록한다.

### 모든 Fail과 판단 불가 원문

| 번호 | 평가 대상 | 판정 | 실제 적용한 기준 원문 | 판단 근거 원문 |
| --- | --- | --- | --- | --- |
| 1 | doc-80a3aa3a1be847ddb396f9aa5123b8f1 | 판단 불가 | 접근 차단은 실행 문제로 구분한다. | doc-80a3aa3a1be847ddb396f9aa5123b8f1 문장 0~2는 자바스크립트를 요구하는 로봇 확인 화면이다. https://www.mapquest.com/us/oklahoma/driver-dispatch-425362787 의 실제 본문은 확보되지 않았다. |
| 2 | doc-8eb203a9f6154047b98b990a683de8fa | Fail | 본문이 아닌 공통 하단 내용을 정상 수집 문서로 남겼다. | doc-8eb203a9f6154047b98b990a683de8fa 문장 0~1은 유튜브 사업자·상품 고지뿐이다. 영상 설명이나 자막은 없는데 정상 fetched 항목으로 저장돼 후속 기술 근거로 사용할 수 없다. |
| 3 | doc-8db30fecebd14906b5f2957f483fe8c2 | Fail | 선택한 기사 본문 대신 추천·탐색 메뉴를 수집했다. | doc-8db30fecebd14906b5f2957f483fe8c2 문장 0~11은 관련 여행·관광지·맛집·순위 목록뿐이다. 제목의 박물관 관람 안내 본문이 없지만 정상 fetched 문서로 남았다. |
| 4 | doc-b00037a15a6845318727e24f436f8c9e | Fail | 본문 대신 공통 탐색 메뉴만 수집했다. | doc-b00037a15a6845318727e24f436f8c9e 문장 0~28은 여러 우버 서비스의 공통 메뉴다. 운전자 상품 항목이나 관련 글 내용 없이 정상 fetched 문서로 저장됐다. |
| 5 | doc-b0cc15b68e554e34b99056f9bbf81f52 | Fail | 본문 대신 공통 탐색 메뉴만 수집했다. | doc-b0cc15b68e554e34b99056f9bbf81f52 문장 0~28은 공통 서비스 메뉴뿐이다. 선택한 분류의 실제 항목·기술 본문이 없는데 수집 성공 문서로 남았다. |
| 6 | doc-c57fb755d3b24c0fa8379eecde24f954 | Fail | 본문 대신 공통 탐색 메뉴만 수집했다. | doc-c57fb755d3b24c0fa8379eecde24f954 문장 0~28은 다른 지역 페이지와 동일한 메뉴다. 운전자 상품 내용이나 검토 가능한 본문이 확보되지 않았다. |
| 7 | doc-fb4bb9353acf48269309dad64a083739 | 판단 불가 | 접근 차단은 실행 문제로 구분한다. | doc-fb4bb9353acf48269309dad64a083739 문장 0~2는 로봇 확인과 자바스크립트 활성화 안내다. https://www.mapquest.com/us/georgia/geospatial-engineering-consulting-llc-536993443 의 실제 페이지 내용은 확보되지 않았다. |
| 8 | doc-3c0efdf572bc4d01a4ae67f465cc4819 | Fail | 본문 대신 공통 탐색 메뉴만 수집했다. | doc-3c0efdf572bc4d01a4ae67f465cc4819 문장 0~28은 공통 서비스 메뉴이며 운전자 상품 분류의 실제 항목이 없다. 이를 정상 fetched 문서로 저장했다. |
| 9 | doc-9f91f4d2b47c4b3abafcc311d8e84e73 | Fail | 본문 대신 공통 탐색 메뉴만 수집했다. | doc-9f91f4d2b47c4b3abafcc311d8e84e73 문장 0~28은 다른 지역 경로와 동일한 메뉴다. 해당 분류의 실제 내용이나 기술 본문이 없다. |
| 10 | doc-38101cf01afc46acae81c4eba48e781b | Fail | 본문 대신 공통 탐색 메뉴만 수집했다. | doc-38101cf01afc46acae81c4eba48e781b 문장 0~28은 공통 서비스 메뉴다. 기술 블로그 글 목록이나 개별 기술 본문 없이 정상 fetched 문서로 남았다. |
| 11 | doc-7c0755306e854adbac07f21ce28f580e | Fail | 본문이 아닌 플랫폼 공통 하단 내용을 정상 문서로 저장했다. | doc-7c0755306e854adbac07f21ce28f580e 문장 0~1은 유튜브 사업자·상품 고지다. 배차 강의의 설명·자막이 전혀 없어 후속 근거 확인용 본문이 아니다. |
| 12 | doc-29a8b144466849cb86e151e2d533e8d1 | Fail | 본문이 아닌 플랫폼 공통 하단 내용을 정상 문서로 저장했다. | doc-29a8b144466849cb86e151e2d533e8d1 문장 0~1은 유튜브의 사업자·상품 고지뿐이다. 제목의 대규모 요청 처리 설명이나 자막이 없어 기술 근거로 사용할 수 없다. |
| 13 | doc-b3f94afcc5d649f58c43d7526a5e765f | Fail | 본문이 아닌 플랫폼 공통 하단 내용을 정상 문서로 저장했다. | doc-b3f94afcc5d649f58c43d7526a5e765f 문장 0~1은 유튜브 공통 고지다. 재시도 지연이나 복원력 강의의 본문·자막이 없다. |
| 14 | doc-6d93b1caa77e4a3baaee78e0cc6961de | Fail | 본문이 아닌 플랫폼 공통 하단 내용을 정상 문서로 저장했다. | doc-6d93b1caa77e4a3baaee78e0cc6961de 문장 0~1은 유튜브의 사업자·상품 고지다. 실시간 지도 영상의 설명이나 자막이 없어 후속 근거 확인용 본문이 아니다. |
| 15 | fetch:https://medium.com/@paulbuzakov/idempotency-in-a-payment-pipeline-retry-the-request-is-architecture-not-a-retry-policy-0130bbf1ade3 | 판단 불가 | 접근 차단에 의한 수집 실패는 실행 오류로 구분한다. | 대상 URL의 fetch_failures에 HTTP 403 오류가 기록됐다. 실제 본문과 문장 번호가 없으므로 수집 유효성을 판정할 수 없으며, 이를 품질 실패로 점수화하지 않는다. |
| 16 | fetch:https://www.kkday.com/ko/product/33859-belgium-bruges-day-tour-from-amsterdam | 판단 불가 | 접근 차단에 의한 수집 실패는 실행 오류로 구분한다. | 대상 URL의 fetch_failures에 HTTP 403 오류가 기록됐다. 본문과 문장 번호가 없으며, 무관한 대상 선정 문제와 수집 실행 오류는 별개다. |
| 17 | fetch:https://www.ilsos.gov/content/dam/departments/index/register/volume50/register_volume50_24.pdf | 판단 불가 | 접근 차단에 의한 수집 실패는 실행 오류로 구분한다. | 대상 URL의 fetch_failures에 HTTP 403 오류가 있다. PDF 본문이나 문장 번호는 확보되지 않았고 다른 내용을 정상 본문으로 처리했다는 기록도 없다. |
| 18 | fetch:https://scalablehuman.com/2022/08/21/how-does-partitioning-work-when-requests-are-being-routed/feed | 판단 불가 | 빈 본문으로 명시된 수집 실패는 실행 문제로 구분한다. | 대상 URL의 fetch_failures는 본문이 비어 있다고 명시한다. 정상 문서로 대체 저장하지 않았으며, 확인할 본문과 문장 번호가 없다. |
| 19 | fetch:https://ca.indeed.com/q-documentation-manager-l-mississauga,-on-jobs.html | 판단 불가 | 접근 차단에 의한 수집 실패는 실행 오류로 구분한다. | 대상 URL의 fetch_failures에 HTTP 403 오류가 있다. 본문과 문장 번호가 없어 수집 내용의 유효성을 평가할 수 없다. 채용 목록 선정의 부적합과는 별개다. |
| 20 | fetch:https://intl.its.go.kr/file/088fa543-4fe0-451c-bced-bf3b80ce8ce7_221027_2022%E1%84%82%E1%85%A7%E1%86%AB%20%E1%84%8C%E1%85%A628%E1%84%92%E1%85%AC%20LA%20ITS%20%E1%84%89%E1%85%A6%E1%84%80%E1%85%A8%E1%84%8E%E1%85%A9%E1%86%BC%E1%84%92%E1%85%AC%20%E1%84%80%E1%85%A7%E1%86%AF%E1%84%80%E1%85%AA%E1%84%87%E1%85%A9%E1%84%80%E1%85%A9%E1%84%89%E1%85%A5_V1.2(%E1%84%80%E1%85%B5%E1%84%8B%E1%85%A5%E1%86%B8%E1%84%87%E1%85%A2%E1%84%91%E1%85%A9%E1%84%8B%E1%85%AD%E1%86%BC).pdf | 판단 불가 | 빈 본문으로 명시된 수집 실패는 실행 문제로 구분한다. | 대상 URL의 fetch_failures에 빈 본문 오류가 기록됐다. PDF 텍스트와 문장 번호가 없으며 실패를 정상 본문으로 처리하지 않았다. |
| 21 | fetch:https://www.indeed.com/cmp/Uber-Drivers/reviews?fjobtitle=Driver&fcountry=US&floc=State+College%2C+PA&sort=helpfulness&ftext=driver | 판단 불가 | 접근 차단에 의한 수집 실패는 실행 오류로 구분한다. | 대상 URL의 fetch_failures에 HTTP 403 오류가 있다. 운전자 후기 본문과 문장 번호는 확보되지 않아 수집 유효성을 판단할 수 없다. |
| 22 | fetch:https://kr.investing.com/news/stock-market-news/article-1588263 | 판단 불가 | 접근 차단에 의한 수집 실패는 실행 오류로 구분한다. | 대상 URL의 fetch_failures에 HTTP 403 오류가 기록됐다. 기사 본문·문장 번호가 없으며, 대상 선정의 무관성과 접근 실패를 분리한다. |
| 23 | fetch:https://ca.indeed.com/career-advice/career-development/horizontal-vs-vertical-scaling | 판단 불가 | 접근 차단에 의한 수집 실패는 실행 오류로 구분한다. | 대상 URL의 fetch_failures에 HTTP 403 오류가 있다. 실제 설명 본문과 문장 번호가 없어 본문 수집의 유효성을 판정할 수 없다. |
| 24 | fetch:https://rocketreach.co/t-kartor-geospatial-ab-it-department_b4550bf4fc915885 | 판단 불가 | 접근 차단에 의한 수집 실패는 실행 오류로 구분한다. | 대상 URL의 fetch_failures에 HTTP 403 오류가 기록됐다. 페이지 본문과 문장 번호가 없으며 다른 내용을 정상 본문으로 처리한 기록도 없다. |
| 25 | fetch:https://medium.com/codetodeploy/uber-architecture-part-5-the-dispatch-engine-and-map-rendering-64ac669fa698 | 판단 불가 | 접근 차단에 의한 수집 실패는 실행 오류로 구분한다. | 대상 URL의 fetch_failures에 HTTP 403 오류가 있다. 관련성 있는 제목을 찾았더라도 실제 배차 설계 본문과 문장 번호는 확보되지 않았다. |
| 26 | fetch:https://www.instagram.com/reel/DWv9hpGKtVi | 판단 불가 | 빈 본문으로 명시된 수집 실패는 실행 문제로 구분한다. | 대상 URL의 fetch_failures에 본문이 비어 있다고 기록됐다. 영상 내용·설명·문장 번호가 없으며 정상 본문을 수집했다고 처리하지 않았다. |
| 27 | fetch:https://www.instagram.com/reel/DaIYdx7zKeH | 판단 불가 | 빈 본문으로 명시된 수집 실패는 실행 문제로 구분한다. | 대상 URL의 fetch_failures에 빈 본문 오류가 있다. 위치 스트리밍 관련 내용을 확인할 실제 본문·문장 번호는 없으므로 판단을 유보한다. |
| 28 | fetch:https://medium.com/@YodgorbekKomilo/how-uber-streams-millions-of-live-locations-without-lag-20cc1838f596 | 판단 불가 | 접근 차단에 의한 수집 실패는 실행 오류로 구분한다. | 대상 URL의 fetch_failures에 HTTP 403 오류가 기록됐다. 위치 스트리밍의 실제 본문과 문장 번호가 없어 제목 이상의 근거로 사용할 수 없다. |
| 29 | fetch:https://medium.com/@mohanmmohadikar/partitioning-and-sharding-in-mongodb-a-senior-engineers-perspective-3fb7985047c7 | 판단 불가 | 접근 차단에 의한 수집 실패는 실행 오류로 구분한다. | 대상 URL의 fetch_failures에 HTTP 403 오류가 있다. 분할 방법의 본문·문장 번호는 확보되지 않았으므로 수집 유효성은 판단 불가다. |
