import json

import pytest

from archgen.domain.research import FetchResult, Paragraph
from archgen.research.keep import KeepTool


def register_document(tool, doc_id="doc-a", query_id="query-latency"):
    result = FetchResult(
        doc_id=doc_id,
        url=f"https://docs.example/{doc_id}",
        title="채팅 설계",
        paragraphs=[
            Paragraph(index=0, text="소개 원문"),
            Paragraph(index=1, text="메시지 지연 p99는 100ms 이하이다."),
            Paragraph(index=2, text="제외할 원문"),
            Paragraph(
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
def test_keep_stores_selected_original_paragraphs_in_document_order(indices):
    tool = KeepTool()
    fetched, _ = register_document(tool)

    count = tool.keep(fetched.doc_id, indices)

    assert count == "1"
    assert tool.documents[fetched.doc_id].model_dump() == {
        "id": fetched.doc_id,
        "url": fetched.url,
        "title": fetched.title,
        "content": fetched.paragraphs[1].text + "\n\n" + fetched.paragraphs[3].text,
    }


def test_keep_counts_documents_only_for_their_first_query():
    tool = KeepTool()
    register_document(tool, "doc-a", "query-latency")
    register_document(tool, "doc-b", "query-availability")
    register_document(tool, "doc-c", "query-latency")
    register_document(tool, "doc-a", "query-availability")

    assert tool.keep("doc-a", [1]) == "1"
    assert tool.keep("doc-b", [3]) == "1"
    assert tool.keep("doc-c", [1]) == "2"
    assert tool.keep("doc-a", [3]) == "2"
    assert tool.keep("doc-b", [1]) == "1"


def test_keep_reduces_only_the_selected_documents_fetch_messages():
    tool = KeepTool()
    fetched, message = register_document(tool)
    _, repeated_message = register_document(tool)
    _, other_message = register_document(tool, "doc-b")
    other_before = dict(other_message)

    assert tool.keep(fetched.doc_id, [3, 1]) == "1"

    expected = fetched.model_dump()
    expected["paragraphs"] = [
        p.model_dump() for p in fetched.paragraphs if p.index in [1, 3]
    ]
    for item in [message, repeated_message]:
        assert item["role"] == "tool"
        assert item["tool_call_id"] == "fetch-doc-a"
        assert json.loads(item["content"]) == expected
    assert other_message == other_before
    assert [p.index for p in fetched.paragraphs] == [0, 1, 2, 3]


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
    assert tool.keep("doc-a", [3]) == "1"
    document_before = tool.documents["doc-a"].model_dump()
    message_before = dict(message)

    error = tool.keep(doc_id, indices)

    assert isinstance(error, str)
    assert "오류" in error
    assert list(tool.documents) == ["doc-a"]
    assert tool.documents["doc-a"].model_dump() == document_before
    assert message == message_before


def test_keep_accumulates_unique_paragraphs_in_document_order_without_recounting():
    tool = KeepTool()
    fetched, message = register_document(tool)

    assert tool.keep(fetched.doc_id, [3, 1, 1]) == "1"
    assert tool.documents[fetched.doc_id].content == (
        fetched.paragraphs[1].text + "\n\n" + fetched.paragraphs[3].text
    )
    assert [p["index"] for p in json.loads(message["content"])["paragraphs"]] == [1, 3]

    assert tool.keep(fetched.doc_id, [1, 0]) == "1"
    assert list(tool.documents) == [fetched.doc_id]
    assert tool.documents[fetched.doc_id].content == "\n\n".join(
        fetched.paragraphs[index].text for index in [0, 1, 3]
    )
    assert json.loads(message["content"])["paragraphs"] == [
        fetched.paragraphs[index].model_dump() for index in [0, 1, 3]
    ]


def test_keep_keeps_paragraph_selections_separate_for_each_document():
    tool = KeepTool()
    first, first_message = register_document(tool, "doc-a")
    second, second_message = register_document(tool, "doc-b")

    assert tool.keep(first.doc_id, [1]) == "1"
    assert tool.keep(second.doc_id, [3]) == "2"
    assert tool.documents[first.doc_id].content == first.paragraphs[1].text
    assert tool.documents[second.doc_id].content == second.paragraphs[3].text
    assert [p["index"] for p in json.loads(first_message["content"])["paragraphs"]] == [1]
    assert [p["index"] for p in json.loads(second_message["content"])["paragraphs"]] == [
        3
    ]

    assert tool.keep(first.doc_id, [0]) == "2"
    assert tool.keep(second.doc_id, [0, 1, 2, 3]) == "2"
    assert tool.documents[first.doc_id].content == "\n\n".join(
        first.paragraphs[index].text for index in [0, 1]
    )
    assert tool.documents[second.doc_id].content == "\n\n".join(
        paragraph.text for paragraph in second.paragraphs
    )
    assert [p["index"] for p in json.loads(first_message["content"])["paragraphs"]] == [
        0,
        1,
    ]
    assert json.loads(second_message["content"])["paragraphs"] == [
        paragraph.model_dump() for paragraph in second.paragraphs
    ]
