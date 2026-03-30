"""PostgreSQL-backed task repository using asyncpg."""
import asyncpg

from core.config import Settings
from models.task import Task, TaskFilters
from utils.exceptions import TaskNotFoundError


class PostgresTaskRepository:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._pool = None

    async def init_pool(self) -> None:
        """Create the asyncpg connection pool."""
        s = self._settings
        dsn = f"postgresql://{s.pg_user}:{s.pg_password}@{s.pg_host}:{s.pg_port}/{s.pg_database}"
        self._pool = await asyncpg.create_pool(
            dsn,
            min_size=s.pg_min_connections,
            max_size=s.pg_max_connections,
        )

    async def close_pool(self) -> None:
        """Close the connection pool if it exists."""
        if self._pool is not None:
            await self._pool.close()

    async def list_tasks(self, filters: TaskFilters | None = None) -> list[Task]:
        """Return non-deleted tasks, optionally filtered."""
        query = "SELECT * FROM public.tasks WHERE is_deleted = false"
        params: list = []

        if filters is not None:
            for field in ("status", "priority", "sprint_id", "assigned_to", "phase_id"):
                value = getattr(filters, field, None)
                if value is not None:
                    params.append(value)
                    query += f" AND {field} = ${len(params)}"

        query += " ORDER BY created_at DESC"
        rows = await self._pool.fetch(query, *params)
        return [self._row_to_task(row) for row in rows]

    async def get_task(self, task_id: str) -> Task:
        """Return a single task by ID. Raises TaskNotFoundError if absent."""
        row = await self._pool.fetchrow(
            "SELECT * FROM public.tasks WHERE id = $1 AND is_deleted = false",
            task_id,
        )
        if row is None:
            raise TaskNotFoundError(task_id)
        return self._row_to_task(row)

    def _row_to_task(self, row) -> Task:
        """Map an asyncpg Record to a Task model."""
        return Task(
            id=row["id"],
            user_story_id=row["user_story_id"],
            name=row["name"],
            short_description=row["short_description"],
            long_description=row["long_description"],
            phase_id=row["phase_id"],
            status=row["status"],
            priority=row["priority"],
            assigned_to=row["assigned_to"],
            estimated_hours=float(row["estimated_hours"]) if row["estimated_hours"] is not None else None,
            actual_hours=float(row["actual_hours"]) if row["actual_hours"] is not None else None,
            start_date=row["start_date"],
            due_date=row["due_date"],
            completed_at=row["completed_at"],
            sprint_id=row["sprint_id"],
            is_deleted=row["is_deleted"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            created_by=row["created_by"],
            updated_by=row["updated_by"],
        )
