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

M5 실제 출력 확인과 M6 Judge 오탐 검증을 완료한 뒤, large Judge를 포함한 실제 통합 검증:

```bash
ARCHGEN_LIVE_TEST=1 uv run pytest -q -m slow tests/test_generation_live.py
```

이 명령은 실제 모델·Tavily·문서 사이트를 호출하며 비용이 발생한다.
일반 Python 호출에서는 `run_generation(brief, judge_enabled=True)`로 Judge를 활성화한다.
Fake 테스트 통과는 실제 NFR·루브릭·Judge의 의미적 품질을 보장하지 않는다.
