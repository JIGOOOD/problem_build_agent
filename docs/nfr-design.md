# NFR 설계

# **목표**

- 사용자가 입력한 시스템 디자인 주제에서 중요한 비기능적 요구사항을 조사한다.
- 실제 기술 문서를 근거로 NFR Rubric 생성한 후 Harness 검증을 거쳐 Markdown으로 출력한다.

## 전체 흐름

```
TUI 입력
  ↓
1. Research Agent - NFR 후보 생성, search / requery / fetch / keep으로 근거 수집·선별
  ↓ ResearchResult (topic_summary, nfr_candidates, Document[])
2. Export (NFR Agent) - NFR 최종 확정 및 평가 기준 생성
  ↓ NFRExport
3. Make MD - 생성된 NFR이 올바른지 검증하고 문서로 변환
  ↓
nfr_rubric.md
```

# Research

**목표**

- 해당 주제에서 어떤 NFR이 중요한지 탐색한다.
- 이를 검증할 기술 자료를 직접 검색하고, 본문에서 NFR 판단에 필요한 문장 원문을 수집한다.

**필요성**

- 주제에 따라 요구되는 NFR에는 차이가 있다.
- Rubric의 신뢰도를 위해, 신뢰할 수 있는 자료 기반으로 NFR 정의해야 한다.

## NFR Catalog

**목표**

- 시스템 디자인 면접에서 반복적으로 중요하게 다뤄지는 핵심 NFR을 참고 목록으로 제공한다.
- 후보를 고르는 메뉴가 아니라, 주제에서 도출한 NFR을 해석하고 이름을 통일하는 기준으로 사용한다.
- 주제 특성상 Catalog에 없는 NFR이 더 중요할 수 있으므로, Catalog 밖의 후보도 허용한다.

**필요성**

- 주제에 따라 검색 결과에서 NFR이 명확히 드러나지 않을 수 있다. 이 경우 사전에 정의된 핵심 NFR을 활용해 관련 자료를 추가로 탐색할 수 있다.
- 반대로 검색을 통해 너무 많은 NFR이 발견될 수도 있다. 주제마다 서로 다른 NFR을 모두 Rubric에 반영하면 평가 항목이 과도하게 분산되고 문제별 평가 기준의 일관성이 낮아질 수 있다.
- 따라서 NFR Catalog는 검색을 대체하는 정답 목록이 아니라, 검색이 부족할 때 탐색을 보완하고 검색 결과가 과도할 때 평가 범위를 제한하는 기준으로 사용한다.

**구조**

```
CORE NFR CATALOG

1. PERFORMANCE
   - latency
   - throughput

2. SCALABILITY
   - scalability

3. RELIABILITY
   - availability
   - fault_tolerance

4. DATA_GUARANTEES
   - consistency
```

**선정 기준**

- 실제 시스템 디자인 문제 30종을 분석해 반복적으로 등장하는지 파악한다.
- 여러 도메인에 공통적으로 적용되는지 파악한다.
- 해당 요구사항에 따라 아키텍처 선택이 실제로 달라지는지 파악한다.

| NFR | 등장 문제 수 | 비율 |
| --- | --- | --- |
| **Scalability / Scale** | 29 / 30 | 약 97% |
| **Latency / Timeliness** | 27 / 30 | 약 90% |
| **Consistency** | 22 / 30 | 약 73% |
| **Reliability / Fault Tolerance / Recovery** | 21 / 30 | 약 70% |
| **Availability** | 15 / 30 | 약 50% |
| **Throughput** | **12 / 30** | **약 40%** |
| **Freshness** | 8 / 30 | 약 27% |
| **Durability** | 5 / 30 | 약 17% |

### NFR Catalog Entry

**필요성**

- LLM이 각 NFR의 의미와 적용 맥락을 이해해, 주제에 맞는 NFR을 고르고 검색 방향을 잡도록 한다.

```yaml
name: latency

category: PERFORMANCE

meaning:
  요청부터 응답까지 걸리는 시간

important_when:
  - 사용자가 응답을 기다리는 기능
  - 검색, 조회, 피드 같은 interactive request

examples:
  - p95 < 500ms
  - p99 < 2s

common_tradeoffs:
  - against: throughput
    reason: >-
      여러 요청을 모아 한 번에 처리하면 자원 효율은 오르지만,
      모으는 동안 기다려야 해서 개별 요청의 응답이 늦어진다.
  - against: consistency
    reason: >-
      최신 값을 보장하려고 여러 복제본의 확인을 기다리면
      네트워크 왕복이 늘어 응답이 느려진다.
```

> `common_tradeoffs`는 이 NFR을 달성할 때 발생하는 **대표적인 설계 trade-off 대상**이다.
> Catalog의 NFR로 한정되지 않으며, `cost`처럼 NFR이 아닌 항목도 들어간다.
> 따라서 로더는 `with` 값을 Catalog 항목명으로 검증하지 않는다.
>
> **자주 나타나는** 상충이지 항상 발생하는 관계가 아니다.
> `reason`은 어떤 메커니즘 때문에 상충이 생기는지를 적어 Agent가 문서를 해석할 때
> 참고하게 하려는 것이며, 근거 없이 그대로 옮겨 적으라는 뜻이 아니다.

## Source Policy

**목표**

- NFR을 정의할 때 신뢰할 수 있는 기술 자료를 우선적으로 활용하도록 문서 선택 기준을 정한다.
- 출처 우선순위(tier)는 코드가 매기지 않고 Research Agent가 문서를 판정할 때 적용한다.

**필요성**

- 검색 결과에는 공식 문서부터 개인 블로그까지 다양한 품질의 자료가 함께 노출된다.
- 출처 기준 없이 자료를 사용하면 부정확하거나 근거가 약한 정보가 NFR과 Rubric에 반영될 수 있다.

```
1순위
- 공식 Engineering / Technical Blog
- 공식 Technical Documentation

2순위
- 논문
- 기술 Conference 발표

3순위
- 신뢰할 수 있는 제3자 기술 블로그
- 시스템 디자인 면접 자료
```

## Research Agent (tool calling)

Research Agent는 기존 Research Planner, Search API, Crawling 세 단계를 대체한다.
하나의 에이전트가 `search`, `requery`, `fetch`, `keep`을 호출하며, 가져온 문서를 읽고
근거가 부족한 쿼리만 다시 검색한다. 출력 `ResearchResult`의 `nfr_candidates`와
`Document[]`는 Export 단계의 NFR Agent 입력으로 그대로 사용한다.

### 상수

| 이름 | 값 | 비고 |
| --- | --- | --- |
| `CANDIDATES_MIN`, `CANDIDATES_MAX` | 3, 5 | 기존 `domain/research.py` 값 재사용. 최초 후보 생성에 적용 |
| `MAX_QUERIES` | 6 | 기존 값 재사용. 주제용 1 + 후보당 1. 재생성은 기존 쿼리를 대체 |
| `RESULTS_PER_QUERY` | 10 | search가 쿼리당 돌려주는 URL 수 |
| `FETCH_BATCH` | 3 | 쿼리별로 한 번에 fetch하는 URL 수 |
| `SUFFICIENT_DOCS` | 2 | NFR 쿼리 확정에 필요한 쓸만한 문서 수 |
| `SUFFICIENT_DOCS_TOPIC` | 1 | 주제 쿼리 확정에 필요한 문서 수 |
| `MAX_REQUERY` | 1 | 쿼리 하나당 재생성 횟수 |
| `MAX_CONTENT_CHARS` | 12000 | 문장으로 나누기 전 원문 상한. 판정 전 LLM 입력량을 제한한다. HTML 본문 추출에서 메뉴·푸터를 먼저 제외한다. 실험 후 조정 |
| `MAX_KEEP_CHARS` | 2000 | 문서별 누적 선택 본문 한도. 문장 사이 구분 문자 포함 |
| `MAX_AGENT_STEPS` | 20 | LLM 호출 상한. 병렬 호출로 보통 3~4번, 많아도 10번 안팎을 예상하며 무한 루프를 방지한다 |

### 처리 흐름

1. LLM이 주제를 분석해 `topic_summary`와 NFR 후보 `CANDIDATES_MIN`~`CANDIDATES_MAX`개를 만든다.
2. LLM이 쿼리를 만든다. 주제용 1개 + 후보당 1개, 합계 `MAX_QUERIES` 이하.
   각 쿼리는 `related_nfr`을 가지며 주제용은 `null`이다.
3. 쿼리마다 아래를 반복한다.
   1. `search(query_id)`로 URL 최대 `RESULTS_PER_QUERY`개를 받는다.
   2. 아직 안 본 URL 중 순위가 높은 것부터 `FETCH_BATCH`개를 `fetch`한다.
   3. LLM이 가져온 문서마다 쓸만한지 판정하고, 쓸만한 문서는 `keep`으로 남길 문장 번호를 기록한다.
      `keep`하지 않은 문서는 버린다.
   4. `keep`한 문서가 기준 수(`SUFFICIENT_DOCS`, 주제 쿼리는 `SUFFICIENT_DOCS_TOPIC`) 이상이면
      그 쿼리를 확정한다.
   5. 부족하고 안 본 URL이 남아 있으면 다음 순위 URL을 fetch한다.
   6. URL을 다 봤는데 부족하고 재생성 횟수가 `MAX_REQUERY` 미만이면,
      그 쿼리만 새로 만들어 search부터 다시 한다. 재생성 전후에 keep한 문서 수는 누적한다.
   7. 재생성까지 했는데 부족하면 그 후보는 출력에서 빼고 시스템 로그에 남긴다.
4. 모든 쿼리가 끝나면 `ResearchResult`를 출력한다.

위 반복은 쿼리별 상태 전이를 설명한다. 실제 도구 호출은 아래 규칙에 따라 같은 단계의 쿼리를
모아 병렬로 실행한다. 코드는 쿼리별 URL 목록·확인 여부·keep한 문서·재생성 횟수를 추적한다.
`query_id`는 코드가 관리하는 쿼리 식별자이며, 재생성 전후를 같은 후보 쿼리로 연결한다.

최초 후보 생성에는 3~5개 제약을 적용하지만, 근거가 부족한 후보를 제외한 최종
`ResearchResult.nfr_candidates`에는 최소 3개를 강제하지 않는다. 수를 맞추려고 근거 없는
후보를 채우지 않는다.

### 도구 호출 묶기 (프롬프트에 넣음)

같은 단계의 도구 호출은 한 응답에서 병렬로 묶어서 호출한다. LLM 호출 횟수를 줄이기 위해서다.

- 첫 search: 모든 쿼리를 한 번에 호출한다.
- fetch: 필요한 쿼리의 `query_id`를 각각 전달해 함께 호출한다. 코드가 쿼리별 미확인 URL을 순위대로 `FETCH_BATCH`개씩 가져온다.
- keep: 이번에 판정한 문서를 한 번에 호출한다.
- 추가 fetch, 쿼리 재생성 search도 해당되는 쿼리를 모아 한 번에 호출한다.

### LLM과 코드의 역할

| 일 | 담당 |
| --- | --- |
| 후보 생성, 쿼리 생성, 쿼리 재생성 | LLM |
| 문서가 쓸만한지 판정, 남길 문장 선택, 쿼리 확정 판단 | LLM |
| 검색 호출, 중복 URL 제거, 순위 정렬 | 코드 (search) |
| 본문 가져오기, 문서 저장과 id 부여, 재시도 | 코드 (fetch) |
| 선택한 문장 원문으로 content 조립, 대화 기록 축소 | 코드 (keep 및 배치 판정 완료 처리) |
| 쿼리별 URL 목록과 확인 여부, keep한 문서 수 추적 | 코드 |
| 상수 한도 강제 (`MAX_QUERIES`, `RESULTS_PER_QUERY`, `FETCH_BATCH`, `MAX_CONTENT_CHARS`, `MAX_REQUERY`, `MAX_AGENT_STEPS`) | 코드 |

### 판정 기준 (프롬프트에 넣음)

- 쓸만한 문서: 해당 NFR(주제 쿼리는 주제 자체)을 설계 관점에서 다루는 문서.
  수치, 요구 수준, 설계 선택 중 하나 이상이 있다.
- 버리는 문서: 광고성 글, 주제와 무관한 글, NFR 언급 없이 기능 소개만 있는 글,
  본문을 못 가져온 문서.
- 같은 조건이면 Source Policy 1순위 > 2순위 > 3순위 문서를 먼저 고른다.

남길 문장을 고르는 기준은 해당 후보보다 넓게 잡는다.
NFR Agent는 검색하지 않고 이 문장만 읽고 판단하기 때문이다.

- 해당 후보 NFR을 다루는 문장
- 다른 NFR을 다루는 문장 (NFR Agent가 놓친 NFR을 찾는 데 사용)
- 수치, 단위, percentile 같은 목표 수준이 있는 문장
- 설계 선택이나 trade-off를 설명하는 문장

### 쿼리 재생성 규칙 (프롬프트에 넣음)

- 재생성 대상은 부족한 쿼리 하나뿐이다. 다른 쿼리는 건드리지 않는다.
- 이전 쿼리와 같은 표현을 쓰지 않는다. 동의어, 영어, 관점 변경을 사용한다.
  예: "응답 시간" → "API latency SLA".
- 해당 NFR의 Catalog 항목(`meaning`, `important_when`)을 참고한다.

### 프롬프트 입력

- `topic` (`InterviewBrief.topic`): 후보와 쿼리의 기준. 모든 쿼리에 주제 맥락을 넣는다.
- `seniority` (`InterviewBrief.seniority`): Research에서는 쓰지 않는다. NFR Agent로 넘긴다.
- `notes` (`InterviewBrief.notes`, 있을 때만): 후보로 우선 검토하되 다른 후보와 똑같이 검증한다.
- NFR Catalog: 후보를 고르는 메뉴가 아니라 kind 이름을 통일하는 기준.
  대응 항목이 있으면 그 kind를 쓰고, Catalog 밖 후보는 전체의 절반 이하로 제한한다.
  Research 입력에는 `name`, `meaning`, `important_when`만 전달한다.
  `examples`, `common_tradeoffs`는 NFR Agent가 사용하는 전체 Catalog에 유지한다.
- Source Policy: 문서 선택 우선순위.
  쿼리 생성 시에도 공식 기술 문서와 공식 Engineering / Technical Blog를 우선 찾도록
  `official documentation`, `engineering blog` 같은 검색 표현을 주제와 NFR에 맞게 넣는다.
  출처 검색 표현을 넣어도 주제 맥락과 해당 NFR을 유지한다.

검색 전 구체적 수치를 확정하거나 확인되지 않은 사실을 단정하지 않는다.
Catalog 항목을 기계적으로 모두 선택하지 않는다.
초기 계획 프롬프트에는 `InitialResearchPlan`의 JSON Schema도 포함한다.
응답은 코드 블록 없는 JSON 객체 하나이며, 주제 쿼리의 `related_nfr: null`을 포함한
모든 필수 필드를 명시하도록 지시한다. 응답 검증과 1회 재시도는 코드가 수행한다.

### 도구

#### search(query_id: str) -> list[SearchResult] | str

- LLM은 `query_id`만 전달한다. 코드는 해당 ID의 계획 검색어를 사용하며, 없는 ID는 오류 문자열을 반환한다. 검색어 문자열 비교는 하지 않는다.

- Tavily로 검색한다. 차단 도메인은 구현하지 않는다.
- 이번 실행에서 이미 나온 URL은 제거한다.
- Tavily가 돌려준 순서(`score` 순)를 유지한 채 최대 `RESULTS_PER_QUERY`개를 반환한다.
  `rank`는 중복 제거 후 반환 순위이며 1부터 시작한다.
- Source Policy tier는 코드가 매기지 않고, LLM이 문서를 판정할 때 판단한다.
- 실패하면 예외 대신 오류 문자열을 반환한다. 코드는 이 쿼리를 "URL 소진"으로 처리한다.
  다른 쿼리는 계속 진행하며, 실패한 쿼리에도 남은 재생성 기회를 적용한다.

```yaml
SearchResult:
  query_id: string
  url: string
  title: string
  rank: integer        # 반환 순위, 1부터
```

#### requery(query_id: str, new_query: str, reason: str) -> list[SearchResult] | str

- 초기 검색을 마치고 미확인 URL을 모두 확인했으며 keep 문서 수가 기준 미달인 쿼리만 허용한다.
- 쿼리당 최대 `MAX_REQUERY`회다. 같은 검색어(대소문자·공백만 바뀐 경우 포함)는 거부한다.
- 같은 `query_id`의 검색어와 검색 결과를 교체하고 검색한다. 기존 keep 문서와 확인한 URL은 유지한다.
- 검색 실패도 재검색 기회를 사용한 것으로 처리한다. 실패는 다른 쿼리 진행을 막지 않는다.
- `query_id`, `old_query`, `new_query`, `reason`을 경고 로그의 필드로 남긴다.
- LLM에는 매 회차 쿼리별 재검색 횟수를 전달한다. 기준 미달 후보는 최종 결과에서 제외하고 문서 수·제외 사유를 로그에 남긴다.

#### fetch(query_id: str) -> list[FetchBatchItem] | str

- LLM은 `query_id`만 전달한다. 코드가 해당 쿼리의 순위가 높은 미확인 URL 3개를 선택한다. 남은 URL이 1~2개면 남은 것만 가져온다.
- URL별 성공·실패와 무관하게 선택한 URL 모두 확인한 것으로 처리한다. 다음 호출은 다음 순위부터 진행한다.
- 같은 응답에 같은 쿼리를 여러 번 호출해도 배치는 최대 3개다. 없는 쿼리나 가져올 URL이 없으면 오류 문자열을 반환한다.
- 쿼리 간 및 배치 내 URL 요청은 병렬로 실행하고 결과는 검색 순위대로 반환한다.
- 배치 항목은 `{url, rank, result}`이며 `result`는 `FetchResult` 또는 오류 문자열이다. 성공한 각 문서를 개별 keep 판정한다.
- 실제 HTTP·본문 추출은 내부 `FetchTool.fetch(url)`이 담당하며 아래 동작을 유지한다.

- HTTP로 HTML을 가져오고, 본문 추출에서 메뉴·푸터와 댓글을 제외한다.
- 정리한 본문에 `MAX_CONTENT_CHARS` 상한을 적용한다. 초과분은 버리고 URL·원문 길이·상한을 로그에 남긴다.
- 빈 줄로 나눈 본문을 문장부호 경계에서 문장으로 분리하고 0부터 연속 번호를 붙인다. 소수점과 흔한 약어는 경계에서 제외한다. 긴 문장을 임의로 잘라 나누지 않는다.
- 상한을 적용한 본문 문자열을 `documents` 저장소에 보관하고 `doc_id`를 부여한다. 요약하지 않는다.
  이 저장소에는 판정 전 문서도 있으며, 최종 출력에는 keep한 문서만 포함한다.
- LLM에게는 번호가 붙은 문장 목록을 반환한다.
- 이미 가져온 URL이면 저장된 결과를 반환한다.
- 본문이 비어 있으면 문서로 저장하지 않고 오류 문자열을 반환한다.
- timeout, 연결 오류, HTTP 429·5xx처럼 일시적인 요청 실패만 같은 URL로 1회 재시도한다. 429를 제외한 HTTP 4xx, 본문 추출 오류, 빈 본문은 재시도하지 않는다. 실패하면 오류 문자열을 반환하고 LLM은 다음 URL로 넘어간다.

```yaml
FetchResult:
  doc_id: string
  url: string
  title: string
  sentences:
    - index: integer
      text: string
```

#### keep(doc_id: str, sentence_indices: list[int]) -> dict | str

- LLM은 추가할 문장 번호를 중요도순으로 전달한다. 이번 배치의 판정이 끝날 때까지 keep하지 않은 문서는 버린 것으로 본다.
- 재호출은 기존 선택을 유지하고 새 문장을 누적한다. 기존 번호는 다시 보낼 필요가 없으며 중복 번호는 한 번만 반영한다.
- 문서당 `MAX_KEEP_CHARS = 2000`자 한도를 적용하며 문장 사이 구분 문자(`\n\n`)도 포함한다. 기존 선택을 우선 보존하고 남은 예산에서 새 문장을 전달 순서대로 선택한다. 넘치는 문장은 통째로 건너뛰고 다음 문장을 확인한다.
- 코드는 누적 선택한 문장을 원문 순서대로 연결해 `content`에 저장한다. 추가 문장이 모두 제외되어도 기존 선택을 지우지 않는다. 재호출로 쿼리의 보존 문서 수가 늘어나지 않는다.
- fetch 대화 기록도 누적 선택한 문장만 남도록 갱신한다. 판정이 끝난 배치에서 keep하지 않은 문서는 "버림"으로 줄인다.
- 없는 문서 ID, 빈 목록, 정수가 아니거나 범위 밖인 문장 번호는 오류 문자열을 반환하고 기존 상태를 바꾸지 않는다.
- 반환: `selected_indices`(누적 선택, 원문 순서), `skipped_indices`(이번 호출에서 예산 초과로 제외), `content_chars`(누적 본문 길이), `kept_documents`(해당 쿼리의 보존 문서 수).

### 출력

```yaml
ResearchResult:
  topic_summary: string

  nfr_candidates:
    - kind: string
      reason: string
      doc_ids: [string]          # LLM은 id만 고른다

  documents:                     # 코드가 만든다. LLM이 다시 쓰지 않는다
    - id: string
      url: string
      title: string
      content: string            # 고른 문장 원문을 순서대로 이어 붙인 것 (코드)
```

- `documents`에는 keep한 문서만 들어간다. 버린 문서는 넣지 않는다.
- 후보의 `doc_ids`는 그 후보 쿼리(재생성 쿼리 포함)에서 keep한 문서 id다.
- 주제 쿼리에서 keep한 문서는 `documents`에만 넣고 어느 후보에도 연결하지 않는다.
- `documents`를 LLM 출력으로 받지 않는 이유: Pre-Render `core.cross-ref`가
  `evidence_refs`를 실제 크롤한 Document ID로 검사하기 때문이다.
- NFR Agent는 후보별 `doc_ids`를 근거 탐색의 출발점으로 삼되, 전달된 모든 문서를 읽고
  추가 NFR과 trade-off를 확인한다. `doc_ids`가 있다고 NFR을 최종 확정한 것은 아니다.

### 후보 응답 정리와 재시도

기존 Planner의 후보 응답 정리 규칙을 유지한다.

후보·쿼리 중복 정리 후, 후보에 없는 `related_nfr`은 검색어 순서대로 후보에 추가한다.
reason은 `계획 검색어에서 추가된 후보: {query}`로 채운다. 이미 후보가 `CANDIDATES_MAX`개이면
그 kind는 추가하지 않고 해당 쿼리를 제거한다. 추가·제거는 경고 로그에 남기며,
후보 개수·후보별 쿼리 수·전체 쿼리 수 검사는 이 보완 처리 후 수행한다.
재시도 후에도 검증에 실패하면 `ResearchPlanError`를 발생시키기 전에 1차·2차 LLM 응답 원문을 오류 로그에 남긴다.
초기 생성의 후보 개수 제약과 근거 검증 후의 후보 제외는 구분한다.

| 응답 | 처리 |
| --- | --- |
| kind 표기 흔들림 (`Fault Tolerance`, `fault-tolerance`, `fault__tolerance_`) | 소문자, 공백·하이픈·밑줄 덩어리 → 밑줄 하나, 앞뒤 밑줄 제거 |
| 겹친 후보 kind | 먼저 나온 것만 남김. 최초 생성에서는 걸러낸 뒤 3~5개 밖이면 재시도 |
| 빈 값, 깨진 JSON, 최초 생성의 후보 수 위반, 정리해도 snake_case가 아닌 kind | 위치와 이유를 알려주고 1회 재시도. 다시 위반하면 실패 사유를 기록 |

이 재시도는 후보 응답 형식의 오류를 고치는 것이며, 근거가 부족한 쿼리를 바꾸는
`MAX_REQUERY`와 별개다. 재시도 LLM 호출도 `MAX_AGENT_STEPS`에 포함한다.
두 응답 모두 실패하면 1·2차 검증 사유를 함께 남긴다.
LLM 호출 자체의 예외(네트워크 등)와 문자열이 아닌 응답(연결부 버그)은
후보 응답 형식의 재시도 대상으로 취급하지 않는다.

### 시스템 로그

쿼리 재생성 기록은 `ResearchResult`에 넣지 않고 logger 또는 LangSmith trace에 남긴다.

- `query_id`
- `old_query`
- `new_query`
- `reason`

재생성 후에도 문서 수가 부족해 제외한 후보와 제외 사유도 시스템 로그에 남긴다.

### 구현 전에 확정할 경계 동작

- 실행 전체의 URL 중복 제거로 여러 후보에 관련된 문서가 후속 쿼리에서 빠질 때,
  기존 문서를 후속 쿼리에 연결하거나 문서 수에 포함할지.
- 주제 쿼리가 재생성 후에도 기준 문서 수를 채우지 못했을 때의 종료 처리.
- `MAX_AGENT_STEPS`에 도달했을 때, 미완료 쿼리를 제외한 부분 결과를 반환할지 실패할지.
- 확정: 잘못된 keep 입력은 오류 문자열을 반환하고 상태를 유지한다. 재호출은 2,000자 한도에서 기존 선택에 새 문장을 누적하며 문서 수를 중복 집계하지 않는다.

# Export

## Golden Exapmle

**목표**

- 크롤링한 문서에서 어떤 정보를 핵심 NFR로 선택해야 하는지 기준을 제공한다.
- 선택한 NFR을 0~3 단계의 평가 기준으로 어떻게 변환해야 하는지 예시를 제공한다.

**필요성**

- 스키마만으로는 어떤 NFR을 선택해야 하는지와 각 점수 단계의 깊이를 일관되게 만들기 어렵다.
- 잘 만든 예시를 제공해 NFR 선정 기준과 0~3 점수 간 수준 차이를 안정화한다.

```yaml
Criterion:
  id: NFR-C1
  title: 검색 응답 지연시간
  description: 검색 요청이 요구되는 latency 수준을 만족하도록 설계했는가

  weight: 40

  related_nfr_ids:
    - NFR-1

  levels:
    - score: 0
      descriptor: latency 요구사항을 고려하지 않는다.

    - score: 1
      descriptor: 낮은 latency가 필요하다고 인식하지만 설계에 구체적으로 반영하지 못한다.

    - score: 2
      descriptor: 요구되는 latency를 만족할 수 있는 설계를 제시한다.

    - score: 3
      descriptor: 요구 latency를 만족하면서 병목과 tail latency, 관련 trade-off까지 고려한다.
```

## NFR Agent

```yaml
NFR Agent

목적
- Research Agent가 만든 NFR 후보를 실제 Document로 검증한다.
- Research Agent가 놓친 NFR도 추가로 발견한다.
- 해당 NFR과 관련된 Trade-off도 발견한다.
- 최종 NFR을 확정하고 0~3 Rubric Criterion으로 변환한다.

1. NFR 후보군 구성

입력
- ResearchResult.topic_summary
- ResearchResult.nfr_candidates
  - kind
  - reason
  - doc_ids
- ResearchResult.documents (Document[])
- target_level (InterviewBrief.seniority)

처리
- Research Agent가 선택한 NFR과 reason을 Document와 대조한다.
- reason을 뒷받침하는 내용이 실제 문서에 있는지 의미적으로 확인한다.
- 전달된 Document 전체에서도 추가적인 NFR 관련 내용을 탐색한다. NFR Agent는 직접 검색하지 않는다.
- Research Agent 후보에 없던 중요한 NFR이 발견되면 신규 후보로 추가한다.

후보가 하나도 없는 경우
- Core NFR Catalog를 참고해 Document를 다시 확인한다. Catalog 항목을 정답으로 넣지 않는다.
- 그래도 근거가 없다면 억지로 NFR을 생성하지 않는다.
- candidate_not_found

2. 핵심 NFR 선정

각 후보에 대해 다음을 확인한다.

- subject의 핵심 기능과 직접 관련 있는가
- 실제 문서 근거가 존재하는가
- 해당 NFR의 요구 수준이 달라지면 주요 설계 선택이 달라지는가

판단
- 조건을 충분히 만족하면 최종 NFR로 확정한다.
- 단순히 문서에서 한 번 언급됐다는 이유만으로 선정하지 않는다.
- 근거가 약하면 제외하거나 보류한다.

3. NFR 목표 수준 결정

처리
- Document에 수치, 단위, percentile, consistency 수준 등이 명시되어 있으면 그대로 추출한다.
- 여러 문서에 비슷한 수치가 있으면 공통 범위로 정리할 수 있다.
- 수치 없이 `low latency`, `high availability`처럼 정성적 표현만 있으면 정성적 요구사항으로 유지한다.

수치가 없는 경우
- LLM이 임의의 숫자를 생성하지 않는다.
- value_not_found

4. Trade-off 확인

처리
- Research Agent가 남긴 문장에서 핵심 trade-off의 근거를 찾는다.
- 후보의 doc_ids에 연결되지 않은 문서도 포함해, 전달된 Document 전체에서 trade-off를 확인한다.
- 단순히 Catalog에 common_tradeoffs가 있다는 이유만으로 추가하지 않는다.

근거가 없는 경우
- 해당 trade-off를 최종 결과에 포함하지 않는다.

5. Rubric Criterion 생성

입력
- 최종 확정 NFR
- 관련 evidence
- trade-off
- target_level
- Golden Examples

처리
- NFR마다 평가 Criterion을 생성한다.
- Golden Example을 참고해 0~3 단계의 수준 차이를 만든다.
- target_level이 높을수록 높은 점수에서 요구하는 설계 깊이를 높인다.

기본 의미
0
- NFR을 고려하지 못함

1
- NFR을 인식했지만 설계 반영이 부족함

2
- NFR을 만족하는 설계를 제시함

3
- NFR을 만족하고 병목, 예외 상황, trade-off까지 설명함

최종 출력
- confirmed_nfrs
- 각 NFR의 rationale
- target 또는 qualitative target
- evidence_refs
- tradeoffs
- rubric criteria
- level 0~3 descriptors
```

### 출력 스키마

```yaml
NFRExport:

  confirmed_nfrs:
    # 문서 근거를 통해 최종적으로 확정된 NFR 목록

    - id: string
      # NFR 고유 ID

      kind: string
      # NFR 종류
      # 예: latency, scalability, availability, consistency

      statement: string
      # 이번 주제에서 실제 요구되는 NFR 문장
      # 예: "검색 응답은 낮은 tail latency를 유지해야 한다."

      rationale: string
      # 왜 이 NFR이 중요한지에 대한 설명
      # Research Agent 후보의 reason + Document 근거를 바탕으로 정리

      target:
        # 문서에 구체적인 목표 수준이 있는 경우 저장
        # 없으면 null

        value: number | null
        # 수치
        # 예: 2

        unit: string | null
        # 단위
        # 예: second, %, requests/sec

        condition: string | null
        # 측정 조건
        # 예: p99, peak traffic

      qualitative_target: string | null
      # 수치가 없고 정성적인 수준만 확인된 경우 사용
      # 예: "low latency", "high availability"

      evidence_refs:
        - string
      # 이 NFR을 뒷받침하는 Document ID 목록

  tradeoffs:
    # 확정된 NFR과 관련된 핵심 trade-off

    - id: string

      related_nfr_ids:
        - string
      # 어떤 NFR과 관련된 trade-off인지 연결

      description: string
      # 어떤 선택 사이에 충돌이 있는지 설명
      # 예: "강한 consistency를 높이면 latency가 증가할 수 있다."

      evidence_refs:
        - string
      # 해당 trade-off의 근거 문서

  rubric:
    # 확정된 NFR을 실제 평가 기준으로 변환한 결과

    criteria:
      - id: string
        # Criterion 고유 ID

        title: string
        # 평가 항목 이름

        description: string
        # 무엇을 평가하는 Criterion인지 설명

        related_nfr_ids:
          - string
        # 어떤 NFR을 평가하는지 연결

        weight: integer
        # 해당 Criterion의 중요도. 1~100 자연수

        levels:
          - score: 0
            descriptor: string
            # NFR을 고려하지 못한 수준

          - score: 1
            descriptor: string
            # NFR을 인식했지만 설계 반영이 부족한 수준

          - score: 2
            descriptor: string
            # NFR 요구사항을 만족하는 설계를 제시한 수준

          - score: 3
            descriptor: string
            # 병목, 예외 상황, trade-off까지 고려한 수준
```

# Make

**목표 채점 모델**: criterion 마다 0–3 레벨. 가중 합산 후 100점 정규화한다.

```
criterion_pct = level / 3
section_pct   = Σ(w × criterion_pct) / Σw
total         = Σ(section.weight × section_pct)      # section weight 합 = 100
```

## Pre-Render

### core.weight-sum

**목표**

- 각 Criterion의 weight가 범위 안이고 합이 100인지 검사한다.
- weight 누락과 자연수가 아닌 값(소수, bool)은 스키마가 파싱 단계에서 거부하므로 여기서 보지 않는다.

**검사**

- 1 ≤ weight ≤ 100인지 확인한다. 0점 criterion은 면접 시간만 쓰고 점수에 반영되지 않는다.
    - WEIGHT_OUT_OF_RANGE
- sum(weight) == 100인지 확인한다.
    - WEIGHT_SUM_INVALID

### core.criteria-count

**목표**

- Criterion 개수가 면접에서 다룰 수 있는 범위인지 검사한다.
  NFR에 쓰는 10~15분 안에 제대로 다룰 수 있는 건 3개가 기본이다.

**검사**

- Criterion이 2~4개인지 확인한다.
    - CRITERIA_COUNT_OUT_OF_RANGE

### core.levels

**목표**

- 각 Criterion이 0~3 단계로 채점 가능한지 검사한다.

**검사**

- score 0, 1, 2, 3이 모두 존재하는지 확인한다.
    - LEVEL_MISSING
- score 중복이 없는지 확인한다.
    - LEVEL_DUPLICATED
- descriptor에 중복이나 누락이 없는지 확인한다.
    - LEVEL_DESCRIPTOR_DUPLICATED
    - LEVEL_DESCRIPTOR_MISSING

### core.nfr-measurable

**목표**

- NFR이 실제로 평가 가능한 형태인지 검사한다.

**검사**

- NFR 종류가 명확한지 확인한다.
    - NFR_KIND_MISSING
- 정량형 NFR은 숫자, 단위, 비교 기준이 있는지 확인한다.
    - NFR_VALUE_NOT_FOUND
    - NFR_UNIT_MISSING
    - NFR_COMPARATOR_MISSING
- 보장형 NFR은 consistency 수준이나 장애 허용 조건처럼 명확한 기준이 있는지 확인한다.
    - NFR_GUARANTEE_UNCLEAR

### core.cross-ref

**목표**

- 확정된 NFR과 Rubric Criterion의 연결이 정상인지 검사한다.
- 인용(evidence_refs)이 실제로 크롤한 Document를 가리키는지 검사한다.
  Document 목록은 코드가 조립한 `ResearchResult.documents`이며 LLM 출력이 아니다.
  실행마다 keep한 문서의 id 목록으로 검사를 만든다.

**검사**

- NFR, trade-off, Criterion 각각의 안에서 id가 겹치지 않는지 확인한다.
    - ID_DUPLICATED
- Criterion과 trade-off가 존재하는 NFR ID만 참조하는지 확인한다.
    - NFR_REFERENCE_INVALID
- trade-off가 최소 하나의 NFR에 연결되어 있는지 확인한다.
    - TRADEOFF_NFR_REFERENCE_MISSING
- Criterion이 정확히 하나의 NFR과 연결되어 있는지 확인한다.
    - CRITERION_NFR_REFERENCE_MISSING (0개)
    - CRITERION_MULTI_NFR (2개 이상)
- 모든 확정 NFR이 정확히 하나의 Criterion에서 평가되는지 확인한다.
    - NFR_NOT_COVERED (0개)
    - NFR_MULTI_COVERED (2개 이상)
- NFR과 trade-off에 근거 문서가 있는지 확인한다.
    - EVIDENCE_REF_MISSING
- NFR과 trade-off의 evidence_refs가 ResearchResult.documents의 Document ID만 가리키는지 확인한다.
  fetch했어도 버린 문서는 인용할 수 없다.
    - EVIDENCE_REF_UNKNOWN

### 실패

- NFR Agent를 재실행한다.
- 최대 2회 정도 실행한다.

## Render

**목표**

- Jinja2로 렌더링해 섹션 순서·헤딩 레벨·표 구조를 코드로 고정한다.
- 템플릿: `src/archgen/render/templates/nfr_rubric.md.j2`
- 출력 형식과 렌더 규칙: `docs/rubric-format.md`의 출력 샘플·렌더 규칙

```
# {주제}
**대상 연차** / **배점**(weight 합)

## NFR
> 채점 규칙
| # | 평가 항목 | 배점 | 획득 |          ← criterion마다 한 행

### {criterion.id}. {criterion.title} · {weight}점   ← criterion마다 반복
**평가 항목**   criterion.description
**요구 수준**   `kind` — 목표 + statement (정성 목표면 statement만)
**관련 trade-off**   그 NFR에 연결된 trade-off (없으면 블록 생략)
| Level | 기준 |   score 0~3
```

## Post-Render

**목표**

- 최종 Markdown이 NFRExport 내용을 빠짐없이, 그대로 반영했는지 확인한다.
- 렌더된 md를 되읽어 원본과 값 단위로 비교한다. 검사 목록은 `docs/rubric-format.md`의 Post-Render 표.

**실패**

- Finding을 생성한다. 렌더러 코드 버그라 NFR Agent를 재실행해도 고쳐지지 않으므로 repair하지 않는다.

## LLM Judge
