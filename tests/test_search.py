import pytest

from archgen.retrieval.search import SearchTool


class FakeTavily:
    def __init__(self, *responses: dict | Exception) -> None:
        self.responses = list(responses)
        self.calls: list[dict] = []

    def search(self, **kwargs) -> dict:
        self.calls.append(kwargs)
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def test_search_passes_query_unchanged_to_tavily() -> None:
    client = FakeTavily({"results": []})
    search = SearchTool(client)
    query = "  실시간 Chat 서비스 API latency SLA \n"

    search.search(query, query_id="query-topic")

    assert len(client.calls) == 1
    assert client.calls[0]["query"] == query


@pytest.mark.parametrize("query_id", ["query-topic", "query-latency"])
def test_search_returns_metadata_and_ranks_in_tavily_order(query_id: str) -> None:
    client = FakeTavily(
        {
            "results": [
                {"url": "https://blog.example/Chat", "title": "Chat 설계", "score": 0.2},
                {"url": "https://docs.example/api", "title": "API 문서", "score": 0.9},
                {"url": "https://paper.example/a", "title": "논문", "score": 0.5},
            ]
        }
    )

    results = SearchTool(client).search("chat architecture", query_id=query_id)

    assert not isinstance(results, str)
    assert [result.model_dump() for result in results] == [
        {
            "query_id": query_id,
            "url": "https://blog.example/Chat",
            "title": "Chat 설계",
            "rank": 1,
        },
        {
            "query_id": query_id,
            "url": "https://docs.example/api",
            "title": "API 문서",
            "rank": 2,
        },
        {
            "query_id": query_id,
            "url": "https://paper.example/a",
            "title": "논문",
            "rank": 3,
        },
    ]


@pytest.mark.parametrize("count", [0, 1, 9, 10, 11, 15])
def test_search_returns_at_most_first_ten_results(count: int) -> None:
    client = FakeTavily(
        {
            "results": [
                {"url": f"https://example.com/{index}", "title": f"문서 {index}"}
                for index in range(count)
            ]
        }
    )

    results = SearchTool(client).search("chat architecture", query_id="query-topic")

    assert not isinstance(results, str)
    assert [result.url for result in results] == [
        f"https://example.com/{index}" for index in range(min(count, 10))
    ]
    assert [result.rank for result in results] == list(range(1, min(count, 10) + 1))
    assert client.calls[0]["max_results"] == 10


def test_search_removes_duplicate_urls_within_and_across_queries() -> None:
    client = FakeTavily(
        {
            "results": [
                {"url": "https://example.com/a", "title": "첫 A"},
                {"url": "https://example.com/a", "title": "중복 A"},
                {"url": "https://example.com/b", "title": "첫 B"},
            ]
        },
        {
            "results": [
                {"url": "https://example.com/b", "title": "이미 나온 B"},
                {"url": "https://example.com/c", "title": "첫 C"},
                {"url": "https://example.com/c", "title": "중복 C"},
                {"url": "https://example.com/a", "title": "이미 나온 A"},
                {"url": "https://example.com/d", "title": "첫 D"},
            ]
        },
    )
    search = SearchTool(client)

    first = search.search("chat overview", query_id="query-topic")
    second = search.search("chat latency", query_id="query-latency")

    assert not isinstance(first, str)
    assert not isinstance(second, str)
    assert [result.model_dump() for result in first] == [
        {
            "query_id": "query-topic",
            "url": "https://example.com/a",
            "title": "첫 A",
            "rank": 1,
        },
        {
            "query_id": "query-topic",
            "url": "https://example.com/b",
            "title": "첫 B",
            "rank": 2,
        },
    ]
    assert [result.model_dump() for result in second] == [
        {
            "query_id": "query-latency",
            "url": "https://example.com/c",
            "title": "첫 C",
            "rank": 1,
        },
        {
            "query_id": "query-latency",
            "url": "https://example.com/d",
            "title": "첫 D",
            "rank": 2,
        },
    ]


@pytest.mark.parametrize(
    "error",
    [
        TimeoutError("Tavily timeout"),
        ConnectionError("Tavily connection failed"),
        RuntimeError("429 rate limit"),
    ],
)
def test_search_returns_error_string_when_tavily_call_fails(error: Exception) -> None:
    client = FakeTavily(error)

    result = SearchTool(client).search("chat latency", query_id="query-latency")

    assert isinstance(result, str)
    assert "query-latency" in result
    assert type(error).__name__ in result
    assert str(error) in result
    assert len(client.calls) == 1


def test_search_keeps_tavily_order_when_official_documentation_is_last() -> None:
    urls = ["https://blog.example/chat", "https://docs.aws.amazon.com/chat"]
    client = FakeTavily({"results": [{"url": url, "title": "자료"} for url in urls]})

    results = SearchTool(client).search("chat", query_id="query-topic")

    assert not isinstance(results, str)
    assert [result.url for result in results] == urls
    assert [result.rank for result in results] == [1, 2]
