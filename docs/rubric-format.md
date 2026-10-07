# 루브릭 출력 형식 (확정)

> 스키마 → 하네스 체크 → 렌더 템플릿이 전부 여기서 파생된다.
> `plan.md`의 F0.1 / F4.x / F5.x는 이 문서를 따른다.

## 결정 요약

| 항목 | 결정 | 근거 |
|---|---|---|
| 출력 형식 | 요약표 + criterion 상세. **출처 표시(인용·근거 표)는 넣지 않는다** | 채점표는 면접관이 쓰는 문서다. 근거는 `evidence_refs`로 데이터에 남고 하네스(`EVIDENCE_REF_*`)가 검사한다. 사람이 출처를 검토할 기록은 M7 finalize에서 별도 파일로 검토 |
| NFR의 위치 | 전체 루브릭의 **한 섹션** | README `rubric.sections[]` 구조 |
| NFR 내부 배점 합 | **100 고정** | 채점식이 `Σw`로 나누므로 섹션 내부 합은 자유 → 읽기 쉬운 값으로 고정 |
| 역량 축 | **criterion마다 부착** | README에 이미 있는 설계. 지금 넣어야 4섹션 합칠 때 스키마를 다시 안 연다 |
| criterion 개수 | **3개 기본 / 2~4개 허용** | 면접에서 NFR에 쓸 수 있는 시간이 10~15분 |
| criterion:NFR | **1:1** | 점수 하나로 두 NFR을 판정하면 채점이 갈린다. `competency_axis`도 criterion당 하나뿐 |
| descriptor 길이 | **15~200자** | 하한은 "미고려" 같은 무의미한 서술을, 상한은 한 레벨이 두 가지를 평가하는 걸 막는다 |
| md 작성 주체 | **Jinja2** (LLM 아님) | README 설계 원칙 1 |

---

## 1. 스키마

LLM이 만드는 것은 `NFRExport`뿐이다. 근거 문서 목록(`Document[]`)은 파이프라인
상태이지 LLM 출력이 아니다 — **LLM이 출처를 지어내지 못하게 하려는 의도적 분리.**
하네스(`core.cross-ref`)가 이 목록으로 `evidence_refs`를 검사한다.
렌더러는 `(NFRExport, InterviewBrief)`를 받는다 — md에 출처를 쓰지 않으므로 문서 목록이 필요 없다.

```yaml
NFRExport:
  confirmed_nfrs:
    - id: string            # NFR-1
      kind: string          # latency | throughput | scalability |
                            # availability | fault_tolerance | consistency | ...
      statement: string     # 이번 주제에서 요구되는 NFR 문장
      rationale: string     # 왜 중요한지
      target:               # 정량 목표. 없으면 null
        value: number | null
        unit: string | null
        condition: string | null   # p99, peak traffic
      qualitative_target: string | null   # 수치가 없을 때만
      evidence_refs: [string]             # Document.id 목록

  tradeoffs:
    - id: string
      related_nfr_ids: [string]
      description: string
      evidence_refs: [string]

  rubric:
    criteria:
      - id: string          # NFR-C1
        title: string
        description: string
        related_nfr_ids: [string]       # 정확히 1개
        weight: integer                 # 자연수 1~100, 섹션 내부 합 = 100
        competency_axis: CompetencyAxis # ← 이번에 추가
        levels:
          - score: 0..3
            descriptor: string          # 15~200자

CompetencyAxis:
  - TRADE_OFF
  - DATA_MANAGEMENT
  - FAILURE_RECOVERY
  - HIGH_TRAFFIC
  - COMPUTER_SCIENCE
```

### 채점 모델

**상위 점수는 하위 점수의 요건을 모두 포함한다.** 3점은 2점 요건을 충족한 상태에서
추가 조건까지 만족한 답변에만 준다. descriptor마다 반복해 쓰지 않고 **렌더된 문서
머리말에 한 번 명시**한다 — descriptor 길이를 먹지 않으면서 채점자가 보게 하려는 것.

```
criterion_pct = level / 3
section_pct   = Σ(w × criterion_pct) / Σw          # NFR 섹션 점수
axis_pct(a)   = Σ(w × criterion_pct) / Σw          # axis == a 인 criterion만
total         = Σ(section.weight × section_pct)    # section weight 합 = 100
```

축 롤업은 섹션 점수와 **같은 계산 한 번**에서 나온다 (필터만 다름).

---

## 2. 출력 샘플

주제: 실시간 채팅 시스템 / 대상: 미들

````markdown
# 실시간 채팅 시스템

**대상 연차** 미들\
**배점** 100

## NFR

> **채점 규칙**: 상위 점수는 하위 점수의 요건을 포함한다. 2점 설계 없이 3점 조건만
> 만족한 답변은 3점이 아니다.

| # | 평가 항목 | 역량 축 | 배점 | 획득 |
|---|---|---|---|---|
| NFR-C1 | 메시지 전달 지연 | HIGH_TRAFFIC | 30 | ☐0 ☐1 ☐2 ☐3 |
| NFR-C2 | 메시지 순서 보장 | DATA_MANAGEMENT | 25 | ☐0 ☐1 ☐2 ☐3 |
| NFR-C3 | 장애 시 가용성 | FAILURE_RECOVERY | 25 | ☐0 ☐1 ☐2 ☐3 |
| NFR-C4 | 동시 접속 확장성 | HIGH_TRAFFIC | 20 | ☐0 ☐1 ☐2 ☐3 |

---

### NFR-C1. 메시지 전달 지연 · 30점 · `HIGH_TRAFFIC`

**평가 항목**
메시지 전송부터 수신자 화면 도달까지의 지연을 요구 수준 내로 설계했는가

**요구 수준**
`latency` — p99 500 ms
메시지는 전송 후 p99 500ms 이내에 수신자에게 도달해야 한다.

**관련 trade-off**
- 순서 보장을 강하게 걸수록 전달 지연이 증가한다.

| Level | 기준 |
|---|---|
| 0 | latency 요구사항을 설계에서 고려하지 않는다. |
| 1 | 낮은 지연이 필요하다고 언급하지만 이를 만족시킬 구조를 제시하지 못한다. |
| 2 | 지속 연결(WebSocket) 등 p99 500ms를 만족할 수 있는 전송 구조를 제시한다. |
| 3 | 요구 지연을 만족하면서 대규모 방의 팬아웃 병목, 재연결 시 tail latency, 순서 보장과의 trade-off까지 설명한다. |

---

### NFR-C2. 메시지 순서 보장 · 25점 · `DATA_MANAGEMENT`

... (동일 구조 반복)
````

### 렌더 규칙

- 헤딩 단계: `# 주제` → `## NFR` → `### NFR-C{n}` (criterion)
- 주제 바로 아래에 **대상 연차**와 **배점**(criterion weight 합, 고정 문구 아님)을 한 줄씩
- 4섹션을 합칠 때는 `# 주제`와 대상 연차를 합치는 쪽에서 한 번만 내고,
  각 섹션은 `## NFR`부터 끼워 넣는다
- `## NFR` 바로 아래에 **누적 채점 규칙**을 한 줄 넣는다 (템플릿 고정 문구)
- **요구 수준**: 정량 목표면 `` `kind` — 목표`` 다음 줄에 statement,
  정성 목표면 `` `kind` — statement`` 한 줄 (정성 목표는 statement의 요약이라 반복하지 않는다)
- 목표 수치는 천 단위 콤마, 지수 표기 없음, 숫자와 단위는 띄우되 `%`만 붙인다
  (`p99 500 ms`, `peak 10,000 msg/s`, `99.9%`)
- 레벨표는 데이터 순서와 상관없이 score 0 → 3 순으로 쓴다
- 역량 축 열·헤딩 표기(`HIGH_TRAFFIC` 등)는 `core.axis` 구현 후. 현재 렌더에는 없다
- criterion id는 `NFR-C{n}` — 섹션 prefix로 다른 섹션과 충돌 방지
- **출처 표시(`[D1]` 인용, 근거 표)는 넣지 않는다.** 문서 id(`D{n}`)는 데이터와 하네스 안에서만 쓴다
- descriptor 안의 `|`는 `\|`로 이스케이프
- trade-off가 없는 criterion은 해당 블록 자체를 생략 (빈 섹션을 남기지 않는다)

---

## 3. 이 형식에서 파생되는 하네스 체크

### Pre-Render (M4)

| check | 코드 | 이 형식 때문에 생긴 것 |
|---|---|---|
| `core.weight-sum` | `WEIGHT_OUT_OF_RANGE` / `WEIGHT_SUM_INVALID` | 합 == **100**, 각 weight 1~100 자연수로 확정. 누락·소수는 스키마가 거부 |
| `core.levels` | `LEVEL_MISSING` / `LEVEL_DUPLICATED` / `LEVEL_DESCRIPTOR_MISSING` / `LEVEL_DESCRIPTOR_DUPLICATED` / **`LEVEL_DESCRIPTOR_TOO_SHORT`** / **`LEVEL_DESCRIPTOR_TOO_LONG`** | ← 15~200자. 길이 검사 2개는 2순위·미구현 |
| `core.nfr-measurable` | `NFR_KIND_MISSING` / `NFR_VALUE_NOT_FOUND` / `NFR_UNIT_MISSING` / `NFR_COMPARATOR_MISSING` / `NFR_GUARANTEE_UNCLEAR` | 2순위·미구현 |
| `core.cross-ref` | **`ID_DUPLICATED`** / `NFR_REFERENCE_INVALID` / `NFR_NOT_COVERED` / **`NFR_MULTI_COVERED`** / `CRITERION_NFR_REFERENCE_MISSING` / **`CRITERION_MULTI_NFR`** / **`TRADEOFF_NFR_REFERENCE_MISSING`** / **`EVIDENCE_REF_MISSING`** / **`EVIDENCE_REF_UNKNOWN`** | ← 인용이 실존 Document를 가리키는가. NFR은 정확히 한 criterion에서 평가 |
| **`core.criteria-count`** | **`CRITERIA_COUNT_OUT_OF_RANGE`** | ← criterion 2~4개 |
| **`core.axis`** | **`AXIS_MISSING`** / **`AXIS_INVALID`** | ← 역량 축 신설. 2순위·미구현 |

### Post-Render (M2)

렌더된 md를 되읽어(`render/post_render.py`의 `read_back`) 원본 `NFRExport`·`InterviewBrief`와 값 단위로 비교한다.
`check_rendered(md, export, brief)`.
렌더러가 일부러 바꾸는 것(표 칸 이스케이프, 헤딩 공백 접기, 목표 수치 표기, 레벨 정렬)은
되돌리거나 같은 규칙을 적용한 뒤 비교한다.

| md 부분 | 검사 | 코드 | path |
|---|---|---|---|
| 머리말 | 주제(공백 접기)·대상 연차가 brief와, 배점이 weight 합과 같고, `## NFR` 헤딩·채점 규칙이 있음 | `RENDER_HEADER_MISMATCH` | `header` |
| 요약표 | 행들이 원본 criterion들의 `[id, title, 배점]`과 같음 | `RENDER_SUMMARY_MISMATCH` | `rubric.criteria` |
| criterion 섹션들 | `### id.` 섹션 id 목록이 원본 criterion id 목록과 같음 (누락·중복·순서) | `RENDER_SECTIONS_MISMATCH` | `rubric.criteria` |
| 헤딩 | title(공백 접기 적용)·배점이 원본과 같음 | `RENDER_HEADING_MISMATCH` | `rubric.criteria[i].title` / `.weight` |
| 평가 항목 | 본문이 `description`과 같음 | `RENDER_DESCRIPTION_MISMATCH` | `rubric.criteria[i].description` |
| 요구 수준 | `` `kind` — 목표/statement``와 같음 | `RENDER_REQUIREMENT_MISMATCH` | `confirmed_nfrs[k]` |
| 관련 trade-off | bullet 목록이 그 NFR의 trade-off 설명들과 같음(개수·순서·내용) | `RENDER_TRADEOFF_MISMATCH` | `rubric.criteria[i].tradeoffs` |
| 레벨표 | 행들이 원본 레벨(score 순)의 `(score, 서술)` 목록과 같음. 행 수 차이도 여기 | `RENDER_LEVELS_MISMATCH` | `rubric.criteria[i].levels` |

code 하나가 md의 한 부분을 가리킨다 — 이름만 보고 고칠 템플릿 블록을 안다.
레벨이 4개인지는 하네스 `core.levels`가 보장하므로, Post-Render는 옮기면서 달라졌는지만 본다.

Post-Render Finding은 렌더러 코드 버그라 repair 루프를 돌리지 않는다 (M7에서 즉시 실패).

### Judge (M6) — 형식과 무관하게 의미만

`WEIGHT_IMBALANCED`는 축이 생기면서 판단 근거가 하나 늘었다 —
한 축에 배점이 과도하게 몰려 있으면 지적 대상.

---

## 4. 열린 항목

- 축 배정의 타당성(`HIGH_TRAFFIC`인가 `TRADE_OFF`인가)은 규칙으로 못 잡는다
  → Judge에 `AXIS_MISASSIGNED`를 둘지 M6 구현 시 판단
- descriptor 15~200자. 첫 골든셋(Pro)의 score 3이 228~248자였고 이를 줄이려고 잡은 값이다.
  Day 9 실측에서 `LEVEL_DESCRIPTOR_TOO_LONG` 발생률을 보고 조정
- 200자 descriptor 4개가 든 레벨표의 가독성은 Day 3에 골든셋을 실제로 렌더해보고 판단한다.
  읽기 힘들면 표를 레벨별 목록으로 바꾼다
