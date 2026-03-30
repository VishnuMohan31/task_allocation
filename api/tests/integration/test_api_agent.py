"""Tests for the agent decision HTTP endpoint.

Covers:
  - GET /agent/decision: returns 200 with correct shape
  - GET /agent/decision: response has required fields
  - GET /agent/decision: productivity_score is always in [0.0, 1.0]
  - GET /agent/decision: suggestion is always a non-empty string

Uses FastAPI TestClient with the agent service mocked so no real OpenAI calls are made.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from models.agent import AgentDecision


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _mock_decide(next_task=None, score=0.0, suggestion="No tasks yet.", reasoning="Mock reasoning."):
    """Return a callable that returns a fixed AgentDecision."""
    decision = AgentDecision(
        next_task=next_task,
        productivity_score=score,
        suggestion=suggestion,
        reasoning=reasoning,
    )
    return MagicMock(return_value=decision)


# ---------------------------------------------------------------------------
# GET /agent/decision — response shape
# ---------------------------------------------------------------------------


class TestAgentDecisionShape:
    """Tests for response structure."""

    def test_returns_200(self, client, mock_pool):
        with patch("app.api.agent.decide", _mock_decide()):
            response = client.get("/agent/decision")
        assert response.status_code == 200

    def test_response_has_next_task_field(self, client, mock_pool):
        with patch("app.api.agent.decide", _mock_decide()):
            response = client.get("/agent/decision")
        assert "next_task" in response.json()

    def test_response_has_productivity_score_field(self, client, mock_pool):
        with patch("app.api.agent.decide", _mock_decide()):
            response = client.get("/agent/decision")
        assert "productivity_score" in response.json()

    def test_response_has_suggestion_field(self, client, mock_pool):
        with patch("app.api.agent.decide", _mock_decide()):
            response = client.get("/agent/decision")
        assert "suggestion" in response.json()

    def test_response_has_reasoning_field(self, client, mock_pool):
        with patch("app.api.agent.decide", _mock_decide()):
            response = client.get("/agent/decision")
        assert "reasoning" in response.json()

    def test_reasoning_is_non_empty_string(self, client, mock_pool):
        with patch("app.api.agent.decide", _mock_decide(reasoning="Some reasoning.")):
            response = client.get("/agent/decision")
        data = response.json()
        assert isinstance(data["reasoning"], str)
        assert data["reasoning"].strip() != ""

    def test_suggestion_is_non_empty_string(self, client, mock_pool):
        with patch("app.api.agent.decide", _mock_decide(suggestion="Do something.")):
            response = client.get("/agent/decision")
        data = response.json()
        assert isinstance(data["suggestion"], str)
        assert data["suggestion"].strip() != ""

    def test_productivity_score_is_float(self, client, mock_pool):
        with patch("app.api.agent.decide", _mock_decide(score=0.5)):
            response = client.get("/agent/decision")
        score = response.json()["productivity_score"]
        assert isinstance(score, (int, float))

    def test_productivity_score_in_unit_interval(self, client, mock_pool):
        with patch("app.api.agent.decide", _mock_decide(score=0.75)):
            response = client.get("/agent/decision")
        score = response.json()["productivity_score"]
        assert 0.0 <= score <= 1.0


# ---------------------------------------------------------------------------
# GET /agent/decision — empty tasks (current behavior: decide([]) called)
# ---------------------------------------------------------------------------


class TestAgentDecisionEmptyTasks:
    """Tests when decide is called with no tasks."""

    def test_no_tasks_next_task_is_null(self, client, mock_pool):
        with patch("app.api.agent.decide", _mock_decide(next_task=None)):
            response = client.get("/agent/decision")
        assert response.json()["next_task"] is None

    def test_no_tasks_score_is_zero(self, client, mock_pool):
        with patch("app.api.agent.decide", _mock_decide(score=0.0)):
            response = client.get("/agent/decision")
        assert response.json()["productivity_score"] == 0.0

    def test_no_tasks_suggestion_is_non_empty(self, client, mock_pool):
        with patch("app.api.agent.decide", _mock_decide(suggestion="Add some tasks.")):
            response = client.get("/agent/decision")
        assert response.json()["suggestion"].strip() != ""
