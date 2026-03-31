from __future__ import annotations

import json
from datetime import date

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from core.config import settings
from models.agent import AgentDecision
from models.task import Task
from services.task_service import TaskService


def tasks_agent_json(tasks: list[Task]) -> str:
    """Serialize tasks for the model (one place — tool output matches this shape)."""
    return json.dumps([
        {
            "id": t.id,
            "name": t.name,
            "status": t.status,
            "priority": t.priority,
            "estimated_hours": t.estimated_hours,
            "actual_hours": t.actual_hours,
            "start_date": t.start_date.isoformat() if t.start_date else None,
            "due_date": t.due_date.isoformat() if t.due_date else None,
            "phase_id": t.phase_id,
            "sprint_id": t.sprint_id,
            "assigned_to": t.assigned_to,
        }
        for t in tasks
    ])


@tool
def get_current_date_context() -> str:
    """Today's date (ISO) and weekday — use when comparing task due_date to today."""
    t = date.today()
    return json.dumps({"date_iso": t.isoformat(), "weekday": t.strftime("%A")})


def make_agent_tools(service: TaskService) -> list:
    @tool
    async def get_tasks() -> str:
        """Load the current task list from the database."""
        rows = await service.list_tasks(None)
        if not rows:
            return settings.agent_no_pending_message
        return tasks_agent_json(rows)

    return [get_tasks, get_current_date_context]


def _build_agent(service: TaskService):
    llm = ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
        temperature=settings.openai_temperature,
    )
    return create_react_agent(llm, make_agent_tools(service))


def build_agent_graph(service: TaskService):
    """Compiled graph for LangGraph Studio (`langgraph dev`)."""
    return _build_agent(service)


def _extract_assistant_output(result: dict) -> str:
    output = ""
    for msg in reversed(result["messages"]):
        content = getattr(msg, "content", "") or ""
        if content.strip():
            output = content.strip()
            break
    return output


def _strip_code_fences(output: str) -> str:
    if not output.startswith("```"):
        return output
    lines = output.splitlines()
    return "\n".join(
        line for line in lines
        if not line.strip().startswith("```")
    ).strip()


def _validation_issues_for_payload(decision_data: dict) -> list[str]:
    issues: list[str] = []
    raw_score = decision_data.get("productivity_score", None)
    if raw_score is None:
        issues.append("missing productivity_score")
    else:
        try:
            score = float(raw_score)
        except (TypeError, ValueError):
            issues.append("productivity_score must be a number")
        else:
            if not 0.0 <= score <= 1.0:
                issues.append("productivity_score must be between 0.0 and 1.0")
    suggestion = decision_data.get("suggestion", "")
    if not isinstance(suggestion, str) or not suggestion.strip():
        issues.append("suggestion must be a non-empty string")
    nid = decision_data.get("next_task_id", None)
    if nid is not None and not isinstance(nid, str):
        issues.append("next_task_id must be a string or null")
    return issues


def _parse_and_validate_decision(output: str, tasks: list[Task]) -> tuple[AgentDecision | None, list[str]]:
    if not output:
        return None, ["response was empty"]

    try:
        decision_data = json.loads(output)
    except json.JSONDecodeError as e:
        return None, [f"response is not valid JSON ({e.msg})"]

    if not isinstance(decision_data, dict):
        return None, ["response must be a JSON object"]

    issues = _validation_issues_for_payload(decision_data)
    if issues:
        return None, issues

    next_task_id = decision_data.get("next_task_id")
    next_task = (
        next((t for t in tasks if t.id == next_task_id), None)
        if next_task_id
        else None
    )
    score = float(decision_data["productivity_score"])
    return AgentDecision(
        next_task=next_task,
        productivity_score=score,
        suggestion=decision_data["suggestion"].strip(),
        reasoning=str(decision_data.get("reasoning", "") or ""),
    ), []


def _fallback_agent_decision(issues: list[str]) -> AgentDecision:
    return AgentDecision(
        next_task=None,
        productivity_score=0.0,
        suggestion=(
            "Could not obtain a valid agent decision after retries; using a safe fallback."
        ),
        reasoning="Validation failed after retry: " + "; ".join(issues),
    )


_MAX_DECISION_ATTEMPTS = 2


async def decide(service: TaskService) -> AgentDecision:
    agent = _build_agent(service)
    messages: list = [
        {"role": "system", "content": settings.agent_system_prompt},
        {"role": "user", "content": settings.agent_user_prompt},
    ]
    last_issues: list[str] = []

    for attempt in range(_MAX_DECISION_ATTEMPTS):
        result = await agent.ainvoke({"messages": messages})
        output = _strip_code_fences(_extract_assistant_output(result))
        tasks = await service.list_tasks(None)
        decision, issues = _parse_and_validate_decision(output, tasks)
        if decision is not None:
            return decision
        last_issues = issues
        if attempt == _MAX_DECISION_ATTEMPTS - 1:
            break
        feedback = (
            "Your previous response was invalid because: "
            + "; ".join(issues)
            + ". Fix and retry."
        )
        messages = list(result["messages"]) + [{"role": "user", "content": feedback}]

    return _fallback_agent_decision(last_issues)
