"""Integration-test fixtures — mocks the PostgresTaskRepository pool."""
from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient


def make_task_row(
    id="TSK-001",
    name="Test Task",
    status="Planning",
    priority="Medium",
    user_story_id="US-001",
    sprint_id=None,
    assigned_to=None,
    phase_id=None,
    is_deleted=False,
):
    return {
        "id": id,
        "user_story_id": user_story_id,
        "name": name,
        "short_description": None,
        "long_description": None,
        "phase_id": phase_id,
        "status": status,
        "priority": priority,
        "assigned_to": assigned_to,
        "estimated_hours": None,
        "actual_hours": None,
        "start_date": None,
        "due_date": None,
        "completed_at": None,
        "sprint_id": sprint_id,
        "is_deleted": is_deleted,
        "created_at": None,
        "updated_at": None,
        "created_by": None,
        "updated_by": None,
    }


@pytest.fixture()
def mock_pool():
    """Patch _repo so no real DB connection is needed.

    Patches init_pool/close_pool as no-ops and replaces _pool with a MagicMock
    whose fetch/fetchrow are AsyncMocks returning empty results by default.
    """
    from app.api.tasks import _repo

    pool = MagicMock()
    pool.fetch = AsyncMock(return_value=[])
    pool.fetchrow = AsyncMock(return_value=None)

    with (
        patch.object(_repo, "init_pool", new=AsyncMock()),
        patch.object(_repo, "close_pool", new=AsyncMock()),
        patch.object(_repo, "_pool", pool),
    ):
        yield pool


@pytest.fixture()
def client(mock_pool):
    """TestClient with DB pool mocked — lifespan runs without a real Postgres connection."""
    from app.main import app

    with TestClient(app, raise_server_exceptions=True) as c:
        yield c
