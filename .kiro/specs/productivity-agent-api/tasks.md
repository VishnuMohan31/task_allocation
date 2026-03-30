# Tasks: Productivity Agent API

## Phase 1: Project Scaffold

- [x] 1.1 Initialize project structure
  - Objective: Create the full directory skeleton so all subsequent tasks have a home.
  - Files: `app/__init__.py`, `app/api/__init__.py`, `core/__init__.py`, `models/__init__.py`, `services/__init__.py`, `repositories/__init__.py`, `utils/__init__.py`, `tests/__init__.py`, `data/.gitkeep`
  - Action:
    1. Write all empty `__init__.py` files and `data/.gitkeep`.
    2. Write `tests/test_scaffold.py` that asserts each file/directory exists.
    3. Run `pytest tests/test_scaffold.py -v` and save output as proof.
  - Expected outcome: `tests/test_scaffold.py` exists and pytest output confirms all directories and files are present.

- [x] 1.2 Create `requirements.txt` with all dependencies
  - Objective: Pin all runtime and dev dependencies so the project installs cleanly.
  - Files: `requirements.txt`
  - Action:
    1. Write `requirements.txt` with all dependencies.
    2. Write `tests/test_requirements.py` that asserts each required package is importable.
    3. Run `pytest tests/test_requirements.py -v` and save output as proof.
  - Expected outcome: `tests/test_requirements.py` exists and pytest output confirms fastapi, uvicorn, pydantic, pydantic-settings, pytest, httpx, hypothesis are importable.

- [x] 1.3 Create application settings (`core/config.py`)
  - Objective: Centralize all config values; no hardcoding anywhere else.
  - Files: `core/config.py`
  - Action:
    1. Write `core/config.py` with the `Settings` class.
    2. Write `tests/test_config.py` that instantiates `Settings` and asserts `store_path`, `log_level`, `app_name` are accessible.
    3. Run `pytest tests/test_config.py -v` and save output as proof.
  - Expected outcome: `tests/test_config.py` exists and pytest output confirms `Settings` loads correctly.

---

## Phase 2: Models (Schemas)

- [x] 2.1 Define task Pydantic models (`models/task.py`)
  - Objective: Establish the core domain types used across all layers.
  - Files: `models/task.py`
  - Action:
    1. Write `models/task.py` with `TaskCreate`, `Task`, `TaskResponse`.
    2. Write `tests/test_models_task.py` that tests valid construction, title empty validation, priority out-of-range validation, UUID default, datetime default.
    3. Run `pytest tests/test_models_task.py -v` and save output as proof.
  - Expected outcome: `tests/test_models_task.py` exists and pytest output confirms all model validations behave correctly.

- [x] 2.2 Define agent Pydantic model (`models/agent.py`)
  - Objective: Define the response shape for the agent decision endpoint.
  - Files: `models/agent.py`
  - Action:
    1. Write `models/agent.py` with `AgentDecision` and `AgentDecisionResponse`.
    2. Write `tests/test_models_agent.py` that tests valid construction and field types.
    3. Run `pytest tests/test_models_agent.py -v` and save output as proof.
  - Expected outcome: `tests/test_models_agent.py` exists and pytest output confirms `AgentDecision` and `AgentDecisionResponse` are correctly defined.

- [x] 2.3 Define error response model (`models/error.py`)
  - Objective: Establish the standardized error response schema.
  - Files: `models/error.py`
  - Action:
    1. Write `models/error.py` with `ErrorResponse`.
    2. Write `tests/test_models_error.py` that tests valid construction and default `details` field.
    3. Run `pytest tests/test_models_error.py -v` and save output as proof.
  - Expected outcome: `tests/test_models_error.py` exists and pytest output confirms `ErrorResponse` is correctly defined.

---

## Phase 3: Custom Exceptions and Error Handling

- [x] 3.1 Define custom exception classes (`utils/exceptions.py`)
  - Objective: Create typed exceptions that map cleanly to HTTP status codes.
  - Files: `utils/exceptions.py`
  - Action:
    1. Write `utils/exceptions.py` with `TaskNotFoundError` and `StoreCorruptedError`.
    2. Write `tests/test_exceptions.py` that raises each exception and asserts `error_code` attribute.
    3. Run `pytest tests/test_exceptions.py -v` and save output as proof.
  - Expected outcome: `tests/test_exceptions.py` exists and pytest output confirms both exceptions carry the correct `error_code`.

- [x] 3.2 Write tests for exception handler behavior (`tests/test_error_handling.py`) — TDD
  - Objective: Write test cases for each custom exception mapping to HTTP responses.
  - Files: `tests/test_error_handling.py`
  - Action:
    1. Write `tests/test_error_handling.py` covering 404 (TaskNotFoundError), 500 (StoreCorruptedError), 500 (unhandled), 422 (validation).
    2. Run `pytest tests/test_error_handling.py -v` and save output as proof (tests will be red until 3.3 is done).
  - Expected outcome: `tests/test_error_handling.py` exists and pytest output is saved as proof of test execution.

- [x] 3.3 Implement global exception handlers (`utils/error_handlers.py`)
  - Objective: Register FastAPI exception handlers that convert exceptions to `ErrorResponse`.
  - Files: `utils/error_handlers.py`
  - Action:
    1. Write `utils/error_handlers.py` with all exception handlers.
    2. Run `pytest tests/test_error_handling.py -v` and save output as proof.
  - Expected outcome: pytest output confirms all error handling tests pass green.

---

## Phase 4: Structured Logging

- [x] 4.1 Implement structured logger factory (`core/logging.py`)
  - Objective: Provide a single `get_logger(name)` function returning a structured logger.
  - Files: `core/logging.py`
  - Action:
    1. Write `core/logging.py` with `get_logger`.
    2. Write `tests/test_logging.py` that calls `get_logger`, emits a log record, and asserts `timestamp`, `log_level` fields are present.
    3. Run `pytest tests/test_logging.py -v` and save output as proof.
  - Expected outcome: `tests/test_logging.py` exists and pytest output confirms logger emits structured records.

- [x] 4.2 Implement request logging middleware (`app/middleware.py`)
  - Objective: Log every request and response with `request_id`, method, path, status code, and duration.
  - Files: `app/middleware.py`
  - Action:
    1. Write `app/middleware.py` with the logging middleware.
    2. Write `tests/test_middleware.py` that sends a request via `TestClient` and asserts two log entries with matching `request_id` are emitted.
    3. Run `pytest tests/test_middleware.py -v` and save output as proof.
  - Expected outcome: `tests/test_middleware.py` exists and pytest output confirms middleware logs request and response.

---

## Phase 5: Repository Layer — TDD

- [x] 5.1 Write tests for `TaskRepository` (`tests/test_task_repository.py`) — TDD
  - Objective: Write all test cases for the repository before implementation.
  - Files: `tests/test_task_repository.py`
  - Action:
    1. Write `tests/test_task_repository.py` using `tmp_path` covering all repository methods.
    2. Run `pytest tests/test_task_repository.py -v` and save output as proof (tests will be red until 5.2 is done).
  - Expected outcome: `tests/test_task_repository.py` exists and pytest output is saved as proof of test execution.

- [x] 5.2 Implement `TaskRepository` (`repositories/task_repository.py`)
  - Objective: File-based JSON storage with atomic read-modify-write.
  - Files: `repositories/task_repository.py`
  - Action:
    1. Write `repositories/task_repository.py`.
    2. Run `pytest tests/test_task_repository.py -v` and save output as proof.
  - Expected outcome: pytest output confirms all repository tests pass green.

---

## Phase 6: Agent Service — TDD

- [x] 6.1 Write tests for agent service pure functions (`tests/test_agent_service.py`) — TDD
  - Objective: Write all test cases for agent logic before implementation.
  - Files: `tests/test_agent_service.py`
  - Action:
    1. Write `tests/test_agent_service.py` covering all branches of `select_next_task`, `calculate_productivity_score`, `generate_suggestion`, `decide`.
    2. Run `pytest tests/test_agent_service.py -v` and save output as proof (tests will be red until 6.3 is done).
  - Expected outcome: `tests/test_agent_service.py` exists and pytest output is saved as proof of test execution.

- [x] 6.2 Write property-based test for `calculate_productivity_score` (`tests/test_agent_service.py`) — TDD
  - Objective: Add a hypothesis property test verifying score is always in `[0.0, 1.0]`.
  - Files: `tests/test_agent_service.py`
  - Action:
    1. Append the hypothesis property test to `tests/test_agent_service.py`.
    2. Run `pytest tests/test_agent_service.py -v` and save output as proof (test will be red until 6.3 is done).
  - Expected outcome: pytest output is saved as proof showing the property test is collected and executed.

- [x] 6.3 Implement agent service (`services/agent_service.py`)
  - Objective: Pure, stateless functions — no I/O, no imports from repositories or FastAPI.
  - Files: `services/agent_service.py`
  - Action:
    1. Write `services/agent_service.py` with all four functions.
    2. Run `pytest tests/test_agent_service.py -v` and save output as proof.
  - Expected outcome: pytest output confirms all agent service tests pass green, including the hypothesis property test.

---

## Phase 7: Task Service — TDD

- [x] 7.1 Write tests for `TaskService` (`tests/test_task_service.py`) — TDD
  - Objective: Write all test cases for task service before implementation.
  - Files: `tests/test_task_service.py`
  - Action:
    1. Write `tests/test_task_service.py` with a mocked repository covering all branches.
    2. Run `pytest tests/test_task_service.py -v` and save output as proof (tests will be red until 7.2 is done).
  - Expected outcome: `tests/test_task_service.py` exists and pytest output is saved as proof of test execution.

- [x] 7.2 Implement `TaskService` (`services/task_service.py`)
  - Objective: Orchestrate task creation and completion; delegate all persistence to the injected repository.
  - Files: `services/task_service.py`
  - Action:
    1. Write `services/task_service.py`.
    2. Run `pytest tests/test_task_service.py -v` and save output as proof.
  - Expected outcome: pytest output confirms all task service tests pass green.

---

## Phase 8: API Route Handlers — TDD

- [x] 8.1 Write tests for task endpoints (`tests/test_api_tasks.py`) — TDD
  - Objective: Write all test cases for task HTTP endpoints before implementation.
  - Files: `tests/test_api_tasks.py`
  - Action:
    1. Write `tests/test_api_tasks.py` using `TestClient` with repository dependency overridden.
    2. Run `pytest tests/test_api_tasks.py -v` and save output as proof (tests will be red until 8.3 is done).
  - Expected outcome: `tests/test_api_tasks.py` exists and pytest output is saved as proof of test execution.

- [x] 8.2 Write tests for agent endpoint (`tests/test_api_agent.py`) — TDD
  - Objective: Write all test cases for the agent decision endpoint before implementation.
  - Files: `tests/test_api_agent.py`
  - Action:
    1. Write `tests/test_api_agent.py` using `TestClient` with repository dependency overridden.
    2. Run `pytest tests/test_api_agent.py -v` and save output as proof (tests will be red until 8.4 is done).
  - Expected outcome: `tests/test_api_agent.py` exists and pytest output is saved as proof of test execution.

- [x] 8.3 Implement task route handlers (`app/api/tasks.py`)
  - Objective: Thin HTTP handlers that delegate to `TaskService`; no business logic.
  - Files: `app/api/tasks.py`
  - Action:
    1. Write `app/api/tasks.py`.
    2. Run `pytest tests/test_api_tasks.py -v` and save output as proof.
  - Expected outcome: pytest output confirms all task endpoint tests pass green.

- [x] 8.4 Implement agent route handler (`app/api/agent.py`)
  - Objective: Thin HTTP handler that loads tasks from the repository and calls `decide()`.
  - Files: `app/api/agent.py`
  - Action:
    1. Write `app/api/agent.py`.
    2. Run `pytest tests/test_api_agent.py -v` and save output as proof.
  - Expected outcome: pytest output confirms all agent endpoint tests pass green.

---

## Phase 9: Application Entry Point

- [x] 9.1 Wire up FastAPI app (`app/main.py`)
  - Objective: Create the FastAPI application instance, register routers, middleware, and exception handlers.
  - Files: `app/main.py`
  - Action:
    1. Write `app/main.py`.
    2. Write `tests/test_main.py` that imports the app and asserts routes for `/tasks` and `/agent/decision` are registered.
    3. Run `pytest tests/test_main.py -v` and save output as proof.
  - Expected outcome: `tests/test_main.py` exists and pytest output confirms the app wires up correctly.

- [x] 9.2 Add `conftest.py` with shared test fixtures (`tests/conftest.py`)
  - Objective: Provide reusable fixtures to avoid duplication across test files.
  - Files: `tests/conftest.py`
  - Action:
    1. Write `tests/conftest.py` with TestClient fixture (dependency overrides), tmp_path store fixture, and sample task fixtures.
    2. Run `pytest tests/ -v` and save output as proof that all existing tests still pass with shared fixtures.
  - Expected outcome: pytest output confirms all tests pass with the shared conftest fixtures in place.

---

## Phase 10: Final Validation

- [x] 10.1 Run full test suite
  - Objective: Verify the complete implementation is green end-to-end.
  - Files: all test files
  - Action:
    1. Run `pytest tests/ -v --tb=short` and save output as proof.
  - Expected outcome: pytest output confirms 0 failures; hypothesis property test runs at least 100 examples.

- [x] 10.2 Manual smoke test via curl or HTTPie
  - Objective: Confirm the running server behaves correctly for the happy path.
  - Files: none (runtime verification)
  - Action: User starts the server manually with `uvicorn app.main:app --reload` and tests endpoints with curl or HTTPie.
  - Expected outcome: POST /tasks → 201, GET /agent/decision → 200 with all fields, POST /tasks/{id}/complete → 200; structured logs appear in terminal.
