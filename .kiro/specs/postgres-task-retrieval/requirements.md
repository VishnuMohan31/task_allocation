# Requirements Document

## Introduction

Replace the existing file-based JSON task store with a read-only PostgreSQL connection to an external `worky` database. The API becomes a pure read layer: all write endpoints (POST, PATCH, DELETE) are removed, and only `GET /tasks` and `GET /tasks/{task_id}` remain, backed by asyncpg queries against `public.tasks`.

## Glossary

- **API**: The FastAPI application serving task data over HTTP.
- **PostgresTaskRepository**: The repository class that manages the asyncpg connection pool and executes SQL queries against `public.tasks`.
- **TaskService**: The service layer that orchestrates calls between the router and the repository.
- **Router**: The FastAPI tasks router exposing HTTP endpoints.
- **Pool**: The asyncpg connection pool held by `PostgresTaskRepository`.
- **Task**: The internal Pydantic model representing a row from `public.tasks`, including all 20 columns.
- **TaskResponse**: The Pydantic model returned to HTTP clients, identical to `Task` but excluding `is_deleted`.
- **TaskFilters**: The Pydantic model holding optional filter parameters: `status`, `priority`, `sprint_id`, `assigned_to`, `phase_id`.
- **Settings**: The pydantic-settings configuration class that reads database credentials from environment variables.
- **TaskNotFoundError**: The application exception raised when a requested task does not exist or is soft-deleted.
- **soft-delete**: The pattern where rows are marked `is_deleted = true` rather than physically removed.

---

## Requirements

### Requirement 1: Connection Pool Lifecycle

**User Story:** As a system operator, I want the database connection pool to be managed automatically at application startup and shutdown, so that connections are available for all requests and released cleanly when the app stops.

#### Acceptance Criteria

1. WHEN the application starts, THE PostgresTaskRepository SHALL initialise an asyncpg connection pool with a minimum of 2 and a maximum of 10 connections.
2. WHEN the application shuts down, THE PostgresTaskRepository SHALL close the connection pool and release all held connections.
3. IF the database is unreachable during startup, THEN THE API SHALL propagate the connection error and fail to start.

---

### Requirement 2: Read-Only HTTP Endpoints

**User Story:** As an API consumer, I want to retrieve tasks via HTTP GET endpoints, so that I can list and inspect tasks without the ability to mutate them.

#### Acceptance Criteria

1. THE Router SHALL expose a `GET /tasks` endpoint that returns a list of `TaskResponse` objects.
2. THE Router SHALL expose a `GET /tasks/{task_id}` endpoint that returns a single `TaskResponse` object.
3. WHEN a request is made to `POST /tasks`, `PATCH /tasks/{task_id}`, or `DELETE /tasks/{task_id}`, THE Router SHALL return a 404 or 405 HTTP response.
4. WHEN `GET /tasks` is called with no filters, THE Router SHALL return all non-deleted tasks ordered by `created_at` descending.
5. WHEN `GET /tasks/{task_id}` is called with a valid task ID, THE Router SHALL return the corresponding `TaskResponse` with a 200 status code.
6. WHEN `GET /tasks/{task_id}` is called with an ID that does not exist or is soft-deleted, THE Router SHALL return a 404 response with an `ErrorResponse` body.

---

### Requirement 3: Soft-Delete Filtering

**User Story:** As an API consumer, I want soft-deleted tasks to be invisible to all queries, so that I only see active tasks.

#### Acceptance Criteria

1. WHEN `GET /tasks` is called, THE PostgresTaskRepository SHALL apply `is_deleted = false` to the SQL query before returning results.
2. WHEN `GET /tasks/{task_id}` is called, THE PostgresTaskRepository SHALL apply `is_deleted = false` to the SQL query and raise `TaskNotFoundError` if the row is absent or soft-deleted.
3. THE TaskService SHALL never return a `Task` where `is_deleted` is `true`.

---

### Requirement 4: Task Filtering

**User Story:** As an API consumer, I want to filter tasks by status, priority, sprint, assignee, and phase, so that I can retrieve targeted subsets of tasks.

#### Acceptance Criteria

1. WHEN `GET /tasks` is called with a `status` query parameter, THE PostgresTaskRepository SHALL include only tasks whose `status` column matches the provided value.
2. WHEN `GET /tasks` is called with a `priority` query parameter, THE PostgresTaskRepository SHALL include only tasks whose `priority` column matches the provided value.
3. WHEN `GET /tasks` is called with a `sprint_id` query parameter, THE PostgresTaskRepository SHALL include only tasks whose `sprint_id` column matches the provided value.
4. WHEN `GET /tasks` is called with an `assigned_to` query parameter, THE PostgresTaskRepository SHALL include only tasks whose `assigned_to` column matches the provided value.
5. WHEN `GET /tasks` is called with a `phase_id` query parameter, THE PostgresTaskRepository SHALL include only tasks whose `phase_id` column matches the provided value.
6. WHEN `GET /tasks` is called with multiple filter parameters, THE PostgresTaskRepository SHALL combine all non-null filters using AND logic so that only tasks satisfying every filter are returned.
7. WHEN `GET /tasks` is called with no filter parameters, THE PostgresTaskRepository SHALL return all non-deleted tasks without additional filtering.

---

### Requirement 5: Task and Response Data Models

**User Story:** As a developer, I want the Task model to reflect the full `public.tasks` schema and the TaskResponse to omit internal fields, so that the API surface is clean and the internal model is complete.

#### Acceptance Criteria

1. THE Task model SHALL contain all 20 columns of `public.tasks`: `id`, `user_story_id`, `name`, `short_description`, `long_description`, `phase_id`, `status`, `priority`, `assigned_to`, `estimated_hours`, `actual_hours`, `start_date`, `due_date`, `completed_at`, `sprint_id`, `is_deleted`, `created_at`, `updated_at`, `created_by`, `updated_by`.
2. THE TaskResponse model SHALL contain all fields of `Task` except `is_deleted`.
3. WHEN a `Task` is serialised as a `TaskResponse`, THE API SHALL exclude the `is_deleted` field from the HTTP response body.
4. THE API SHALL remove the `TaskCreate` and `TaskUpdate` models entirely so that no write-oriented schemas are accessible.

---

### Requirement 6: Row Mapping

**User Story:** As a developer, I want every column from a `public.tasks` row to be correctly mapped to the Task model, so that no data is lost or misrepresented when reading from the database.

#### Acceptance Criteria

1. WHEN `PostgresTaskRepository` fetches a row from `public.tasks`, THE PostgresTaskRepository SHALL map all 20 columns to the corresponding `Task` fields, preserving `None` for nullable columns that contain SQL `NULL`.
2. WHEN a date or datetime column contains a value, THE PostgresTaskRepository SHALL map it to the appropriate Python `date` or `datetime` type.

---

### Requirement 7: Database Configuration

**User Story:** As a system operator, I want database credentials to be loaded from environment variables, so that secrets are never hardcoded in source code.

#### Acceptance Criteria

1. THE Settings class SHALL read `pg_host`, `pg_port`, `pg_database`, `pg_user`, and `pg_password` from environment variables or a `.env` file.
2. THE Settings class SHALL provide default values: `pg_host = "localhost"`, `pg_port = 5437`, `pg_database = "worky"`, `pg_user = "postgres"`, `pg_min_connections = 2`, `pg_max_connections = 10`.
3. THE PostgresTaskRepository SHALL use only parameterised queries (`$1`, `$2`, …) when constructing SQL statements, with no string interpolation of user-supplied values.

---

### Requirement 8: Runtime Error Handling

**User Story:** As an API consumer, I want clear error responses when tasks are not found or the database is unavailable, so that I can handle failures gracefully.

#### Acceptance Criteria

1. WHEN `get_task` finds no row matching the given ID with `is_deleted = false`, THE PostgresTaskRepository SHALL raise `TaskNotFoundError`.
2. WHEN `TaskNotFoundError` is raised, THE Router SHALL return a 404 HTTP response with an `ErrorResponse` body containing the error code `TASK_NOT_FOUND`.
3. WHEN an asyncpg exception occurs during a query at runtime, THE API SHALL return a 500 HTTP response with an `ErrorResponse` body containing the error code `INTERNAL_ERROR`.

---

### Requirement 9: Dependency

**User Story:** As a developer, I want the asyncpg library available in the project dependencies, so that the PostgreSQL driver is installed in all environments.

#### Acceptance Criteria

1. THE `api/requirements.txt` file SHALL include `asyncpg>=0.29` as a dependency.
