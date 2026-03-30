"""Async unit tests for PostgresTaskRepository.

Uses AsyncMock/MagicMock to mock the asyncpg pool — no live database required.
"""
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from models.task import Task, TaskFilters
from utils.exceptions import TaskNotFoundError


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_mock_settings():
    s = MagicMock()
    s.pg_user = "postgres"
    s.pg_password = "test"
    s.pg_host = "localhost"
    s.pg_port = 5437
    s.pg_database = "worky"
    s.pg_min_connections = 2
    s.pg_max_connections = 10
    return s


def make_row(**overrides) -> dict:
    """Return a dict representing a full tasks row with sensible defaults."""
    row = {
        "id": "task-1",
        "user_story_id": "us-1",
        "name": "Test Task",
        "short_description": "Short desc",
        "long_description": "Long desc",
        "phase_id": "phase-1",
        "status": "Planning",
        "priority": "Medium",
        "assigned_to": "user-1",
        "estimated_hours": Decimal("4.5"),
        "actual_hours": Decimal("2.0"),
        "start_date": date(2024, 1, 1),
        "due_date": date(2024, 1, 31),
        "completed_at": None,
        "sprint_id": "sprint-1",
        "is_deleted": False,
        "created_at": datetime(2024, 1, 1, 12, 0, 0),
        "updated_at": datetime(2024, 1, 2, 12, 0, 0),
        "created_by": "admin",
        "updated_by": "admin",
    }
    row.update(overrides)
    return row


def make_repo(pool=None):
    """Create a PostgresTaskRepository with a pre-injected mock pool."""
    from repositories.task_repository import PostgresTaskRepository
    repo = PostgresTaskRepository(make_mock_settings())
    repo._pool = pool or AsyncMock()
    return repo


# ---------------------------------------------------------------------------
# list_tasks — no filters
# ---------------------------------------------------------------------------

class TestListTasksNoFilters:
    @pytest.mark.asyncio
    async def test_base_query_contains_is_deleted_false(self):
        """list_tasks() with no filters must include is_deleted = false."""
        pool = AsyncMock()
        pool.fetch = AsyncMock(return_value=[])
        repo = make_repo(pool)

        await repo.list_tasks()

        call_args = pool.fetch.call_args
        query = call_args[0][0]
        assert "is_deleted = false" in query.lower()

    @pytest.mark.asyncio
    async def test_no_filters_passes_no_extra_params(self):
        """list_tasks() with no filters should call fetch with only the query."""
        pool = AsyncMock()
        pool.fetch = AsyncMock(return_value=[])
        repo = make_repo(pool)

        await repo.list_tasks()

        call_args = pool.fetch.call_args
        # Only the query string, no extra positional params
        assert len(call_args[0]) == 1

    @pytest.mark.asyncio
    async def test_returns_empty_list_when_no_rows(self):
        pool = AsyncMock()
        pool.fetch = AsyncMock(return_value=[])
        repo = make_repo(pool)

        result = await repo.list_tasks()

        assert result == []

    @pytest.mark.asyncio
    async def test_returns_tasks_from_rows(self):
        pool = AsyncMock()
        pool.fetch = AsyncMock(return_value=[make_row()])
        repo = make_repo(pool)

        result = await repo.list_tasks()

        assert len(result) == 1
        assert isinstance(result[0], Task)
        assert result[0].id == "task-1"


# ---------------------------------------------------------------------------
# list_tasks — individual filters
# ---------------------------------------------------------------------------

class TestListTasksIndividualFilters:
    @pytest.mark.asyncio
    async def test_filter_status_appends_and_clause(self):
        pool = AsyncMock()
        pool.fetch = AsyncMock(return_value=[])
        repo = make_repo(pool)

        await repo.list_tasks(TaskFilters(status="In Progress"))

        query = pool.fetch.call_args[0][0]
        assert "AND status = $1" in query

    @pytest.mark.asyncio
    async def test_filter_status_passes_value_as_param(self):
        pool = AsyncMock()
        pool.fetch = AsyncMock(return_value=[])
        repo = make_repo(pool)

        await repo.list_tasks(TaskFilters(status="In Progress"))

        args = pool.fetch.call_args[0]
        assert "In Progress" in args

    @pytest.mark.asyncio
    async def test_filter_priority_appends_and_clause(self):
        pool = AsyncMock()
        pool.fetch = AsyncMock(return_value=[])
        repo = make_repo(pool)

        await repo.list_tasks(TaskFilters(priority="High"))

        query = pool.fetch.call_args[0][0]
        assert "AND priority = $1" in query

    @pytest.mark.asyncio
    async def test_filter_sprint_id_appends_and_clause(self):
        pool = AsyncMock()
        pool.fetch = AsyncMock(return_value=[])
        repo = make_repo(pool)

        await repo.list_tasks(TaskFilters(sprint_id="sprint-42"))

        query = pool.fetch.call_args[0][0]
        assert "AND sprint_id = $1" in query

    @pytest.mark.asyncio
    async def test_filter_assigned_to_appends_and_clause(self):
        pool = AsyncMock()
        pool.fetch = AsyncMock(return_value=[])
        repo = make_repo(pool)

        await repo.list_tasks(TaskFilters(assigned_to="user-99"))

        query = pool.fetch.call_args[0][0]
        assert "AND assigned_to = $1" in query

    @pytest.mark.asyncio
    async def test_filter_phase_id_appends_and_clause(self):
        pool = AsyncMock()
        pool.fetch = AsyncMock(return_value=[])
        repo = make_repo(pool)

        await repo.list_tasks(TaskFilters(phase_id="phase-7"))

        query = pool.fetch.call_args[0][0]
        assert "AND phase_id = $1" in query


# ---------------------------------------------------------------------------
# list_tasks — multiple filters
# ---------------------------------------------------------------------------

class TestListTasksMultipleFilters:
    @pytest.mark.asyncio
    async def test_two_filters_produce_two_and_clauses(self):
        pool = AsyncMock()
        pool.fetch = AsyncMock(return_value=[])
        repo = make_repo(pool)

        await repo.list_tasks(TaskFilters(status="Done", priority="Low"))

        query = pool.fetch.call_args[0][0]
        assert "AND status = $1" in query
        assert "AND priority = $2" in query

    @pytest.mark.asyncio
    async def test_two_filters_pass_both_values_as_params(self):
        pool = AsyncMock()
        pool.fetch = AsyncMock(return_value=[])
        repo = make_repo(pool)

        await repo.list_tasks(TaskFilters(status="Done", priority="Low"))

        args = pool.fetch.call_args[0]
        assert "Done" in args
        assert "Low" in args

    @pytest.mark.asyncio
    async def test_all_five_filters_produce_five_and_clauses(self):
        pool = AsyncMock()
        pool.fetch = AsyncMock(return_value=[])
        repo = make_repo(pool)

        filters = TaskFilters(
            status="In Progress",
            priority="High",
            sprint_id="sprint-1",
            assigned_to="user-1",
            phase_id="phase-1",
        )
        await repo.list_tasks(filters)

        query = pool.fetch.call_args[0][0]
        for i, field in enumerate(("status", "priority", "sprint_id", "assigned_to", "phase_id"), start=1):
            assert f"AND {field} = ${i}" in query


# ---------------------------------------------------------------------------
# get_task
# ---------------------------------------------------------------------------

class TestGetTask:
    @pytest.mark.asyncio
    async def test_returns_task_when_row_found(self):
        pool = AsyncMock()
        pool.fetchrow = AsyncMock(return_value=make_row(id="task-abc"))
        repo = make_repo(pool)

        result = await repo.get_task("task-abc")

        assert isinstance(result, Task)
        assert result.id == "task-abc"

    @pytest.mark.asyncio
    async def test_raises_task_not_found_when_fetchrow_returns_none(self):
        pool = AsyncMock()
        pool.fetchrow = AsyncMock(return_value=None)
        repo = make_repo(pool)

        with pytest.raises(TaskNotFoundError):
            await repo.get_task("missing-id")

    @pytest.mark.asyncio
    async def test_query_uses_id_param_and_is_deleted_false(self):
        pool = AsyncMock()
        pool.fetchrow = AsyncMock(return_value=make_row())
        repo = make_repo(pool)

        await repo.get_task("task-xyz")

        call_args = pool.fetchrow.call_args[0]
        query = call_args[0]
        assert "is_deleted = false" in query.lower()
        assert call_args[1] == "task-xyz"


# ---------------------------------------------------------------------------
# _row_to_task
# ---------------------------------------------------------------------------

class TestRowToTask:
    def test_maps_all_20_columns(self):
        repo = make_repo()
        row = make_row()

        task = repo._row_to_task(row)

        assert task.id == row["id"]
        assert task.user_story_id == row["user_story_id"]
        assert task.name == row["name"]
        assert task.short_description == row["short_description"]
        assert task.long_description == row["long_description"]
        assert task.phase_id == row["phase_id"]
        assert task.status == row["status"]
        assert task.priority == row["priority"]
        assert task.assigned_to == row["assigned_to"]
        assert task.start_date == row["start_date"]
        assert task.due_date == row["due_date"]
        assert task.completed_at == row["completed_at"]
        assert task.sprint_id == row["sprint_id"]
        assert task.is_deleted == row["is_deleted"]
        assert task.created_at == row["created_at"]
        assert task.updated_at == row["updated_at"]
        assert task.created_by == row["created_by"]
        assert task.updated_by == row["updated_by"]

    def test_maps_none_for_nullable_fields(self):
        repo = make_repo()
        row = make_row(
            short_description=None,
            long_description=None,
            phase_id=None,
            assigned_to=None,
            estimated_hours=None,
            actual_hours=None,
            start_date=None,
            due_date=None,
            completed_at=None,
            sprint_id=None,
            created_by=None,
            updated_by=None,
        )

        task = repo._row_to_task(row)

        assert task.short_description is None
        assert task.long_description is None
        assert task.phase_id is None
        assert task.assigned_to is None
        assert task.estimated_hours is None
        assert task.actual_hours is None
        assert task.start_date is None
        assert task.due_date is None
        assert task.completed_at is None
        assert task.sprint_id is None
        assert task.created_by is None
        assert task.updated_by is None

    def test_casts_decimal_estimated_hours_to_float(self):
        repo = make_repo()
        row = make_row(estimated_hours=Decimal("3.75"))

        task = repo._row_to_task(row)

        assert isinstance(task.estimated_hours, float)
        assert task.estimated_hours == 3.75

    def test_casts_decimal_actual_hours_to_float(self):
        repo = make_repo()
        row = make_row(actual_hours=Decimal("1.25"))

        task = repo._row_to_task(row)

        assert isinstance(task.actual_hours, float)
        assert task.actual_hours == 1.25
