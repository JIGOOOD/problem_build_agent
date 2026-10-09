"""Tavily 검색을 Research Agent에서 사용할 수 있게 연결한다."""

from threading import Lock
from typing import Any, Protocol

from archgen.domain.research import RESULTS_PER_QUERY, SearchResult


class SearchClient(Protocol):
    def search(self, *, query: str, max_results: int) -> dict[str, Any]: ...


class SearchTool:
    """조사 실행마다 새 인스턴스를 만들어 반환한 URL의 중복을 제거한다."""

    def __init__(self, client: SearchClient) -> None:
        self._client = client
        self._seen_urls: set[str] = set()
        self._lock = Lock()

    def search(self, query: str, *, query_id: str) -> list[SearchResult] | str:
        try:
            response = self._client.search(
                query=query,
                max_results=RESULTS_PER_QUERY,
            )
        except Exception as error:  # noqa: BLE001 — 외부 검색 실패는 오류 문자열로 반환한다.
            return f"search[{query_id}] 실패: {type(error).__name__}: {error}"
        with self._lock:
            return self._collect(response, query_id)

    """search 결과를 SearchResult로 변환"""

    def _collect(self, response: dict[str, Any], query_id: str) -> list[SearchResult]:
        results: list[SearchResult] = []
        for item in response["results"]:
            if item["url"] in self._seen_urls:
                continue
            results.append(
                SearchResult(
                    query_id=query_id,
                    url=item["url"],
                    title=item["title"],
                    rank=len(results) + 1,
                )
            )
            self._seen_urls.add(item["url"])
            if len(results) == RESULTS_PER_QUERY:
                break
        return results
