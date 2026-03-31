"""
Tests for services/agent_service.py — LangChain agent.
The graph is mocked so no real OpenAI calls are made in CI.
"""
from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from models.agent import AgentDecision
from models.task import Task


def make_task(**kwargs) -> Task:
    defaults = {
        "id": "task-001",
        "user_story_id": "us-001",
        "name": "Task",
        "status": "Planning",
        "priority": "Medium",
    }
    defaults.update(kwargs)
    return Task(**defaults)


def _mock_service(tasks: list[Task]) -> MagicMock:
    svc = MagicMock()
    svc.list_tasks = AsyncMock(return_value=tasks)
    return svc


def _mock_agent(next_task_id: str | None, score: float, suggestion: str, reasoning: str = "Mock reasoning."):
    output = json.dumps({
        "next_task_id": next_task_id,
        "productivity_score": score,
        "suggestion": suggestion,
        "reasoning": reasoning,
    })
    msg = MagicMock()
    msg.content = output
    agent = MagicMock()
    agent.ainvoke = AsyncMock(return_value={"messages": [msg]})
    return agent


def _msg_with_content(content: str) -> MagicMock:
    m = MagicMock()
    m.content = content
    return m


def _mock_agent_sequence(contents: list[str]) -> MagicMock:
    agent = MagicMock()
    attempt = {"n": 0}

    async def ainvoke_side_effect(payload: dict):
        messages_in = list(payload["messages"])
        i = attempt["n"]
        attempt["n"] += 1
        content = contents[min(i, len(contents) - 1)]
        assistant = _msg_with_content(content)
        return {"messages": messages_in + [assistant]}

    agent.ainvoke.side_effect = ainvoke_side_effect
    return agent


@pytest.mark.asyncio
class TestDecide:
    async def test_returns_agent_decision_instance(self):
        from services.agent_service import decide

        task = make_task(name="Do something", id="task-abc")
        svc = _mock_service([task])
        with patch("services.agent_service._build_agent", return_value=_mock_agent(
            task.id, 0.0, "Low productivity score. Prioritize: Do something"
        )):
            result = await decide(svc)
        assert isinstance(result, AgentDecision)

    async def test_empty_tasks_returns_null_next_task(self):
        from services.agent_service import decide

        svc = _mock_service([])
        with patch("services.agent_service._build_agent", return_value=_mock_agent(
            None, 0.0, "No tasks yet. Add some tasks to get started."
        )):
            result = await decide(svc)
        assert result.next_task is None
        assert result.productivity_score == 0.0
        assert result.suggestion != ""

    async def test_next_task_resolved_from_id(self):
        from services.agent_service import decide

        task = make_task(name="High priority", id="task-high")
        svc = _mock_service([task])
        with patch("services.agent_service._build_agent", return_value=_mock_agent(
            task.id, 0.0, "Prioritize: High priority"
        )):
            result = await decide(svc)
        assert result.next_task is not None
        assert result.next_task.id == task.id

    async def test_unknown_task_id_resolves_to_none(self):
        from services.agent_service import decide

        task = make_task(name="Some task")
        svc = _mock_service([task])
        with patch("services.agent_service._build_agent", return_value=_mock_agent(
            "non-existent-id", 0.5, "Keep going"
        )):
            result = await decide(svc)
        assert result.next_task is None

    async def test_productivity_score_passed_through(self):
        from services.agent_service import decide

        task = make_task(id="task-done")
        svc = _mock_service([task])
        with patch("services.agent_service._build_agent", return_value=_mock_agent(
            None, 1.0, "All done!"
        )):
            result = await decide(svc)
        assert result.productivity_score == 1.0

    async def test_suggestion_passed_through(self):
        from services.agent_service import decide

        task = make_task(name="Write tests")
        svc = _mock_service([task])
        with patch("services.agent_service._build_agent", return_value=_mock_agent(
            task.id, 0.3, "Low productivity score. Prioritize: Write tests"
        )):
            result = await decide(svc)
        assert result.suggestion == "Low productivity score. Prioritize: Write tests"

    async def test_all_fields_populated(self):
        from services.agent_service import decide

        task = make_task(name="Deploy", id="task-deploy")
        svc = _mock_service([task])
        with patch("services.agent_service._build_agent", return_value=_mock_agent(
            task.id, 0.75, "Good pace. Next up: Deploy", "High priority task selected."
        )):
            result = await decide(svc)
        assert result.next_task is not None
        assert isinstance(result.productivity_score, float)
        assert result.suggestion != ""
        assert result.reasoning != ""

    async def test_retry_succeeds_after_invalid_first_response(self):
        from services.agent_service import decide

        task = make_task(name="Fix bug", id="task-fix")
        svc = _mock_service([task])
        valid = json.dumps({
            "next_task_id": task.id,
            "productivity_score": 0.5,
            "suggestion": "Work on Fix bug next.",
            "reasoning": "Second attempt valid.",
        })
        agent = _mock_agent_sequence(["not valid json {{{", valid])
        with patch("services.agent_service._build_agent", return_value=agent):
            result = await decide(svc)
        assert agent.ainvoke.call_count == 2
        assert result.next_task is not None
        assert result.next_task.id == task.id
        assert result.productivity_score == 0.5

    async def test_fallback_after_two_failed_validations(self):
        from services.agent_service import decide

        task = make_task()
        svc = _mock_service([task])
        agent = _mock_agent_sequence(["not json", "still not json"])
        with patch("services.agent_service._build_agent", return_value=agent):
            result = await decide(svc)
        assert agent.ainvoke.call_count == 2
        assert result.next_task is None
        assert result.productivity_score == 0.0
        assert "fallback" in result.suggestion.lower()
        assert "Validation failed after retry" in result.reasoning

    async def test_retry_injects_standard_feedback_message(self):
        from services.agent_service import decide

        task = make_task()
        svc = _mock_service([task])
        valid = json.dumps({
            "next_task_id": None,
            "productivity_score": 0.0,
            "suggestion": "Ok.",
            "reasoning": "r",
        })
        agent = _mock_agent_sequence(['{"productivity_score": 2.0, "suggestion": "bad score"}', valid])
        with patch("services.agent_service._build_agent", return_value=agent):
            await decide(svc)
        assert agent.ainvoke.call_count == 2
        second_call_messages = agent.ainvoke.call_args_list[1][0][0]["messages"]
        feedback_texts = [
            getattr(m, "content", "") or (m.get("content", "") if isinstance(m, dict) else "")
            for m in second_call_messages
        ]
        assert any(
            "Your previous response was invalid because:" in t and "Fix and retry." in t
            for t in feedback_texts
        )


@pytest.mark.asyncio
class TestGetTasksTool:
    async def test_empty_db_returns_no_pending_message(self):
        from core.config import settings
        from services.agent_service import make_agent_tools

        svc = MagicMock()
        svc.list_tasks = AsyncMock(return_value=[])
        tools = make_agent_tools(svc)
        out = await tools[0].ainvoke({})
        assert out == settings.agent_no_pending_message

    async def test_returns_serialized_rows(self):
        from services.agent_service import make_agent_tools

        task = make_task(id="t1", name="Do work")
        svc = MagicMock()
        svc.list_tasks = AsyncMock(return_value=[task])
        tools = make_agent_tools(svc)
        out = await tools[0].ainvoke({})
        data = json.loads(out)
        assert len(data) == 1
        assert data[0]["id"] == "t1"
        assert data[0]["name"] == "Do work"


def test_get_current_date_context_returns_iso_and_weekday():
    from services.agent_service import get_current_date_context

    data = json.loads(get_current_date_context.invoke({}))
    assert "date_iso" in data and "weekday" in data
    assert len(data["date_iso"]) == 10
