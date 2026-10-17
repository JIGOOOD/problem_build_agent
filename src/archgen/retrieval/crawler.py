"""Research Agent가 읽을 문서 본문과 문장 번호를 반환한다."""

import logging
import re
from collections.abc import Callable
from uuid import uuid4

import httpx
from trafilatura import bare_extraction
from trafilatura.xml import xmltotxt

from archgen.domain.research import (
    MAX_CONTENT_CHARS,
    Document,
    FetchResult,
    Sentence,
)

_LOGGER = logging.getLogger(__name__)
FETCH_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9,ko;q=0.8",
}
_SENTENCE_END = re.compile(r"""[.!?。！？]["'”’)\]]*(?=\s|$)""")

# 약어 제외
_ABBREVIATION = re.compile(
    r"\b(?:e\.g|i\.e|Mr|Mrs|Ms|Dr|Prof|vs|etc|Fig|No)\.$", re.IGNORECASE
)


def _split_sentences(text: str) -> list[str]:
    """문장부호 경계에서 원문을 나눈다. 긴 문장도 중간에서 자르지 않는다."""
    sentences = []
    start = 0
    for match in _SENTENCE_END.finditer(text):
        if _ABBREVIATION.search(text[: match.end()]):
            continue
        sentences.append(text[start : match.end()].strip())
        start = match.end()
    if text[start:].strip():
        sentences.append(text[start:].strip())
    return sentences


def create_fetch_client(**kwargs) -> httpx.Client:
    """본문 수집에 사용하는 기본 헤더를 한곳에서 적용한다."""
    return httpx.Client(headers=FETCH_HEADERS, **kwargs)


class HttpFetcher:
    """HTTP 응답의 HTML에서 본문과 제목을 추출한다."""

    def __init__(self, client: httpx.Client) -> None:
        self._client = client

    def __call__(self, url: str) -> dict[str, str]:
        response = self._client.get(url, follow_redirects=True, timeout=20)
        response.raise_for_status()
        document = bare_extraction(
            response.text,
            url=str(response.url),
            with_metadata=True,
            include_comments=False,
            prune_xpath=["//nav", "//footer"],
        )
        if document is None:
            return {"title": "", "content": ""}
        blocks = [
            xmltotxt(block, include_formatting=False).strip() for block in document.body
        ]
        return {
            "title": document.title or "",
            "content": "\n\n".join(block for block in blocks if block),
        }


def _fetch_failure(url: str, error: Exception, attempts: int) -> str:
    message = f"fetch[{url}] 실패({attempts}회 요청): {type(error).__name__}: {error}"
    _LOGGER.warning("%s", message)
    return message


class FetchTool:
    """조사 실행마다 문서를 저장하고 성공한 URL의 결과를 재사용한다."""

    def __init__(self, fetcher: Callable[[str], dict[str, str]]) -> None:
        self._fetcher = fetcher
        self.documents: dict[str, Document] = {}
        self._results: dict[str, FetchResult] = {}  # url fetch 결과 캐시

    def fetch(self, url: str) -> FetchResult | str:
        if url in self._results:
            return self._results[url]
        try:
            page = self._fetcher(url)
        except Exception as error:  # noqa: BLE001 — 외부 실패는 오류 문자열로 반환한다.
            retryable = isinstance(
                error,
                (
                    TimeoutError,
                    ConnectionError,
                    httpx.TimeoutException,
                    httpx.ConnectError,
                ),
            ) or (
                isinstance(error, httpx.HTTPStatusError)
                and (
                    error.response.status_code == 429
                    or 500 <= error.response.status_code < 600
                )
            )
            if not retryable:
                return _fetch_failure(url, error, 1)
            try:
                page = self._fetcher(url)
            except Exception as error:  # noqa: BLE001 — 재시도 실패는 오류로 반환한다.
                return _fetch_failure(url, error, 2)
        content = page["content"]  # 전문
        if len(content) > MAX_CONTENT_CHARS:
            _LOGGER.warning(
                "본문 상한 초과로 잘라낸다: url=%s, 원문=%d자, 상한=%d자",
                url,
                len(content),
                MAX_CONTENT_CHARS,
                extra={
                    "url": url,
                    "original_chars": len(content),
                    "max_content_chars": MAX_CONTENT_CHARS,
                },
            )
            content = content[:MAX_CONTENT_CHARS]
        parts = [part.strip() for part in re.split(r"\r?\n[ \t]*\r?\n", content)]
        parts = [part for part in parts if part]  # 한 문단씩
        if not parts:
            return f"fetch[{url}] 실패: 본문이 비어 있다."
        parts = [
            sentence for part in parts for sentence in _split_sentences(part)
        ]  # 한 문장씩
        doc_id = f"doc-{uuid4().hex}"
        result = FetchResult(
            doc_id=doc_id,
            url=url,
            title=page["title"],
            sentences=[
                Sentence(index=index, text=part) for index, part in enumerate(parts)
            ],
        )
        self.documents[doc_id] = Document(
            id=doc_id, url=url, title=page["title"], content=content
        )
        self._results[url] = result
        return result
