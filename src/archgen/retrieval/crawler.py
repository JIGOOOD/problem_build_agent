"""Research Agent가 읽을 문서 본문과 문단 번호를 반환한다."""

import logging
import re
from collections.abc import Callable
from uuid import uuid4

import httpx
from trafilatura import bare_extraction
from trafilatura.xml import xmltotxt

from archgen.domain.research import (
    MAX_CONTENT_CHARS,
    MAX_PARAGRAPH_CHARS,
    Document,
    FetchResult,
    Paragraph,
)

_LOGGER = logging.getLogger(__name__)
_SENTENCE_END = re.compile(r"""[.!?。！？]["'”’)\]]*(?=\s|$)""")


def _split_long_paragraph(text: str) -> list[str]:
    chunks: list[str] = []
    while len(text) > MAX_PARAGRAPH_CHARS:
        boundaries = [
            match.end()
            for match in _SENTENCE_END.finditer(text)
            if match.end() <= MAX_PARAGRAPH_CHARS
        ]
        boundary = boundaries[-1] if boundaries else MAX_PARAGRAPH_CHARS
        chunks.append(text[:boundary].rstrip())
        text = text[boundary:].lstrip()
    if text:
        chunks.append(text)
    return chunks


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


class FetchTool:
    """조사 실행마다 문서를 저장하고 성공한 URL의 결과를 재사용한다."""

    def __init__(self, fetcher: Callable[[str], dict[str, str]]) -> None:
        self._fetcher = fetcher
        self.documents: dict[str, Document] = {}
        self._results: dict[str, FetchResult] = {}

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
                return f"fetch[{url}] 실패(1회 요청): {type(error).__name__}: {error}"
            try:
                page = self._fetcher(url)
            except Exception as error:  # noqa: BLE001 — 재시도 실패는 오류로 반환한다.
                return f"fetch[{url}] 실패(2회 요청): {type(error).__name__}: {error}"
        content = page["content"]
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
        parts = [part for part in parts if part]
        if not parts:
            return f"fetch[{url}] 실패: 본문이 비어 있다."
        parts = [chunk for part in parts for chunk in _split_long_paragraph(part)]
        doc_id = f"doc-{uuid4().hex}"
        result = FetchResult(
            doc_id=doc_id,
            url=url,
            title=page["title"],
            paragraphs=[
                Paragraph(index=index, text=part) for index, part in enumerate(parts)
            ],
        )
        self.documents[doc_id] = Document(
            id=doc_id, url=url, title=page["title"], content=content
        )
        self._results[url] = result
        return result
