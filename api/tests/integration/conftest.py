"""Integration-test fixtures — mocks the LangChain agent so no real OpenAI calls are made."""
from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest


def _make_agent_mock(tasks):
    """Build a mock LangGraph agent that returns a deterministic JSON decision."""
    pending = [t for t in tasks if not t.completed]
    weighted_total = sum(t.priority for t in tasks)
    weighted_done = sum(t.priority for t in tasks if t.completed)
    score = round(weighted_done / weighted_total, 4) if weighted_total else 0.0

    if pending:
        best = sorted(pending, key=lambda t: (-t.priority, t.created_at))[0]
        next_task_id = best.id
        suggestion = f"Prioritize: {best.title}"
        reasoning = f"Selected '{best.title}' because it has the highest priority ({best.priority}) among pending tasks."
    else:
        next_task_id = None
        suggestion = "All tasks complete. Add new tasks to keep momentum."
        reasoning = "No pending tasks remain. All work is done."

    output = json.dumps({
        "next_task_id": next_task_id,
        "productivity_score": score,
        "suggestion": suggestion,
        "reasoning": reasoning,
    })
    msg = MagicMock()
    msg.content = output
    agent = MagicMock()
    agent.invoke.return_value = {"messages": [msg]}
    return agent


@pytest.fixture(autouse=True)
def mock_build_agent(tmp_repo):
    """Patch _build_agent for every integration test — reads tasks from tmp_repo to build response."""
    def _side_effect():
        tasks = tmp_repo.list_tasks()
        return _make_agent_mock(tasks)

    with patch("services.agent_service._build_agent", side_effect=_side_effect):
        yield
