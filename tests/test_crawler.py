import logging

import httpx
import pytest

from archgen.retrieval.crawler import FetchTool, HttpFetcher


class FakeFetcher:
    def __init__(self, *responses):
        self.responses = list(responses)
        self.calls = []

    def __call__(self, url):
        self.calls.append(url)
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def test_fetch_returns_document_metadata_and_numbered_original_paragraph() -> None:
    url = "https://docs.example/chat"
    fetcher = FakeFetcher(
        {"title": "채팅 설계", "content": "메시지 전달 시간을 측정한다."}
    )
    tool = FetchTool(fetcher)

    result = tool.fetch(url)

    assert not isinstance(result, str)
    assert result.doc_id
    assert result.model_dump() == {
        "doc_id": result.doc_id,
        "url": url,
        "title": "채팅 설계",
        "paragraphs": [{"index": 0, "text": "메시지 전달 시간을 측정한다."}],
    }
    assert tool.documents[result.doc_id].model_dump() == {
        "id": result.doc_id,
        "url": url,
        "title": "채팅 설계",
        "content": "메시지 전달 시간을 측정한다.",
    }
    assert fetcher.calls == [url]


def test_fetch_splits_on_blank_lines_and_numbers_only_nonempty_paragraphs() -> None:
    content = "\n\n 첫 문단의 첫 줄\n첫 문단의 둘째 줄 \n \t\n\n\n둘째 문단\r\n\r\n\t\r\n\r\n셋째 문단\n\n"
    tool = FetchTool(FakeFetcher({"title": "설계", "content": content}))

    result = tool.fetch("https://docs.example/chat")

    assert not isinstance(result, str)
    assert [paragraph.model_dump() for paragraph in result.paragraphs] == [
        {"index": 0, "text": "첫 문단의 첫 줄\n첫 문단의 둘째 줄"},
        {"index": 1, "text": "둘째 문단"},
        {"index": 2, "text": "셋째 문단"},
    ]


@pytest.mark.parametrize("size", [11999, 12000, 12001])
def test_fetch_caps_content_before_numbering_and_logs_only_when_truncated(size, caplog):
    content = ("가" * 98 + "\n\n") * 121
    content = content[:size]
    url = "https://docs.example/long"
    tool = FetchTool(FakeFetcher({"title": "긴 문서", "content": content}))

    with caplog.at_level(logging.WARNING, logger="archgen.retrieval.crawler"):
        result = tool.fetch(url)

    assert not isinstance(result, str)
    expected = [part.strip() for part in content[:12000].split("\n\n") if part.strip()]
    assert [p.text for p in result.paragraphs] == expected
    assert [p.index for p in result.paragraphs] == list(range(len(expected)))
    assert tool.documents[result.doc_id].content == content[:12000]
    records = [r for r in caplog.records if r.name == "archgen.retrieval.crawler"]
    if size > 12000:
        assert len(records) == 1
        assert records[0].levelno == logging.WARNING
        assert records[0].url == url
        assert records[0].original_chars == size
        assert records[0].max_content_chars == 12000
    else:
        assert records == []


def test_fetch_reuses_url_result_but_assigns_other_urls_distinct_ids() -> None:
    fetcher = FakeFetcher(
        {"title": "첫 문서", "content": "첫 원문"},
        {"title": "둘째 문서", "content": "둘째 원문"},
    )
    tool = FetchTool(fetcher)
    first_url = "https://docs.example/a"
    second_url = "https://docs.example/b"

    first = tool.fetch(first_url)
    cached = tool.fetch(first_url)
    second = tool.fetch(second_url)

    assert not isinstance(first, str)
    assert not isinstance(second, str)
    assert cached == first
    assert first.doc_id != second.doc_id
    assert fetcher.calls == [first_url, second_url]
    assert set(tool.documents) == {first.doc_id, second.doc_id}
    assert tool.documents[first.doc_id].content == "첫 원문"
    assert tool.documents[second.doc_id].content == "둘째 원문"


@pytest.mark.parametrize("content", ["\n\n\t\r\n\r\n"])
def test_fetch_returns_error_without_storing_an_empty_document(content) -> None:
    url = "https://docs.example/empty"
    fetcher = FakeFetcher({"title": "빈 문서", "content": content})
    tool = FetchTool(fetcher)

    result = tool.fetch(url)

    assert isinstance(result, str)
    assert url in result
    assert "본문이 비어" in result
    assert tool.documents == {}
    assert fetcher.calls == [url]


@pytest.mark.parametrize(
    "error", [httpx.ReadTimeout("timeout"), httpx.ConnectError("connection failed")]
)
def test_fetch_retries_once_and_returns_a_successful_second_response(error) -> None:
    url = "https://docs.example/retry"
    fetcher = FakeFetcher(error, {"title": "복구된 문서", "content": "복구된 원문"})
    tool = FetchTool(fetcher)

    result = tool.fetch(url)

    assert not isinstance(result, str)
    assert result.title == "복구된 문서"
    assert [p.model_dump() for p in result.paragraphs] == [
        {"index": 0, "text": "복구된 원문"}
    ]
    assert fetcher.calls == [url, url]
    assert tool.documents[result.doc_id].content == "복구된 원문"


@pytest.mark.parametrize("error", [TimeoutError("timeout")])
def test_fetch_returns_error_after_exactly_two_failed_attempts(error) -> None:
    url = "https://docs.example/fail"
    fetcher = FakeFetcher(TimeoutError("first failure"), error)
    tool = FetchTool(fetcher)

    result = tool.fetch(url)

    assert isinstance(result, str)
    assert url in result
    assert type(error).__name__ in result
    assert str(error) in result
    assert fetcher.calls == [url, url]
    assert tool.documents == {}


def test_http_fetch_extracts_title_and_paragraphs_without_navigation_or_footer() -> None:
    first = "채팅 서버는 WebSocket 연결을 유지하며 메시지 지연 시간을 측정한다. " * 6
    second = "장애 시 메시지를 재전송하고 중복 수신을 멱등 처리로 방지한다. " * 6
    html = (
        "<html><head><title>채팅 기술 문서</title></head><body>"
        '<nav><a href="/home">제거할 메뉴</a></nav>'
        f"<article><p>{first}</p><p>{second}</p></article>"
        "<footer>제거할 푸터</footer></body></html>"
    )
    requests = []

    def respond(request):
        requests.append(request)
        return httpx.Response(200, text=html, headers={"Content-Type": "text/html"})

    with httpx.Client(transport=httpx.MockTransport(respond)) as client:
        tool = FetchTool(HttpFetcher(client))
        result = tool.fetch("https://docs.example/chat")

    assert not isinstance(result, str)
    assert result.title == "채팅 기술 문서"
    assert [p.text for p in result.paragraphs] == [first.strip(), second.strip()]
    assert [p.index for p in result.paragraphs] == [0, 1]
    assert len(requests) == 1
    assert str(requests[0].url) == "https://docs.example/chat"
    assert "제거할 메뉴" not in tool.documents[result.doc_id].content
    assert "제거할 푸터" not in tool.documents[result.doc_id].content


@pytest.mark.parametrize(
    ("content", "expected"),
    [
        ("가" * 1000, ["가" * 1000]),
        ("가" * 1001, ["가" * 1000, "가"]),
        (
            "가" * 699 + ". " + "나" * 199 + "! " + "다" * 349 + "?",
            ["가" * 699 + ". " + "나" * 199 + "!", "다" * 349 + "?"],
        ),
    ],
    ids=[
        "exact-limit",
        "one-over",
        "sentence-packing",
    ],
)
def test_fetch_splits_long_paragraphs_at_sentences_with_1000_character_limit(
    content, expected
):
    tool = FetchTool(FakeFetcher({"title": "긴 문단", "content": content}))

    result = tool.fetch("https://docs.example/long-paragraph")

    assert not isinstance(result, str)
    assert [p.text for p in result.paragraphs] == expected
    assert [p.index for p in result.paragraphs] == list(range(len(expected)))
    assert all(0 < len(p.text) <= 1000 for p in result.paragraphs)
    assert tool.documents[result.doc_id].content == content


@pytest.mark.parametrize("status", [429, 503])
def test_http_fetch_retries_http_errors_without_storing_the_error_page(status) -> None:
    requests = []
    html = (
        "<html><head><title>오류 페이지</title></head><body><article><p>"
        + "오류 페이지 내용 " * 100
        + "</p></article></body></html>"
    )

    def respond(request):
        requests.append(request)
        return httpx.Response(status, text=html)

    with httpx.Client(transport=httpx.MockTransport(respond)) as client:
        tool = FetchTool(HttpFetcher(client))
        result = tool.fetch("https://docs.example/error")

    assert isinstance(result, str)
    assert "HTTPStatusError" in result
    assert str(status) in result
    assert len(requests) == 2
    assert tool.documents == {}


def test_http_fetch_does_not_retry_or_store_an_html_page_without_body_text() -> None:
    requests = []

    def respond(request):
        requests.append(request)
        return httpx.Response(200, text="<html><body></body></html>")

    with httpx.Client(transport=httpx.MockTransport(respond)) as client:
        tool = FetchTool(HttpFetcher(client))
        result = tool.fetch("https://docs.example/empty-html")

    assert isinstance(result, str)
    assert "본문이 비어" in result
    assert len(requests) == 1
    assert tool.documents == {}


@pytest.mark.parametrize(
    ("tag", "attributes"),
    [("nav", ""), ("div", ' id="comments"')],
    ids=["navigation", "comments"],
)
def test_http_fetch_keeps_navigation_and_comments_out_of_a_short_article(tag, attributes):
    body = "채팅 서버는 메시지 응답 지연 시간을 측정한다."
    noise = "메뉴에서 구매할 상품을 골라 광고를 확인하세요. " * 25
    html = (
        "<html><head><title>짧은 설계 문서</title></head><body>"
        f"<article><p>{body}</p></article>"
        f"<{tag}{attributes}><p>{noise}</p></{tag}></body></html>"
    )
    with httpx.Client(
        transport=httpx.MockTransport(lambda request: httpx.Response(200, text=html))
    ) as client:
        tool = FetchTool(HttpFetcher(client))
        result = tool.fetch("https://docs.example/short-article")

    assert not isinstance(result, str)
    assert [p.model_dump() for p in result.paragraphs] == [{"index": 0, "text": body}]
    assert tool.documents[result.doc_id].content == body
    assert noise.strip() not in tool.documents[result.doc_id].content


def test_http_fetch_preserves_heading_and_code_text_without_adding_markdown():
    heading = "메시지 지연"
    body = "채팅 메시지의 지연 시간을 p99로 측정한다. " * 15
    code = "retry(message_id)\nack(message_id)"
    html = (
        "<html><head><title>채팅 문서</title></head><body><article>"
        f"<h2>{heading}</h2><p>{body}</p><pre><code>{code}</code></pre>"
        "</article></body></html>"
    )
    with httpx.Client(
        transport=httpx.MockTransport(lambda request: httpx.Response(200, text=html))
    ) as client:
        tool = FetchTool(HttpFetcher(client))
        result = tool.fetch("https://docs.example/plain-text")

    assert not isinstance(result, str)
    expected = [heading, body.strip(), code]
    assert [p.text for p in result.paragraphs] == expected
    assert [p.index for p in result.paragraphs] == [0, 1, 2]
    assert tool.documents[result.doc_id].content == "\n\n".join(expected)


@pytest.mark.parametrize("status", [403, 404])
def test_http_fetch_does_not_retry_client_errors(status):
    requests = []

    def respond(request):
        requests.append(request)
        return httpx.Response(status)

    with httpx.Client(transport=httpx.MockTransport(respond)) as client:
        tool = FetchTool(HttpFetcher(client))
        result = tool.fetch("https://docs.example/client-error")

    assert isinstance(result, str)
    assert "HTTPStatusError" in result
    assert str(status) in result
    assert len(requests) == 1
    assert tool.documents == {}


@pytest.mark.parametrize("error", [ValueError("invalid HTML")])
def test_fetch_does_not_retry_extraction_errors(error):
    url = "https://docs.example/extraction-error"
    fetcher = FakeFetcher(error)
    tool = FetchTool(fetcher)

    result = tool.fetch(url)

    assert isinstance(result, str)
    assert type(error).__name__ in result
    assert fetcher.calls == [url]
    assert tool.documents == {}


@pytest.mark.parametrize(
    ("content", "expected"),
    [
        ("가" * 299 + ". " + "나" * 699, ["가" * 299 + ". " + "나" * 699]),
        (
            "가" * 299 + ". " + "나" * 299 + ". " + "다" * 397 + ". 다음 문장.",
            ["가" * 299 + ". " + "나" * 299 + ". " + "다" * 397 + ".", "다음 문장."],
        ),
    ],
    ids=["exact-limit-with-earlier-sentence", "last-sentence-at-limit"],
)
def test_fetch_keeps_the_last_sentence_boundary_including_exactly_1000_characters(
    content, expected
):
    tool = FetchTool(FakeFetcher({"title": "문단 경계", "content": content}))

    result = tool.fetch("https://docs.example/boundary")

    assert not isinstance(result, str)
    assert [p.model_dump() for p in result.paragraphs] == [
        {"index": index, "text": text} for index, text in enumerate(expected)
    ]
    assert tool.documents[result.doc_id].content == content


def test_http_fetch_follows_redirect_with_finite_timeouts_and_preserves_an_untitled_body():
    original_url = "https://docs.example/old"
    final_url = "https://docs.example/article"
    body = "메시지 전달 지연과 장애 복구 경로를 설계한다. " * 10
    html = f"<html><body><article><p>{body}</p></article></body></html>"
    requests = []

    def respond(request):
        requests.append(request)
        if str(request.url) == original_url:
            return httpx.Response(302, headers={"Location": "/article"})
        return httpx.Response(200, text=html)

    with httpx.Client(
        transport=httpx.MockTransport(respond), follow_redirects=False, timeout=None
    ) as client:
        tool = FetchTool(HttpFetcher(client))
        result = tool.fetch(original_url)

    assert not isinstance(result, str)
    assert [str(request.url) for request in requests] == [original_url, final_url]
    for request in requests:
        assert all(
            isinstance(value, (int, float)) and 0 < value < float("inf")
            for value in request.extensions["timeout"].values()
        )
    assert result.title == ""
    assert [p.model_dump() for p in result.paragraphs] == [
        {"index": 0, "text": body.strip()}
    ]
    assert tool.documents[result.doc_id].model_dump() == {
        "id": result.doc_id,
        "url": original_url,
        "title": "",
        "content": body.strip(),
    }


def test_http_fetch_retries_status_500_and_stores_only_the_recovered_document():
    body = "메시지 전달 지연과 장애 복구 경로를 설계한다. " * 10
    html = f"<html><head><title>복구된 문서</title></head><body><article><p>{body}</p></article></body></html>"
    requests = []

    def respond(request):
        requests.append(request)
        if len(requests) == 1:
            return httpx.Response(500, text="서버 오류 페이지")
        return httpx.Response(200, text=html)

    with httpx.Client(transport=httpx.MockTransport(respond)) as client:
        tool = FetchTool(HttpFetcher(client))
        result = tool.fetch("https://docs.example/recover")

    assert not isinstance(result, str)
    assert len(requests) == 2
    assert result.title == "복구된 문서"
    assert [p.model_dump() for p in result.paragraphs] == [
        {"index": 0, "text": body.strip()}
    ]
    assert list(tool.documents) == [result.doc_id]
    assert tool.documents[result.doc_id].content == body.strip()


def test_http_fetch_passes_the_final_response_url_to_the_extractor(monkeypatch):
    from archgen.retrieval import crawler

    original_url = "https://docs.example/old"
    final_url = "https://docs.example/article"
    body = "메시지 전달 지연과 장애 복구 경로를 설계한다. " * 10
    html = f"<html><body><article><p>{body}</p></article></body></html>"
    extraction_urls = []
    extract = crawler.bare_extraction

    def record_extraction(*args, **kwargs):
        extraction_urls.append(kwargs.get("url"))
        return extract(*args, **kwargs)

    def respond(request):
        if str(request.url) == original_url:
            return httpx.Response(302, headers={"Location": "/article"})
        return httpx.Response(200, text=html)

    monkeypatch.setattr(crawler, "bare_extraction", record_extraction)
    with httpx.Client(transport=httpx.MockTransport(respond)) as client:
        tool = FetchTool(HttpFetcher(client))
        result = tool.fetch(original_url)

    assert extraction_urls == [final_url]
    assert not isinstance(result, str)
    assert result.url == original_url
    assert tool.documents[result.doc_id].url == original_url
    assert tool.documents[result.doc_id].content == body.strip()
