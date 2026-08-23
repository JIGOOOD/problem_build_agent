import pytest

from archgen.core.graph import build_generation_graph, new_thread_config


@pytest.mark.asyncio
async def test_generation_graph_runs_all_scaffold_stages() -> None:
    graph = build_generation_graph()

    result = await graph.ainvoke(
        {"brief": ["Design a ticketing service"], "events": []},
        config=new_thread_config(),
    )

    assert result["status"] == "ready_for_agents"
    assert result["phase"] == "finalize"
    assert result["events"] == [
        "intake: brief accepted",
        "research: agent not configured",
        "author: agent not configured",
        "validate: harness not configured",
        "finalize: workflow scaffold completed",
    ]
