from datetime import datetime

import pytest

from models.agent import AgentDecision, AgentDecisionResponse
from models.task import Task


def make_task(**kwargs) -> Task:
    defaults = {
        "id": "task-001",
        "user_story_id": "us-001",
        "name": "Test Task",
        "status": "Planning",
        "priority": "Medium",
    }
    defaults.update(kwargs)
    return Task(**defaults)


class TestAgentDecision:
    def test_valid_construction_with_task(self):
        task = make_task(name="Write tests", priority="High")
        decision = AgentDecision(
            next_task=task,
            productivity_score=0.75,
            suggestion="Great progress! Focus on: Write tests",
            reasoning="Highest priority pending task selected.",
        )
        assert decision.next_task == task
        assert decision.productivity_score == 0.75
        assert decision.suggestion == "Great progress! Focus on: Write tests"
        assert decision.reasoning == "Highest priority pending task selected."

    def test_valid_construction_with_no_task(self):
        decision = AgentDecision(
            next_task=None,
            productivity_score=1.0,
            suggestion="All tasks complete. Add new tasks to keep momentum.",
            reasoning="No pending tasks remain.",
        )
        assert decision.next_task is None
        assert decision.productivity_score == 1.0
        assert isinstance(decision.suggestion, str)

    def test_field_types(self):
        task = make_task()
        decision = AgentDecision(
            next_task=task,
            productivity_score=0.5,
            suggestion="Good pace.",
            reasoning="Balanced workload detected.",
        )
        assert isinstance(decision.next_task, Task)
        assert isinstance(decision.productivity_score, float)
        assert isinstance(decision.suggestion, str)
        assert isinstance(decision.reasoning, str)

    def test_next_task_is_optional(self):
        decision = AgentDecision(
            next_task=None,
            productivity_score=0.0,
            suggestion="No tasks yet.",
        )
        assert decision.next_task is None

    def test_productivity_score_zero(self):
        decision = AgentDecision(
            next_task=None,
            productivity_score=0.0,
            suggestion="Low productivity score.",
        )
        assert decision.productivity_score == 0.0

    def test_productivity_score_one(self):
        decision = AgentDecision(
            next_task=None,
            productivity_score=1.0,
            suggestion="All done!",
        )
        assert decision.productivity_score == 1.0

    def test_reasoning_defaults_to_empty_string(self):
        decision = AgentDecision(
            next_task=None,
            productivity_score=0.0,
            suggestion="No tasks yet.",
        )
        assert decision.reasoning == ""

    def test_missing_required_fields_raises(self):
        with pytest.raises(Exception):
            AgentDecision(next_task=None)  # missing productivity_score and suggestion


class TestAgentDecisionResponse:
    def test_valid_construction(self):
        decision = AgentDecision(
            next_task=None,
            productivity_score=0.5,
            suggestion="Keep going.",
            reasoning="Half the tasks are done.",
        )
        response = AgentDecisionResponse(data=decision)
        assert response.data == decision

    def test_data_field_type(self):
        decision = AgentDecision(
            next_task=make_task(name="Deploy", priority="High"),
            productivity_score=0.6,
            suggestion="Good pace. Next up: Deploy",
            reasoning="Deploy has the highest priority.",
        )
        response = AgentDecisionResponse(data=decision)
        assert isinstance(response.data, AgentDecision)

    def test_nested_task_accessible(self):
        task = make_task(name="Review PR", priority="Low")
        decision = AgentDecision(
            next_task=task,
            productivity_score=0.3,
            suggestion="Low productivity score. Prioritize: Review PR",
            reasoning="Review PR is the only pending task.",
        )
        response = AgentDecisionResponse(data=decision)
        assert response.data.next_task is not None
        assert response.data.next_task.name == "Review PR"

    def test_missing_data_field_raises(self):
        with pytest.raises(Exception):
            AgentDecisionResponse()  # missing data
