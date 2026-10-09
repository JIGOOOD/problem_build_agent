"""가져온 문서에서 선택한 근거 문장의 원문을 남긴다."""

from archgen.domain.research import MAX_KEEP_CHARS, Document, FetchResult


class KeepTool:
    def __init__(self) -> None:
        self.documents: dict[str, Document] = {}  # 최종 문서
        self._fetched: dict[str, FetchResult] = {}  # 원문
        self._queries: dict[str, str] = {}
        self._messages: dict[str, list[dict[str, str]]] = {}
        self._selected: dict[str, list[int]] = {}

    def register(
        self, query_id: str, result: FetchResult, message: dict[str, str]
    ) -> None:
        self._fetched.setdefault(result.doc_id, result)
        self._queries.setdefault(result.doc_id, query_id)
        self._messages.setdefault(result.doc_id, []).append(message)

    def keep(self, doc_id: str, sentence_indices: list[int]) -> dict | str:
        if doc_id not in self._fetched:
            return f"keep[{doc_id}] 오류: 없는 문서 ID다."
        if not sentence_indices:
            return f"keep[{doc_id}] 오류: 문장 번호 목록이 비어 있다."
        result = self._fetched[doc_id]
        available = {s.index: s for s in result.sentences}
        if any(
            type(index) is not int or index not in available for index in sentence_indices
        ):
            return f"keep[{doc_id}] 오류: 범위 밖 문장 번호가 있다."
        selected_indices, skipped_indices = [], []
        used = 0
        for index in dict.fromkeys([*self._selected.get(doc_id, []), *sentence_indices]):
            size = len(available[index].text) + (2 if selected_indices else 0)
            if used + size > MAX_KEEP_CHARS:
                skipped_indices.append(index)
                continue
            selected_indices.append(index)
            used += size
        self._selected[doc_id] = selected_indices
        sentences = [available[index] for index in sorted(selected_indices)]
        if sentences:
            self.documents[doc_id] = Document(
                id=doc_id,
                url=result.url,
                title=result.title,
                content="\n\n".join(s.text for s in sentences),
            )
        else:
            self.documents.pop(doc_id, None)
        selected = result.model_copy(update={"sentences": sentences})
        for message in self._messages[doc_id]:
            message["content"] = selected.model_dump_json()
        query_id = self._queries[doc_id]
        return {
            "selected_indices": sorted(selected_indices),
            "skipped_indices": skipped_indices,
            "content_chars": used,
            "kept_documents": sum(
                self._queries[kept] == query_id for kept in self.documents
            ),
        }

    def finish_batch(self, doc_ids: list[str]) -> None:
        for doc_id in doc_ids:
            if doc_id not in self.documents:
                for message in self._messages[doc_id]:
                    message["content"] = "버림"
