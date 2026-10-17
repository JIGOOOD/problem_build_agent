# M7 실행

API 없이 통합 테스트:

```bash
uv run pytest -q tests/test_graph.py tests/test_generation_e2e.py tests/test_generation_service.py tests/test_try_generation.py
```

API 키 복구 후 실제 생성:

```bash
uv run python try_generation.py '실시간 채팅 서비스' --seniority 미들 --notes '메시지 보존'
```

Research·NFR 선정·루브릭 생성은 `small`을 사용한다. Judge는 기본 비활성화다.
`.env`에 API 키·주소·모델 설정과 `TAVILY_API_KEY`가 필요하다.
현재 OpenAI 설정은 `gpt-6.1-sol`이며 Responses API로 연결한다.
변수 이름 `OPENROUTER_*`는 기존 코드와의 호환을 위해 유지한다.

Research 초기 계획·NFR 선정·루브릭 생성 및 재생성·Judge는 각 Pydantic 모델에서 변환한
JSON Schema를 `strict: true`로 API에 전달한다. 모든 키를 요구하고 추가 필드는 금지하며,
목표가 없는 필드는 `null`, 빈 목록은 `[]`로 반환한다. 수동 실행 파일에도 동일하게 적용한다.
응답은 기존 Pydantic·하네스·Judge로 계속 검증한다. 배점 합·참조 관계·한국어·채점 품질은
스키마 강제만으로 보장되지 않는다. 생성 응답 파싱 실패는 중단하고 Judge 파싱 실패는 WARN을 남긴다.

2026-10-14 실제 검증: 저장된 주문/결제 조사 결과를 재사용해 선정·생성·Judge·1회 수정·재검토를
실제 API로 실행했다. `.archgen/structured-generation/20261014-073051-6j1vlo28/`에 기록했으며,
최종 상태는 `complete`, 잔존 Finding은 0개다. 새 검색과 프롬프트 튜닝은 하지 않았다.

`.archgen/generation/<실행>/`에 다음을 저장한다.

- `run.log`, `llm-*-input.json`, `llm-*-response.json`: 진행과 LLM 입출력
- `input.json`, `research.json`, `selection.json`: 입력·보존 문서·확정 NFR
- `nfr_export-*.json`, `*-findings-*.json`: 최초 생성과 최대 2회 재생성 기록
- `status.json`, `findings.json`, `nfr_export.json`: 종료 상태·잔존 지적·최종 JSON
- `nfr_rubric.md`: 검증을 통과했을 때만 생성
- `error.json`: 호출·입력·응답 처리 예외

하네스 또는 Judge ERROR는 합계 최대 2회 재생성한다. 조사와 NFR 선정은 반복하지 않는다.
렌더 검증 ERROR는 즉시 실패한다. WARN은 기록하고 계속 진행한다.
실패 시 스크립트 종료 코드는 1이다. 근거 부족도 성공으로 처리하지 않는다.

M5 실제 생성과 사용자 검토:

```bash
uv run python try_nfr_agent.py
```

M6 골든 루브릭의 Judge 오탐 검증:

```bash
uv run python try_judge.py
```

Judge 입출력과 Finding은 `.archgen/judge/<실행>/`에 저장한다.
Finding이 하나라도 있으면 통과시키지 않고 사람이 근거와 대조한다.

TUI에서 Ctrl+G로 생성하면 현재 단계·경과 시간과 로딩 표시가 화면에 나타난다.
완료·중단·실패 시 로딩과 시간 갱신이 멈추며, 생성 중에는 Ctrl+G로 중복 실행하지 않는다.

직접 입력하며 API 없이 진행 표시를 확인하려면:

```bash
uv run archgen --fake
```

연차·주제·중점 사항을 입력한 뒤 Ctrl+G를 누른다. 조사·선정·기준 작성 단계는 각각 5초씩 대기한다.
입력은 기록하지만 응답은 고정된 채팅 골든 예시다. 모델·검색 API를 호출하지 않으며 키도 필요 없다.
로그와 결과는 `.archgen/fake-generation/<실행>/`에 저장한다.

M5 실제 출력 확인과 M6 Judge 오탐 검증을 완료한 뒤, large Judge를 포함한 실제 통합 검증:

```bash
ARCHGEN_LIVE_TEST=1 uv run pytest -q -m slow tests/test_generation_live.py
```

이 명령은 실제 모델·Tavily·문서 사이트를 호출하며 비용이 발생한다.
일반 Python 호출에서는 `run_generation(brief, judge_enabled=True)`로 Judge를 활성화한다.
Fake 테스트 통과는 실제 NFR·루브릭·Judge의 의미적 품질을 보장하지 않는다.
