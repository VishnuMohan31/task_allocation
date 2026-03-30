"""Shared pytest fixtures for the productivity-agent-api test suite.

Provides:
- ``tmp_store``   — a Path pointing to a temporary store.json location
- ``tmp_repo``    — a TaskRepository backed by ``tmp_store``
- ``client``      — a FastAPI TestClient with both router dependency overrides applied
- ``sample_task`` — a pre-built Task instance for reuse in tests
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from models.task import Task
from repositories.task_repository import TaskRepository


# ---------------------------------------------------------------------------
# Store / repository fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def tmp_store(tmp_path: Path) -> Path:
    """Return a Path for a temporary store.json that does not yet exist."""
    return tmp_path / "store.json"


@pytest.fixture()
def tmp_repo(tmp_store: Path) -> TaskRepository:
    """Return a TaskRepository backed by a temporary directory."""
    return TaskRepository(store_path=tmp_store)


# ---------------------------------------------------------------------------
# TestClient fixture with dependency overrides for both routers
# ---------------------------------------------------------------------------


@pytest.fixture()
def client(tmp_repo: TaskRepository) -> TestClient:
    """Return a TestClient with TaskRepository dependency overridden for all routers.

    Both ``app.api.tasks.get_repository`` and ``app.api.agent.get_repository``
    are overridden so no real store.json is touched during tests.
    """
    from app.api.agent import get_repository as agent_get_repo
    from app.api.tasks import get_repository as tasks_get_repo

    app.dependency_overrides[tasks_get_repo] = lambda: tmp_repo
    app.dependency_overrides[agent_get_repo] = lambda: tmp_repo
    yield TestClient(app)
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Sample task fixture
# ---------------------------------------------------------------------------


@pytest.fixture()
def sample_task() -> Task:
    """Return a pre-built pending Task instance for reuse across tests."""
    return Task(
        title="Sample task",
        description="A reusable task fixture",
        priority=3,
        tags=["fixture"],
        completed=False,
        created_at=datetime(2024, 1, 1, 12, 0, 0),
    )
