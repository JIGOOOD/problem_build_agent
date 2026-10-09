"""실행: uv run python try_keep.py --indices 1 --indices 3"""

import argparse
import json
import tempfile
from datetime import UTC, datetime
from pathlib import Path

from archgen.domain.research import FetchResult
from archgen.paths import PROJECT_ROOT
from archgen.research.keep import KeepTool


def latest_successful_fetch() -> Path:
    paths = sorted(
        (PROJECT_ROOT / ".archgen" / "fetch").glob("*/fetch.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    for path in paths:
        if json.loads(path.read_text(encoding="utf-8")).get("status") == "completed":
            return path
    raise ValueError("성공한 fetch 결과가 없습니다. 먼저 try_fetch.py를 실행하세요.")


def run(
    fetch_path: Path, selections: list[list[int]], *, log_root: Path | None = None
) -> int:
    if not selections:
        raise ValueError("선택할 문단 번호를 지정해 주세요.")
    data = json.loads(fetch_path.read_text(encoding="utf-8"))
    if data.get("status") != "completed":
        raise ValueError("성공한 fetch.json을 지정해 주세요.")
    fetched = FetchResult.model_validate(data.get("result"))
    message = {
        "role": "tool",
        "tool_call_id": "fetch-1",
        "content": fetched.model_dump_json(),
    }
    before = dict(message)
    tool = KeepTool()
    tool.register("query-demo", fetched, message)
    print(f"입력: {fetch_path}")
    print(f"제목: {fetched.title}")
    print(f"선택 전 기록: {len(before['content'])}자")
    steps = []
    exit_code = 0
    for number, indices in enumerate(selections, start=1):
        step_before = dict(message)
        response = tool.keep(fetched.doc_id, indices)
        document = tool.documents.get(fetched.doc_id)
        steps.append(
            {
                "indices": indices,
                "response": response,
                "before_message": step_before,
                "after_message": dict(message),
                "document": document.model_dump() if document is not None else None,
            }
        )
        remaining = [p["index"] for p in json.loads(message["content"])["paragraphs"]]
        print(f"\n호출 {number}: keep({fetched.doc_id!r}, {indices})")
        print(f"keep 반환값: {response}")
        print(f"남은 문단: {remaining} / 대화 기록: {len(message['content'])}자")
        if document is not None:
            print(f"저장된 본문:\n{document.content}")
        if not response.isdecimal():
            exit_code = 1
            break
    document = tool.documents.get(fetched.doc_id)

    log_root = log_root if log_root is not None else PROJECT_ROOT / ".archgen" / "keep"
    log_root.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).astimezone().strftime("%Y%m%d-%H%M%S-")
    run_dir = Path(tempfile.mkdtemp(prefix=timestamp, dir=log_root))
    output = run_dir / "keep.json"
    output.write_text(
        json.dumps(
            {
                "fetch_path": str(fetch_path.resolve()),
                "selections": selections,
                "steps": steps,
                "response": response,
                "before_message": before,
                "after_message": message,
                "document": document.model_dump() if document is not None else None,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"보관한 원본 문단 수: {len(fetched.paragraphs)}")
    print(f"\n선택 전후 기록·저장 문서: {output}")
    return exit_code


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="저장한 실제 fetch 결과에서 문단을 선택한다."
    )
    parser.add_argument(
        "--fetch", type=Path, help="fetch.json 경로 (기본: 최근 성공 결과)"
    )
    parser.add_argument(
        "--indices",
        type=int,
        nargs="+",
        action="append",
        help="호출별 문단 번호. 여러 번 지정하면 같은 문서에 차례로 keep한다.",
    )
    args = parser.parse_args()
    try:
        raise SystemExit(
            run(args.fetch or latest_successful_fetch(), args.indices or [[1, 3]])
        )
    except (OSError, ValueError) as error:
        parser.exit(1, f"오류: {error}\n")
