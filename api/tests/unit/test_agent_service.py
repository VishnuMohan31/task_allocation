"""
Tests for services/agent_service.py — LangChain agent.
The AgentExecutor is mocked so no real OpenAI calls are made in CI.
"""
from __future__ import annotations

import json
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from models.agent import AgentDecision
from models.task import Task


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_task(
    title: str = "Task",
    priority: int = 3,
    completed: bool = False,
    created_at: datetime | None = None,
) -> Task:
    return Task(
        title=title,
        description="",
        priority=priority,
        completed=completed,
        created_at=created_at or datetime.utcnow(),
    )


def _mock_agent(next_task_id: str | None, score: float, suggestion: str, reasoning: str = "Mock reasoning."):
    """Return a mock LangGraph agent that outputs a fixed JSON decision."""
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


# ---------------------------------------------------------------------------
# decide()
# ---------------------------------------------------------------------------

class TestDecide:
    def test_returns_agent_decision_instance(self):
        from services.agent_service import decide
        task = make_task(title="Do something", priority=3)
        with patch("services.agent_service._build_agent", return_value=_mock_agent(
            task.id, 0.0, "Low productivity score. Prioritize: Do something"
        )):
            result = decide([task])
        assert isinstance(result, AgentDecision)

    def test_empty_tasks_returns_null_next_task(self):
        from services.agent_service import decide
        with patch("services.agent_service._build_agent", return_value=_mock_agent(
            None, 0.0, "No tasks yet. Add some tasks to get started."
        )):
            result = decide([])
        assert result.next_task is None
        assert result.productivity_score == 0.0
        assert result.suggestion != ""

    def test_next_task_resolved_from_id(self):
        from services.agent_service import decide
        task = make_task(title="High priority", priority=5)
        with patch("services.agent_service._build_agent", return_value=_mock_agent(
            task.id, 0.0, "Prioritize: High priority"
        )):
            result = decide([task])
        assert result.next_task is not None
        assert result.next_task.id == task.id

    def test_unknown_task_id_resolves_to_none(self):
        from services.agent_service import decide
        task = make_task(title="Some task")
        with patch("services.agent_service._build_agent", return_value=_mock_agent(
            "non-existent-id", 0.5, "Keep going"
        )):
            result = decide([task])
        assert result.next_task is None

    def test_productivity_score_passed_through(self):
        from services.agent_service import decide
        task = make_task(completed=True, priority=4)
        with patch("services.agent_service._build_agent", return_value=_mock_agent(
            None, 1.0, "All done!"
        )):
            result = decide([task])
        assert result.productivity_score == 1.0

    def test_suggestion_passed_through(self):
        from services.agent_service import decide
        task = make_task(title="Write tests")
        with patch("services.agent_service._build_agent", return_value=_mock_agent(
            task.id, 0.3, "Low productivity score. Prioritize: Write tests"
        )):
            result = decide([task])
        assert result.suggestion == "Low productivity score. Prioritize: Write tests"

    def test_all_fields_populated(self):
        from services.agent_service import decide
        task = make_task(title="Deploy", priority=5)
        with patch("services.agent_service._build_agent", return_value=_mock_agent(
            task.id, 0.75, "Good pace. Next up: Deploy", "High priority task selected."
        )):
            result = decide([task])
        assert result.next_task is not None
        assert isinstance(result.productivity_score, float)
        assert result.suggestion != ""
        assert result.reasoning != ""
