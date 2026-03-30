from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Application
    app_name: str = "Productivity Agent API"
    log_level: str = "INFO"
    store_path: Path = Path("data/store.json")

    # OpenAI / LangChain
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    openai_temperature: float = 0.0

    # Agent prompts
    agent_system_prompt: str = (
        "You are a productivity assistant agent. "
        "You are given a list of tasks, each with a priority (1-5), an optional deadline (UTC ISO datetime), "
        "and an optional duration_hours (estimated effort in hours, e.g. 1.5 means 90 minutes). "
        "Your job is to: "
        "1. Use the available tools to analyse the tasks. "
        "2. Identify the single best next task to work on by reasoning across ALL three dimensions: "
        "   - Urgency: how close is the deadline? Is there enough time left to complete it given its duration_hours? "
        "   - Effort: how many hours will it take? Should a quick task be done first to free up focus? "
        "   - Importance: what is the priority level? "
        "3. Calculate the current productivity score. "
        "4. Return a JSON object with exactly these fields: "
        "next_task_id (the id of the recommended task or null if none), "
        "productivity_score (float between 0.0 and 1.0), "
        "suggestion (a short actionable string advising the user what to do next), "
        "reasoning (explain how you weighed urgency, effort, and priority to reach your decision — "
        "call out any deadline risks or effort trade-offs explicitly). "
        "Always respond with ONLY the JSON object — no markdown, no extra text."
    )
    agent_user_prompt_template: str = "Analyse these tasks and give me a decision:\n{tasks_json}"
    agent_no_pending_message: str = "No pending tasks."

    # Middleware / logging
    middleware_logger_name: str = "app.middleware"
    log_event_request: str = "request"
    log_event_response: str = "response"

    # Error codes and messages
    error_code_internal: str = "INTERNAL_ERROR"
    error_code_not_found: str = "TASK_NOT_FOUND"
    error_code_store_corrupted: str = "STORE_CORRUPTED"
    error_code_validation: str = "VALIDATION_ERROR"
    error_msg_internal: str = "An unexpected error occurred"
    error_msg_store_corrupted: str = "Data store is corrupted"
    error_msg_validation: str = "Request validation failed"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False

    # Router prefixes and tags
    tasks_prefix: str = "/tasks"
    tasks_tag: str = "tasks"
    agent_prefix: str = "/agent"
    agent_tag: str = "agent"
    agent_decision_path: str = "/decision"

    # Task model defaults
    task_title_max_length: int = 200
    task_priority_min: int = 1
    task_priority_max: int = 5
    task_title_empty_error: str = "title must not be empty or whitespace"
    task_duration_min: float = 0.25  # minimum duration in hours (15 minutes)

    # PostgreSQL
    pg_host: str = "localhost"
    pg_port: int = 5437
    pg_database: str = "worky"
    pg_user: str = "postgres"
    pg_password: str = ""
    pg_min_connections: int = 2
    pg_max_connections: int = 10

    # Exception messages
    exc_task_not_found_template: str = "Task {task_id} not found"
    exc_task_already_completed_template: str = "Task {task_id} is already completed"
    error_code_task_already_completed: str = "TASK_ALREADY_COMPLETED"


settings = Settings()
