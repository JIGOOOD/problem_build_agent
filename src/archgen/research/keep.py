"""가져온 문서에서 선택한 근거 문단의 원문을 남긴다."""

from archgen.domain.research import Document, FetchResult


class KeepTool:
    def __init__(self) -> None:
        self.documents: dict[str, Document] = {}
        self._fetched: dict[str, FetchResult] = {}
        self._queries: dict[str, str] = {}
        self._messages: dict[str, list[dict[str, str]]] = {}
        self._selected_indices: dict[str, set[int]] = {}

    def register(
        self, query_id: str, result: FetchResult, message: dict[str, str]
    ) -> None:
        self._fetched.setdefault(result.doc_id, result)
        self._queries.setdefault(result.doc_id, query_id)
        self._messages.setdefault(result.doc_id, []).append(message)

    def keep(self, doc_id: str, paragraph_indices: list[int]) -> str:
        if doc_id not in self._fetched:
            return f"keep[{doc_id}] 오류: 없는 문서 ID다."
        if not paragraph_indices:
            return f"keep[{doc_id}] 오류: 문단 번호 목록이 비어 있다."
        result = self._fetched[doc_id]
        available = {p.index for p in result.paragraphs}
        if not set(paragraph_indices) <= available:
            return f"keep[{doc_id}] 오류: 범위 밖 문단 번호가 있다."
        selected_indices = self._selected_indices.setdefault(doc_id, set())
        selected_indices.update(paragraph_indices)
        paragraphs = [p for p in result.paragraphs if p.index in selected_indices]
        self.documents[doc_id] = Document(
            id=doc_id,
            url=result.url,
            title=result.title,
            content="\n\n".join(p.text for p in paragraphs),
        )
        selected = result.model_copy(update={"paragraphs": paragraphs})
        for message in self._messages[doc_id]:
            message["content"] = selected.model_dump_json()
        query_id = self._queries[doc_id]
        return str(sum(self._queries[kept] == query_id for kept in self.documents))

    def finish_batch(self, doc_ids: list[str]) -> None:
        for doc_id in doc_ids:
            if doc_id not in self.documents:
                for message in self._messages[doc_id]:
                    message["content"] = "버림"
