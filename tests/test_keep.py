import json

import pytest

from archgen.domain.research import FetchResult, Sentence
from archgen.research.keep import KeepTool


def test_keep_fills_2000_chars_by_priority_skipping_whole_sentences():
    tool = KeepTool()
    fetched = FetchResult(
        doc_id="doc-budget",
        url="https://docs.example/budget",
        title="설계",
        sentences=[
            Sentence(index=0, text="가" * 198),
            Sentence(index=1, text="나" * 300),
            Sentence(index=2, text="다" * 1800),
        ],
    )
    message = {
        "role": "tool",
        "tool_call_id": "fetch-budget",
        "content": fetched.model_dump_json(),
    }
    tool.register("query-1", fetched, message)

    result = tool.keep(fetched.doc_id, [2, 1, 0, 2])

    assert result == {
        "selected_indices": [0, 2],
        "skipped_indices": [1],
        "content_chars": 2000,
        "kept_documents": 1,
    }
    assert tool.documents[fetched.doc_id].content == "가" * 198 + "\n\n" + "다" * 1800
    assert [s["index"] for s in json.loads(message["content"])["sentences"]] == [0, 2]


@pytest.mark.parametrize("new_length", [1, 2001])
def test_keep_preserves_previous_selection_when_new_sentence_exceeds_budget(new_length):
    tool = KeepTool()
    fetched = FetchResult(
        doc_id="doc-long",
        url="https://docs.example/long",
        title="긴 문장",
        sentences=[
            Sentence(index=0, text="가" * 2000),
            Sentence(index=1, text="나" * new_length),
        ],
    )
    message = {
        "role": "tool",
        "tool_call_id": "fetch-long",
        "content": fetched.model_dump_json(),
    }
    tool.register("query-1", fetched, message)
    assert tool.keep(fetched.doc_id, [0])["content_chars"] == 2000

    result = tool.keep(fetched.doc_id, [1])

    assert result == {
        "selected_indices": [0],
        "skipped_indices": [1],
        "content_chars": 2000,
        "kept_documents": 1,
    }
    assert tool.documents[fetched.doc_id].content == "가" * 2000
    assert json.loads(message["content"])["sentences"] == [
        fetched.sentences[0].model_dump()
    ]


def register_document(tool, doc_id="doc-a", query_id="query-latency"):
    result = FetchResult(
        doc_id=doc_id,
        url=f"https://docs.example/{doc_id}",
        title="채팅 설계",
        sentences=[
            Sentence(index=0, text="소개 원문"),
            Sentence(index=1, text="메시지 지연 p99는 100ms 이하이다."),
            Sentence(index=2, text="제외할 원문"),
            Sentence(
                index=3, text="복제를 늘리면 가용성과 쓰기 지연 사이 trade-off가 생긴다."
            ),
        ],
    )
    message = {
        "role": "tool",
        "tool_call_id": f"fetch-{doc_id}",
        "content": result.model_dump_json(),
    }
    tool.register(query_id, result, message)
    return result, message


@pytest.mark.parametrize("indices", [[1, 3], [3, 1]])
def test_keep_stores_selected_original_sentences_in_document_order(indices):
    tool = KeepTool()
    fetched, _ = register_document(tool)

    count = tool.keep(fetched.doc_id, indices)

    assert count["kept_documents"] == 1
    assert tool.documents[fetched.doc_id].model_dump() == {
        "id": fetched.doc_id,
        "url": fetched.url,
        "title": fetched.title,
        "content": fetched.sentences[1].text + "\n\n" + fetched.sentences[3].text,
    }


def test_keep_counts_documents_only_for_their_first_query():
    tool = KeepTool()
    register_document(tool, "doc-a", "query-latency")
    register_document(tool, "doc-b", "query-availability")
    register_document(tool, "doc-c", "query-latency")
    register_document(tool, "doc-a", "query-availability")

    assert tool.keep("doc-a", [1])["kept_documents"] == 1
    assert tool.keep("doc-b", [3])["kept_documents"] == 1
    assert tool.keep("doc-c", [1])["kept_documents"] == 2
    assert tool.keep("doc-a", [3])["kept_documents"] == 2
    assert tool.keep("doc-b", [1])["kept_documents"] == 1


def test_keep_reduces_only_the_selected_documents_fetch_messages():
    tool = KeepTool()
    fetched, message = register_document(tool)
    _, repeated_message = register_document(tool)
    _, other_message = register_document(tool, "doc-b")
    other_before = dict(other_message)

    assert tool.keep(fetched.doc_id, [3, 1])["kept_documents"] == 1

    expected = fetched.model_dump()
    expected["sentences"] = [
        p.model_dump() for p in fetched.sentences if p.index in [1, 3]
    ]
    for item in [message, repeated_message]:
        assert item["role"] == "tool"
        assert item["tool_call_id"] == "fetch-doc-a"
        assert json.loads(item["content"]) == expected
    assert other_message == other_before
    assert [p.index for p in fetched.sentences] == [0, 1, 2, 3]


def test_finish_batch_marks_only_unkept_documents_in_that_batch_as_discarded():
    tool = KeepTool()
    _, kept_message = register_document(tool, "doc-a")
    _, discarded_message = register_document(tool, "doc-b")
    _, other_batch_message = register_document(tool, "doc-c")
    original_discarded = dict(discarded_message)
    original_other = dict(other_batch_message)
    tool.keep("doc-a", [1])
    selected_message = dict(kept_message)
    assert discarded_message == original_discarded

    tool.finish_batch(["doc-a", "doc-b"])

    assert kept_message == selected_message
    assert discarded_message == {**original_discarded, "content": "버림"}
    assert other_batch_message == original_other
    assert list(tool.documents) == ["doc-a"]


@pytest.mark.parametrize(
    ("doc_id", "indices"),
    [("missing", [1]), ("doc-a", [1, 4]), ("doc-a", [])],
    ids=["unknown-document", "out-of-range", "empty-selection"],
)
def test_keep_returns_an_error_without_changing_state_for_invalid_input(doc_id, indices):
    tool = KeepTool()
    _, message = register_document(tool)
    assert tool.keep("doc-a", [3])["kept_documents"] == 1
    document_before = tool.documents["doc-a"].model_dump()
    message_before = dict(message)

    error = tool.keep(doc_id, indices)

    assert isinstance(error, str)
    assert "오류" in error
    assert list(tool.documents) == ["doc-a"]
    assert tool.documents["doc-a"].model_dump() == document_before
    assert message == message_before


def test_keep_accumulates_new_sentences_without_duplicates_or_recounting():
    tool = KeepTool()
    fetched, message = register_document(tool)
    assert tool.keep(fetched.doc_id, [3, 1])["selected_indices"] == [1, 3]

    result = tool.keep(fetched.doc_id, [0, 3, 0])
    expected_content = "\n\n".join(fetched.sentences[i].text for i in [0, 1, 3])

    assert result == {
        "selected_indices": [0, 1, 3],
        "skipped_indices": [],
        "content_chars": len(expected_content),
        "kept_documents": 1,
    }
    assert list(tool.documents) == [fetched.doc_id]
    assert tool.documents[fetched.doc_id].content == expected_content
    assert json.loads(message["content"])["sentences"] == [
        fetched.sentences[i].model_dump() for i in [0, 1, 3]
    ]


def test_keep_keeps_sentence_selections_separate_for_each_document():
    tool = KeepTool()
    first, first_message = register_document(tool, "doc-a")
    second, second_message = register_document(tool, "doc-b")

    assert tool.keep(first.doc_id, [1])["kept_documents"] == 1
    assert tool.keep(second.doc_id, [3])["kept_documents"] == 2
    assert tool.documents[first.doc_id].content == first.sentences[1].text
    assert tool.documents[second.doc_id].content == second.sentences[3].text
    assert [p["index"] for p in json.loads(first_message["content"])["sentences"]] == [1]
    assert [p["index"] for p in json.loads(second_message["content"])["sentences"]] == [3]

    assert tool.keep(first.doc_id, [0])["kept_documents"] == 2
    assert tool.keep(second.doc_id, [0, 1, 2, 3])["kept_documents"] == 2
    assert tool.documents[first.doc_id].content == "\n\n".join(
        first.sentences[index].text for index in [0, 1]
    )
    assert tool.documents[second.doc_id].content == "\n\n".join(
        sentence.text for sentence in second.sentences
    )
    assert [p["index"] for p in json.loads(first_message["content"])["sentences"]] == [
        0,
        1,
    ]
    assert json.loads(second_message["content"])["sentences"] == [
        sentence.model_dump() for sentence in second.sentences
    ]


def test_keep_and_discard_update_only_their_document_in_a_fetch_batch():
    tool = KeepTool()
    first, _ = register_document(tool, "doc-a")
    second, _ = register_document(tool, "doc-b")
    message = {
        "role": "tool",
        "tool_call_id": "fetch-batch",
        "content": json.dumps(
            [
                {"url": doc.url, "rank": rank, "result": doc.model_dump()}
                for rank, doc in enumerate([first, second], start=1)
            ]
        ),
    }
    for doc in [first, second]:
        tool.register("query-latency", doc, message)

    tool.keep("doc-a", [3, 1])
    payload = json.loads(message["content"])
    assert payload[0]["result"]["sentences"] == [
        first.sentences[i].model_dump() for i in [1, 3]
    ]
    assert payload[1]["result"] == second.model_dump()

    tool.finish_batch(["doc-a", "doc-b"])
    tool.keep("doc-a", [0])
    payload = json.loads(message["content"])
    assert payload[0]["result"]["sentences"] == [
        first.sentences[i].model_dump() for i in [0, 1, 3]
    ]
    assert payload[1] == {
        "url": second.url,
        "rank": 2,
        "result": {"doc_id": "doc-b", "status": "버림"},
    }


def test_keep_does_not_store_a_document_when_every_selected_sentence_exceeds_budget():
    tool = KeepTool()
    fetched = FetchResult(
        doc_id="doc-oversize",
        url="https://docs.example/oversize",
        title="긴 문장",
        sentences=[Sentence(index=0, text="가" * 2001)],
    )
    message = {"role": "tool", "content": fetched.model_dump_json()}
    tool.register("query-1", fetched, message)

    result = tool.keep(fetched.doc_id, [0])

    assert result == {
        "selected_indices": [],
        "skipped_indices": [0],
        "content_chars": 0,
        "kept_documents": 0,
    }
    assert tool.documents == {}
    assert json.loads(message["content"])["sentences"] == []
