# ArchGen

시스템 디자인 면접 문제와 채점 루브릭을 생성하는 터미널 우선 도구.
심층 인터뷰로 요구사항을 좁히고, 4개 섹션 에이전트가 병렬로 루브릭을 쓰고,
플러그인 하네스가 검증한 뒤, 고정 템플릿으로 `.md` 를 렌더링합니다.

> 현재는 실행 가능한 TUI 골격 단계입니다. 인터뷰 입력은 동작하지만 LLM 생성,
> 하네스, 렌더링은 후속 단계입니다.

TUI의 `Ctrl+G`는 LangGraph 기본 워크플로를 실행합니다. 현재는
`intake → research → author → validate → finalize` 상태 전이와 이벤트 기록만
수행하며, 각 실제 에이전트와 하네스는 아직 연결되지 않았습니다.

## 설계 원칙

1. **LLM 은 마크다운을 쓰지 않는다.** 구조화 필드만 생성하고 `.md` 는 Jinja2
   템플릿이 렌더링합니다. 섹션 순서·헤딩 레벨·표 구조가 코드로 고정됩니다.
2. **내부는 nested, 경계에서 flatten.** 구조화 출력 정확도를 위해 모델은 중첩
   스키마를 다루고, flat JSON 은 `schema/flatten.py` 가 만듭니다.
3. **검증은 결정론 우선.** 규칙으로 잡을 수 있는 건 하네스가, 나머지(모호성,
   난이도 정합)만 LLM judge 가 봅니다.

## 실행

```bash
python -m pip install -e ".[dev]"
archgen                # TUI 시작
archgen harnesses      # 현재는 골격 상태를 출력
pytest                 # CLI 골격 검증
```

TUI 에서 질문에 답하다가 `Ctrl+G` 또는 `/done` 으로 생성을 시작합니다.

## 목표 파이프라인 (LangGraph)

인터뷰는 슬롯 채우기 루프(`agents/interviewer.py`)로 별도 진행하고, 인터뷰 종료 후
본 생성 파이프라인은 `core/graph.py` 의 `StateGraph` 하나로 표현됩니다. 노드 =
서브 에이전트, 재생성 루프 = 조건부 엣지입니다.

```
research → problem → rubric → harness ─┬─(errors, 예산 남음)─→ repair ─┐
                                        │                              │
                                        └─(통과 또는 예산 소진)→ finalize → END
                                        ^______________________________|
```

- `rubric` 노드 내부에서 NFR / API / Entity / Architecture 4개 서브 에이전트가
  `asyncio.gather` 로 병렬 실행됩니다 (`agents/authors.py:build_rubric`).
- `harness` 노드는 PRE_RENDER → 렌더 → POST_RENDER → (예산 남았으면) LLM judge 순으로
  돌고, `ERROR` 가 있으면 `repair` 로, 없거나 예산이 소진되면 `finalize` 로 분기합니다.
- `repair` 노드는 finding 의 `RepairTarget` 별로 해당 서브 에이전트만 재실행한 뒤
  `harness` 로 되돌아갑니다. 예산은 `max_attempts` (기본 2) 로 하드 상한.

LLM 호출은 `llm/client.py` 의 `LLM.parse()` / `LLM.text()` 로 통일되어 있고, 내부는
`ChatPromptTemplate | ChatOpenAI.with_structured_output(schema)` LCEL 체인입니다.
에이전트 코드는 이 인터페이스만 보므로 모델 교체·재시도 정책 변경이 `llm/client.py`
한 곳에서 끝납니다.

## 목표 산출물

`artifacts/<problem_id>/` 아래에:

- `problem.json` — depth 없는 flat JSON
- `rubric.md` — 템플릿 렌더 결과
- `solution.md` — 해답지 (선택)

```jsonc
{
  "problem_id": "sd-260817143022",
  "title": "주문 시스템 설계",
  "difficulty": 4,
  "tags": "order,payment,idempotency",
  "functional_requirements.0.id": "FR-1",
  "functional_requirements.0.statement": "주문을 생성한다",
  "rubric.api_endpoints.0.path": "/v1/orders",
  "rubric.sections.0.criteria.0.levels.3.descriptor": "...",
  "rubric_md_path": "sd-260817143022/rubric.md",
  "rubric_sha256": "9f2c…",
  "harness_attempts": 1,
  "harness_findings.0.code": "NFR_NOT_ADDRESSED"
}
```

평탄화 규칙: 리스트는 인덱스 키(`a.0.b`), `CSV_FIELDS` 에 등록된 필드만 콤마
문자열, `None` 과 빈 컬렉션은 키 자체를 생략. `flatten`/`unflatten` 왕복은
테스트로 고정되어 있습니다.

## 목표 채점 모델

criterion 마다 0–3 레벨. 가중 합산 후 100점 정규화.

```
criterion_pct = level / 3
section_pct   = Σ(w × criterion_pct) / Σw
total         = Σ(section.weight × section_pct)      # section weight 합 = 100
```

criterion 마다 역량 축(`TRADE_OFF`, `DATA_MANAGEMENT`, `FAILURE_RECOVERY`,
`HIGH_TRAFFIC`, `COMPUTER_SCIENCE`)이 붙어 있어 섹션 점수와 별개로 축별 롤업
점수가 같은 계산 한 번으로 나옵니다. `RubricSpec.score(awarded)` 참고.

## 목표 하네스 추가

`harnesses/` 에 파일 하나 떨어뜨리면 끝입니다. 등록 코드 수정 불필요.
계약과 예시는 [docs/HARNESS.md](docs/HARNESS.md).

내장된 4개는 레퍼런스입니다:

| id | 검사 |
| --- | --- |
| `core.weight-sum` | 섹션 배점 합 100, criterion id 중복 |
| `core.levels` | 4개 레벨 존재, 점수 0-3, 서술 중복/과소 |
| `core.nfr-measurable` | 모든 NFR 이 숫자+단위 포함 |
| `core.cross-ref` | FR↔API, API↔Entity, Component↔NFR 참조 정합성 |

## 현재 디렉터리

```
src/archgen/
  cli.py      `archgen` 명령 진입점
  tui/        Textual 앱 골격
  core/       향후 애플리케이션 서비스/워크플로 경계
  domain/     향후 Pydantic 도메인 모델 경계
  harness/    향후 검증 하네스 경계
  render/     향후 결정론적 렌더링 경계
```

## 남은 작업

- 하네스 본 구현 (내장 4개는 패턴 예시일 뿐)
- 골든 셋: 손으로 쓴 루브릭 3–5개. 하네스 규칙과 few-shot 의 근거가 됩니다
- 모델명은 `.env` 에서 조정하세요 (`ARCHGEN_MODEL_LARGE` / `_SMALL`)
