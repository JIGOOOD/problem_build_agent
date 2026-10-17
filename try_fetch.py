"""실행: uv run python try_fetch.py 'https://원하는-문서-URL'"""

import argparse
import json
import logging
import tempfile
import time
from datetime import UTC, datetime
from pathlib import Path
from threading import Event, Thread

from archgen.paths import PROJECT_ROOT
from archgen.retrieval.crawler import FetchTool, HttpFetcher, create_fetch_client


def run(url: str, *, log_root: Path | None = None) -> int:
    log_root = log_root if log_root is not None else PROJECT_ROOT / ".archgen" / "fetch"
    log_root.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).astimezone().strftime("%Y%m%d-%H%M%S-")
    run_dir = Path(tempfile.mkdtemp(prefix=timestamp, dir=log_root))
    started = time.monotonic()
    stopped = Event()
    logger = logging.getLogger("archgen.retrieval.crawler")
    handler = logging.FileHandler(run_dir / "run.log", encoding="utf-8")
    logger.addHandler(handler)

    def show(message: str) -> None:
        print(message, flush=True)
        handler.acquire()
        try:
            handler.stream.write(message + "\n")
            handler.flush()
        finally:
            handler.release()

    def show_elapsed() -> None:
        while not stopped.wait(5):
            show(f"[실행 중] {time.monotonic() - started:.1f}초 경과")

    record = {"url": url, "status": "running"}
    result_path = run_dir / "fetch.json"

    def save_record() -> None:
        result_path.write_text(
            json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    progress = Thread(target=show_elapsed, daemon=True)
    try:
        show(f"실행 로그: {run_dir}")
        show(f"M4-3: 본문 수집 중... {url}")
        save_record()
        progress.start()
        with create_fetch_client() as client:
            tool = FetchTool(HttpFetcher(client))
            result = tool.fetch(url)
        if isinstance(result, str):
            record.update(status="error", error=result)
            show(result)
            return 1
        document = tool.documents[result.doc_id]
        record.update(
            status="completed",
            result=result.model_dump(),
            document=document.model_dump(),
        )
        show(f"제목: {result.title or '(없음)'}")
        show(f"문서 ID: {result.doc_id}")
        show(f"저장된 본문: {len(document.content)}자 / 문장: {len(result.sentences)}개")
        for sentence in result.sentences[:3]:
            show(f"\n[{sentence.index}] {sentence.text[:300]}")
        show(f"\n전체 문장·저장 문서: {result_path}")
        return 0
    except BaseException as error:
        record.update(status="error", error_type=type(error).__name__, error=str(error))
        show(f"실행 중단: {type(error).__name__}: {error}")
        raise
    finally:
        stopped.set()
        if progress.ident is not None:
            progress.join()
        record["seconds"] = time.monotonic() - started
        save_record()
        show(f"\n전체 실행 시간: {record['seconds']:.2f}초")
        logger.removeHandler(handler)
        handler.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="URL 한 개의 본문을 실제로 수집한다.")
    parser.add_argument("url", help="수집할 문서의 HTTP(S) URL")
    args = parser.parse_args()
    if not args.url.startswith(("https://", "http://")):
        parser.error("URL은 http:// 또는 https://로 시작해야 합니다.")
    raise SystemExit(run(args.url))
