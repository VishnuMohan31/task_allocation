# Implementation Plan: postgres-task-retrieval

## Overview

Replace the file-based JSON task store with a read-only asyncpg-backed PostgreSQL repository. Remove all write endpoints and models, align the Task model to the full `public.tasks` schema, and wire the connection pool into the FastAPI lifespan.

## Tasks

- [x] 1. Add asyncpg dependency and database configuration
  - Add `asyncpg>=0.29` to `api/requirements.txt`
  - Add `pg_host`, `pg_port`, `pg_database`, `pg_user`, `pg_password`, `pg_min_connections`, `pg_max_connections` fields to `Settings` in `api/core/config.py` with defaults: host=localhost, port=5437, database=worky, user=postgres, min=2, max=10
  - Add `PG_HOST`, `PG_PORT`, `PG_DATABASE`, `PG_USER`, `PG_PASSWORD` entries to `api/.env`
  - _Requirements: 7.1, 7.2, 9.1_

- [x] 2. Replace Task data models
  - [x] 2.1 Rewrite `api/models/task.py` with the new schema
    - Replace `Task` with the 20-column model aligned to `public.tasks` (id, user_story_id, name, short_description, long_description, phase_id, status, priority, assigned_to, estimated_hours, actual_hours, start_date, due_date, completed_at, sprint_id, is_deleted, created_at, updated_at, created_by, updated_by)
    - Replace `TaskResponse` with the same fields minus `is_deleted`
    - Add `TaskFilters` model with optional fields: status, priority, sprint_id, assigned_to, phase_id
    - Remove `TaskCreate` and `TaskUpdate` entirely
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

  - [ ]* 2.2 Write property test for TaskResponse excludes is_deleted
    - **Property 6: TaskResponse excludes is_deleted**
    - **Validates: Requirements 5.2, 5.3**
    - Use hypothesis to generate arbitrary `Task` instances and assert `is_deleted` is absent from `TaskResponse(**task.model_dump(exclude={"is_deleted"})).model_dump()`

- [x] 3. Implement PostgresTaskRepository
  - [x] 3.1 Rewrite `api/repositories/task_repository.py` as `PostgresTaskRepository`
    - Implement `init_pool()` using `asyncpg.create_pool` with DSN built from settings
    - Implement `close_pool()` to await pool close
    - Implement `list_tasks(filters)`: build parameterised SELECT with `is_deleted = false`, append AND clauses for each non-None filter field, order by `created_at DESC`
    - Implement `get_task(task_id)`: SELECT with `id = $1 AND is_deleted = false`, raise `TaskNotFoundError` if row is None
    - Implement `row_to_task(row)` helper mapping all 20 columns to `Task`
    - _Requirements: 1.1, 1.2, 3.1, 3.2, 4.1–4.7, 6.1, 6.2, 7.3, 8.1_

  - [ ]* 3.2 Write property test for soft-delete exclusion
    - **Property 2: Soft-delete exclusion**
    - **Validates: Requirements 3.1, 3.2, 3.3**
    - Mock `pool.fetch` to return rows mixing `is_deleted=true` and `is_deleted=false`; assert no returned Task has `is_deleted=True`

  - [ ]* 3.3 Write property test for filter correctness
    - **Property 3: Filter correctness**
    - **Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5, 4.6**
    - Use hypothesis to generate `TaskFilters` with arbitrary non-None fields; mock pool to return a fixed task list; assert every returned task satisfies all non-None filter predicates

  - [ ]* 3.4 Write property test for row_to_task round-trip completeness
    - **Property 7: row_to_task round-trip completeness**
    - **Validates: Requirements 6.1, 6.2**
    - Use hypothesis to generate dicts representing all 20 columns (including nullable fields set to None); assert `row_to_task` produces a `Task` where every field equals the source value

  - [ ]* 3.5 Write property test for TaskNotFoundError on absent/soft-deleted tasks
    - **Property 8: TaskNotFoundError for absent or soft-deleted tasks**
    - **Validates: Requirements 8.1, 3.2**
    - Mock `pool.fetchrow` to return None; assert `get_task(any_id)` raises `TaskNotFoundError`

- [x] 4. Checkpoint — Ensure all repository tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Replace TaskService with read-only version
  - [x] 5.1 Rewrite `api/services/task_service.py`
    - Remove `create_task`, `update_task`, `complete_task`, `delete_task`
    - Keep `list_tasks(filters: TaskFilters | None = None)` and `get_task(task_id: str)` as async methods delegating to `PostgresTaskRepository`
    - _Requirements: 2.1, 2.2, 3.3_

  - [ ]* 5.2 Write property test for list_tasks / get_task consistency
    - **Property 4: list_tasks / get_task consistency**
    - **Validates: Requirements 2.1, 2.2**
    - Mock repository to return a fixed task list; for each task returned by `list_tasks()`, assert `get_task(task.id)` returns a task with identical field values

- [x] 6. Replace tasks router with GET-only endpoints
  - [x] 6.1 Rewrite `api/app/api/tasks.py`
    - Remove `create_task`, `update_task`, `complete_task`, `delete_task` route handlers
    - Keep `GET /tasks` accepting optional query params (status, priority, sprint_id, assigned_to, phase_id), build `TaskFilters`, call `service.list_tasks(filters)`, return `list[TaskResponse]`
    - Keep `GET /tasks/{task_id}`, call `service.get_task(task_id)`, return `TaskResponse`
    - Update dependency injection to use `PostgresTaskRepository` (module-level singleton) instead of constructing a new `TaskRepository` per request
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 4.1–4.7_

- [x] 7. Wire pool lifecycle into FastAPI lifespan
  - Update `api/app/main.py` to add an `@asynccontextmanager` lifespan function that calls `repo.init_pool()` on startup and `repo.close_pool()` on shutdown, and pass it to `FastAPI(lifespan=lifespan)`
  - _Requirements: 1.1, 1.2, 1.3_

- [x] 8. Update unit tests
  - [x] 8.1 Rewrite `api/tests/unit/test_task_repository.py`
    - Remove all file-based JSON tests
    - Add async unit tests for `PostgresTaskRepository` using `AsyncMock` for the pool
    - Test `list_tasks` SQL clause construction for each filter field and multi-filter AND combination
    - Test `get_task` returns a Task on a valid row and raises `TaskNotFoundError` when `fetchrow` returns None
    - _Requirements: 3.1, 3.2, 4.1–4.7, 8.1_

  - [x] 8.2 Rewrite `api/tests/unit/test_task_service.py` and `test_task_service_extended.py`
    - Remove tests for `create_task`, `update_task`, `complete_task`, `delete_task`
    - Add async tests for `list_tasks` and `get_task` with mocked `PostgresTaskRepository`
    - _Requirements: 2.1, 2.2, 3.3_

- [x] 9. Update integration tests
  - [x] 9.1 Rewrite `api/tests/integration/test_api_tasks.py` and `test_api_tasks_extended.py`
    - Remove all POST, PATCH, DELETE, and complete endpoint test cases
    - Add tests for `GET /tasks` with no filters, with each individual filter, and with multiple combined filters
    - Add test for `GET /tasks/{task_id}` returning 200 with correct body
    - Add test for `GET /tasks/{task_id}` returning 404 for unknown ID
    - Verify `is_deleted` is absent from all response bodies
    - _Requirements: 2.1–2.6, 3.1–3.3, 4.1–4.7, 5.2, 5.3_

  - [ ]* 9.2 Write property test for result ordering
    - **Property 5: Result ordering**
    - **Validates: Requirements 2.4**
    - Mock repository to return tasks with varying `created_at` values; assert adjacent pairs satisfy `tasks[i].created_at >= tasks[i+1].created_at`

- [x] 10. Final checkpoint — Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- The `PostgresTaskRepository` instance should be a module-level singleton in `tasks.py` (or injected via app state) so the pool is shared across requests
- `asyncpg` parameterised queries use `$1`, `$2`, ... positional placeholders — never f-strings or `.format()` for user-supplied values
- Property tests use `hypothesis` with `AsyncMock` — no live database required for unit-level property tests
- Integration tests may target the existing Docker PostgreSQL container (`worky-postgres` on port 5437) with known seed data
