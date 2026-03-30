# Requirements: Productivity Agent API

## Requirement 1: Task Management Endpoints

### User Story
As an API consumer, I want to create tasks and mark them complete via HTTP endpoints, so that I can manage my task list programmatically.

### Acceptance Criteria

1.1 GIVEN a valid `TaskCreate` payload (non-empty title, priority 1–5), WHEN `POST /tasks` is called, THEN the API returns `201` with a `TaskResponse` containing a unique UUID `id`, `completed: false`, and `created_at` set to the current UTC time.

1.2 GIVEN a task exists with `task_id`, WHEN `POST /tasks/{task_id}/complete` is called, THEN the API returns `200` with the task updated to `completed: true` and `completed_at` set to the current UTC time.

1.3 GIVEN a `task_id` that does not exist, WHEN `POST /tasks/{task_id}/complete` is called, THEN the API returns `404` with `{ "error_code": "TASK_NOT_FOUND", "message": "...", "details": {} }`.

1.4 GIVEN an invalid request body (e.g., missing title, priority out of range), WHEN `POST /tasks` is called, THEN the API returns `422` with a standardized error response.

---

## Requirement 2: Agent Decision Endpoint

### User Story
As an API consumer, I want to ask the agent for its decision, so that I receive the next best task to work on, a productivity score, and an actionable suggestion.

### Acceptance Criteria

2.1 WHEN `GET /agent/decision` is called, THEN the API returns `200` with a response containing `next_task` (Task or null), `productivity_score` (float in [0.0, 1.0]), and a non-empty `suggestion` string.

2.2 GIVEN a list of pending tasks with varying priorities, WHEN the agent runs, THEN `next_task` is the pending task with the highest priority (ties broken by earliest `created_at`).

2.3 GIVEN all tasks are completed, WHEN the agent runs, THEN `next_task` is `null` and `suggestion` indicates all tasks are done.

2.4 GIVEN no tasks exist, WHEN the agent runs, THEN `productivity_score` is `0.0` and `next_task` is `null`.

2.5 FOR ANY list of tasks, `productivity_score` MUST always be in the range `[0.0, 1.0]`.

---

## Requirement 3: Agent Logic (Pure Functions)

### User Story
As a developer, I want the agent logic to be implemented as pure, stateless functions, so that it is easily testable and replaceable with an LLM later.

### Acceptance Criteria

3.1 `select_next_task(tasks)` MUST be a pure function with no side effects; given the same input it always returns the same output.

3.2 `calculate_productivity_score(tasks)` MUST return a float in `[0.0, 1.0]` for any valid list of tasks, including an empty list.

3.3 `generate_suggestion(next_task, score)` MUST return a non-empty string for all combinations of `next_task` (Task or None) and `score ∈ [0.0, 1.0]`.

3.4 `decide(tasks)` MUST compose the three functions above and return a complete `AgentDecision` with all fields populated.

---

## Requirement 4: Repository and Data Storage

### User Story
As a developer, I want all file I/O abstracted behind a repository layer, so that the storage backend can be swapped without touching services or routes.

### Acceptance Criteria

4.1 All reads and writes to `data/store.json` MUST go through `TaskRepository`; services and route handlers MUST NOT import or use file I/O directly.

4.2 `TaskRepository.list_tasks()` MUST return an empty list (not raise) when `store.json` does not exist.

4.3 `TaskRepository.get_task(task_id)` MUST raise `TaskNotFoundError` when the task does not exist.

4.4 GIVEN `store.json` contains invalid JSON, WHEN any repository method is called, THEN a `StoreCorruptedError` is raised and the API returns `500` with `{ "error_code": "STORE_CORRUPTED", ... }`.

4.5 The path to `store.json` MUST be configurable via application settings (not hardcoded).

---

## Requirement 5: Structured Logging

### User Story
As an operator, I want structured logs for every request, response, and error, so that I can trace issues in production.

### Acceptance Criteria

5.1 Every HTTP request MUST be logged with `request_id`, `timestamp`, `log_level`, HTTP method, and path.

5.2 Every HTTP response MUST be logged with `request_id`, `status_code`, and response time.

5.3 Every exception MUST be logged with `request_id`, `timestamp`, `log_level: ERROR`, and the exception traceback.

5.4 The log level MUST be configurable via application settings.

5.5 `request_id` MUST be a unique identifier generated per request (e.g., UUID4) and included in all log entries for that request.

---

## Requirement 6: Error Handling

### User Story
As an API consumer, I want all errors to return a consistent, machine-readable response format, so that I can handle errors programmatically.

### Acceptance Criteria

6.1 ALL error responses MUST follow the schema `{ "error_code": string, "message": string, "details": object }`.

6.2 `TaskNotFoundError` MUST map to HTTP `404` with `error_code: "TASK_NOT_FOUND"`.

6.3 `StoreCorruptedError` MUST map to HTTP `500` with `error_code: "STORE_CORRUPTED"`.

6.4 Unhandled exceptions MUST map to HTTP `500` with `error_code: "INTERNAL_ERROR"` and MUST NOT expose internal stack traces in the response body.

6.5 Pydantic `ValidationError` MUST map to HTTP `422` with `error_code: "VALIDATION_ERROR"`.

---

## Requirement 7: Configuration and Code Quality

### User Story
As a developer, I want all configuration centralized and no hardcoded values, so that the app is easy to configure across environments.

### Acceptance Criteria

7.1 All configurable values (store path, log level, app name, etc.) MUST be defined in a `Settings` class using `pydantic-settings` and loaded from environment variables or a `.env` file.

7.2 Dependencies (repository, service) MUST be injected via FastAPI's `Depends()` mechanism; no global singletons instantiated in module scope.

7.3 Each function MUST have a single, clearly defined responsibility (SRP).

---

## Requirement 8: Test-Driven Development

### User Story
As a developer, I want tests written before implementation, so that the codebase is verifiable and regressions are caught early.

### Acceptance Criteria

8.1 Test files MUST be created before their corresponding implementation files.

8.2 Agent service tests MUST cover: empty task list, all tasks completed, single task, multiple tasks with different priorities, tie-breaking by `created_at`.

8.3 Task service tests MUST cover: successful creation, successful completion, completion of non-existent task.

8.4 Repository tests MUST use `tmp_path` (pytest fixture) and MUST NOT touch the real `data/store.json`.

8.5 API endpoint tests MUST use FastAPI `TestClient` with the repository dependency overridden to use an in-memory or `tmp_path`-backed store.

8.6 A property-based test using `hypothesis` MUST verify that `calculate_productivity_score` always returns a value in `[0.0, 1.0]` for any list of tasks.
