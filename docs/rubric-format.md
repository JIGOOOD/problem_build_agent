# 루브릭 출력 형식 (확정)

> 스키마 → 하네스 체크 → 렌더 템플릿이 전부 여기서 파생된다.
> `plan.md`의 F0.1 / F4.x / F5.x는 이 문서를 따른다.

## 결정 요약

| 항목 | 결정 | 근거 |
|---|---|---|
| 출력 형식 | 요약표 + criterion 상세. **출처 표시(인용·근거 표)는 넣지 않는다** | 채점표는 면접관이 쓰는 문서다. 근거는 `evidence_refs`로 데이터에 남고 하네스(`EVIDENCE_REF_*`)가 검사한다. 사람이 출처를 검토할 기록은 M7 finalize에서 별도 파일로 검토 |
| NFR의 위치 | 전체 루브릭의 **한 섹션** | README `rubric.sections[]` 구조 |
| NFR 내부 배점 합 | **100 고정** | 채점식이 `Σw`로 나누므로 섹션 내부 합은 자유 → 읽기 쉬운 값으로 고정 |
| 역량 축 | **사용하지 않는다** | 스키마·요약표·항목 헤딩에 추가하지 않는다 |
| criterion 개수 | **3개 기본 / 2~4개 허용** | 면접에서 NFR에 쓸 수 있는 시간이 10~15분 |
| criterion:NFR | **1:1** | 점수 하나로 두 NFR을 판정하면 채점이 갈린다. |
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
  scope: [string]           # 확정 요구·미확정 범위·조건부 가정. 이전 산출물은 []
  excluded_nfrs: [string]   # 실제 검토 후 제외한 후보 이름과 이유. 이전 산출물은 []
  confirmed_nfrs:
    - id: string            # NFR-1
      kind: string          # latency | throughput | scalability |
                            # availability | fault_tolerance | consistency | ...
      statement: string     # 이번 주제에서 요구되는 NFR 문장
      rationale: string     # 주제·근거·설계 영향과 다른 후보 대비 선정 이유
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
      - id: string          # C1
        title: string
        description: string
        related_nfr_ids: [string]       # 정확히 1개
        weight: integer                 # 자연수 1~100, 섹션 내부 합 = 100
        levels:
          - score: 0..3
            descriptor: string          # 15~200자

```

### 채점 모델

점수 0~3의 의미와 연차별 난이도는 `resources/seniority-criteria.md`를 단일 기준으로 사용한다.
생성·재생성·Judge에 MD 전체를 전달하고, 대상 연차인 Middle 또는 Senior의 기준을 적용한다.
시스템 프롬프트에 별도의 점수별 의미나 공통 심화 요건을 중복 정의하지 않는다.
각 항목의 score 0~3은 한 번씩 있어야 하며, 이 형식은 스키마와 하네스가 검증한다.
항목 획득 배점은 `항목 배점 × 레벨 / 3`으로 환산한다. 채점표 머리말에는 설명 문구를 추가하지 않는다.
항목별 반올림 없이 합산한 뒤 총점을 소수 둘째 자리까지 표시한다.
같은 설계 선택이 여러 NFR에 기여해도 각 항목은 서로 다른 결과 속성을 평가한다.

`scope`는 brief에 명시된 요구와 미확정 기능·규모를 구분한다. 문서 사례는 추가 요구가 아니다.
조건부 가정은 그 가정을 택하지 않은 합리적인 설계의 감점 사유가 될 수 없다.
구현 대신 관찰할 결과와 보장 수준을 평가한다. 특정 기술·구현·상태 관리 위치를 강제하지 않고 요구 수준을 동등하게 충족하는 대안을 인정한다.
trade-off는 문서 근거가 있는 실제 NFR 간 충돌과 발생 조건을 설명한다.
적용 범위·선정·제외 이유는 JSON의 `scope`·`rationale`·`excluded_nfrs`에 보존한다. 채점에 필요한 조건부 적용 범위는 해당 항목의 `description`에 명시한다.

```
criterion_pct = level / 3
section_pct   = Σ(w × criterion_pct) / Σw          # NFR 섹션 점수
total         = Σ(section.weight × section_pct)    # section weight 합 = 100
```


---

## 2. 출력 샘플

전체 배치 기준은 `resources/golden/uber.md`를 따른다. 아래는 구조 예시다.

````markdown
# 차량 공유 서비스

**대상 연차** Middle\
**배점** 100

## NFR

| NFR | 평가 항목 | 배점 | 획득 |
|---|---|---|---|
| NFR-1 · Low Latency | C1. 주변 운전자 검색 최적화 | 30 | ☐0 ☐1 ☐2 ☐3 |
| NFR-2 · Consistency | C2. 운전자 중복 배정 방지 | 35 | ☐0 ☐1 ☐2 ☐3 |
| NFR-3 · High Throughput | C3. 대규모 위치 업데이트 처리 | 15 | ☐0 ☐1 ☐2 ☐3 |
| NFR-3 · High Throughput | C4. 피크 시간대 호출 요청 유실 방지 | 20 | ☐0 ☐1 ☐2 ☐3 |

---

## NFR-1. Low Latency

**요구 수준**
`latency` — 매칭 지연을 요구 수준 내로 유지한다.

### C1. 주변 운전자 검색 최적화 · 30

**평가 항목**
위치 갱신과 근접 검색을 효율적으로 처리하는가?

| Level | 기준 |
|---|---|
| 0 | 요구사항을 고려하지 않는다. |
| 1 | 목표는 언급하지만 처리 구조를 제시하지 못한다. |
| 2 | 요구 수준을 만족하는 구조와 작동 이유를 설명한다. |
| 3 | 2점에 더해 대표적인 문제점이나 한계를 이해하고 개선 방안을 설명한다. |

---

## NFR-2. Consistency

... (NFR별 요구 수준과 관련 평가 항목 반복)

---
````

### 렌더 규칙

- 헤딩 단계: `# 주제` → `## NFR` (요약표) → `## NFR-{n}. 이름` → `### C{n}` (criterion)
- 주제 바로 아래에 **대상 연차**와 **배점**(criterion weight 합, 고정 문구 아님)을 한 줄씩
- md는 요약표와 NFR별 요구 수준·평가 항목·레벨표를 유지한다. 조사·선정 기록은 별도 섹션으로 추가하지 않는다.
- 4섹션을 합칠 때는 `# 주제`와 대상 연차를 합치는 쪽에서 한 번만 내고,
  각 섹션은 `## NFR`부터 끼워 넣는다
- `## NFR` 바로 아래에 출력 샘플의 요약표를 넣는다. 채점 규칙·환산 설명은 본문에 추가하지 않는다.
- NFR별로 요구 수준을 한 번 표시하고, 그 아래 관련 평가 항목을 묶는다.
- NFR 이름은 kind의 표시명이다. latency는 Low Latency, throughput은 High Throughput, 나머지는 밑줄을 공백으로 바꿔 Title Case로 표시한다. consistency를 자동으로 Strong Consistency로 바꾸지는 않는다.
- 요약표는 `NFR id · 이름`, `C번호. 제목`, 배점, 획득 순이다. 본문 항목 제목은 `### C번호. 제목 · 배점`이다.
- **요구 수준**: 정량 목표면 `` `kind` — 목표`` 다음 줄에 statement,
  정성 목표면 `` `kind` — statement`` 한 줄 (정성 목표는 statement의 요약이라 반복하지 않는다)
- 목표 수치는 천 단위 콤마, 지수 표기 없음, 숫자와 단위는 띄우되 `%`만 붙인다
  (`p99 500 ms`, `peak 10,000 msg/s`, `99.9%`)
- 레벨표는 데이터 순서와 상관없이 score 0 → 3 순으로 쓴다
- NFR 표시 번호는 `confirmed_nfrs` 순서대로 `NFR-{n}`, 평가 항목은 항목 순서대로 `C{n}`을 붙인다. JSON의 원본 id와 참조는 유지한다.
- **출처 표시(`[D1]` 인용, 근거 표)는 넣지 않는다.** 문서 id(`D{n}`)는 데이터와 하네스 안에서만 쓴다
- descriptor 안의 `|`는 `\|`로 이스케이프
- 별도 trade-off 블록은 출력하지 않는다. 원본 JSON의 tradeoffs와 근거는 유지한다.

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

### Post-Render (M2)

렌더된 md를 되읽어(`render/post_render.py`의 `read_back`) 원본 `NFRExport`·`InterviewBrief`와 값 단위로 비교한다.
`check_rendered(md, export, brief)`.
렌더러가 일부러 바꾸는 것(표 칸 이스케이프, 헤딩 공백 접기, 목표 수치 표기, 레벨 정렬)은
되돌리거나 같은 규칙을 적용한 뒤 비교한다.

| md 부분 | 검사 | 코드 | path |
|---|---|---|---|
| 머리말 | 주제(공백 접기)·대상 연차가 brief와, 배점이 weight 합과 같고, `## NFR` 헤딩이 있음 | `RENDER_HEADER_MISMATCH` | `header` |
| 요약표 | `[NFR id · 이름, C번호. title, 배점]`이 항목 순서와 같음 | `RENDER_SUMMARY_MISMATCH` | `rubric.criteria` |
| NFR 섹션들 | NFR id·이름 목록이 원본 순서와 같음 | `RENDER_SECTIONS_MISMATCH` | `confirmed_nfrs` |
| criterion 섹션들 | 표시 번호 목록이 NFR별로 묶인 항목 순서와 같음 (누락·중복·순서) | `RENDER_SECTIONS_MISMATCH` | `rubric.criteria` |
| 헤딩 | title(공백 접기 적용)·배점이 원본과 같음 | `RENDER_HEADING_MISMATCH` | `rubric.criteria[i].title` / `.weight` |
| 평가 항목 | 본문이 `description`과 같음 | `RENDER_DESCRIPTION_MISMATCH` | `rubric.criteria[i].description` |
| 요구 수준 | `` `kind` — 목표/statement``와 같음 | `RENDER_REQUIREMENT_MISMATCH` | `confirmed_nfrs[k]` |
| 레벨표 | 행들이 원본 레벨(score 순)의 `(score, 서술)` 목록과 같음. 행 수 차이도 여기 | `RENDER_LEVELS_MISMATCH` | `rubric.criteria[i].levels` |

code 하나가 md의 한 부분을 가리킨다 — 이름만 보고 고칠 템플릿 블록을 안다.
레벨이 4개인지는 하네스 `core.levels`가 보장하므로, Post-Render는 옮기면서 달라졌는지만 본다.

Post-Render Finding은 렌더러 코드 버그라 repair 루프를 돌리지 않는다 (M7에서 즉시 실패).

### Judge (M6) — 형식과 무관하게 의미만

Judge는 문서 근거·채점 가능성·점수 단계의 의미를 검증한다.

---

## 4. 열린 항목

- descriptor 15~200자. 첫 골든셋(Pro)의 score 3이 228~248자였고 이를 줄이려고 잡은 값이다.
  Day 9 실측에서 `LEVEL_DESCRIPTOR_TOO_LONG` 발생률을 보고 조정
- 200자 descriptor 4개가 든 레벨표의 가독성은 Day 3에 골든셋을 실제로 렌더해보고 판단한다.
  읽기 힘들면 표를 레벨별 목록으로 바꾼다
