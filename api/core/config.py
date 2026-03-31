"""Configuration loader.

Reads api/config.yaml as the base config, then applies environment variable
overrides for secrets and deployment-specific values.

Supported env var overrides (case-insensitive):
  OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE
  PG_HOST, PG_PORT, PG_DATABASE, PG_USER, PG_PASSWORD,
  PG_MIN_CONNECTIONS, PG_MAX_CONNECTIONS
  HOST, PORT, RELOAD, LOG_LEVEL, LOG_DIR, LOG_FILE_NAME
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml


def _find_config_yaml() -> Path:
    """Locate config.yaml relative to this file (api/config.yaml)."""
    return Path(__file__).resolve().parent.parent / "config.yaml"


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _apply_env_overrides(cfg: dict[str, Any]) -> None:
    """Overwrite cfg keys with values from environment variables."""
    _str_overrides = {
        "OPENAI_API_KEY": "openai_api_key",
        "OPENAI_MODEL": "openai_model",
        "PG_HOST": "pg_host",
        "PG_DATABASE": "pg_database",
        "PG_USER": "pg_user",
        "PG_PASSWORD": "pg_password",
        "HOST": "host",
        "LOG_LEVEL": "log_level",
        "LOG_FILE_NAME": "log_file_name",
        "LOG_DIR": "log_dir",
        "APP_NAME": "app_name",
        "LANGSMITH_API_KEY": "langsmith_api_key",
        "LANGCHAIN_API_KEY": "langsmith_api_key",
        "LANGSMITH_PROJECT": "langsmith_project",
        "LANGCHAIN_PROJECT": "langsmith_project",
        "LANGSMITH_ENDPOINT": "langsmith_endpoint",
    }
    _int_overrides = {
        "PG_PORT": "pg_port",
        "PG_MIN_CONNECTIONS": "pg_min_connections",
        "PG_MAX_CONNECTIONS": "pg_max_connections",
        "PORT": "port",
        "LOG_MAX_BYTES": "log_max_bytes",
        "LOG_BACKUP_COUNT": "log_backup_count",
    }
    _float_overrides = {
        "OPENAI_TEMPERATURE": "openai_temperature",
    }
    _bool_overrides = {
        "RELOAD": "reload",
        "LANGCHAIN_TRACING_V2": "langsmith_tracing",
    }

    for env_key, cfg_key in _str_overrides.items():
        val = os.environ.get(env_key)
        if val is not None:
            cfg[cfg_key] = val

    for env_key, cfg_key in _int_overrides.items():
        val = os.environ.get(env_key)
        if val is not None:
            cfg[cfg_key] = int(val)

    for env_key, cfg_key in _float_overrides.items():
        val = os.environ.get(env_key)
        if val is not None:
            cfg[cfg_key] = float(val)

    for env_key, cfg_key in _bool_overrides.items():
        val = os.environ.get(env_key)
        if val is not None:
            cfg[cfg_key] = val.lower() in ("true", "1", "yes")


def _load_dotenv(path: Path) -> None:
    """Minimal .env loader — sets env vars that are not already set."""
    if not path.exists():
        return
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip()
            # Don't overwrite vars already set in the real environment
            if key not in os.environ:
                os.environ[key] = value


class Settings:
    """Flat settings object loaded from config.yaml + env overrides."""

    def __init__(self, cfg: dict[str, Any]) -> None:
        # Application
        self.app_name: str = cfg["app_name"]
        self.log_level: str = cfg["log_level"]
        self.store_path: Path = Path(cfg["store_path"])

        # Server
        self.host: str = cfg["host"]
        self.port: int = int(cfg["port"])
        self.reload: bool = bool(cfg["reload"])

        # OpenAI
        self.openai_api_key: str = cfg["openai_api_key"]
        self.openai_model: str = cfg["openai_model"]
        self.openai_temperature: float = float(cfg["openai_temperature"])

        # LangSmith
        self.langsmith_tracing: bool = bool(cfg["langsmith_tracing"])
        self.langsmith_api_key: str = cfg["langsmith_api_key"]
        self.langsmith_project: str = cfg["langsmith_project"]
        self.langsmith_endpoint: str = cfg["langsmith_endpoint"]

        # Agent prompts
        self.agent_system_prompt: str = cfg["agent_system_prompt"]
        self.agent_user_prompt: str = cfg["agent_user_prompt"]
        self.agent_no_pending_message: str = cfg["agent_no_pending_message"]

        # Middleware / logging
        self.middleware_logger_name: str = cfg["middleware_logger_name"]
        self.log_event_request: str = cfg["log_event_request"]
        self.log_event_response: str = cfg["log_event_response"]
        self.log_dir: Path = Path(cfg["log_dir"])
        self.log_file_name: str = cfg["log_file_name"]
        self.log_max_bytes: int = int(cfg["log_max_bytes"])
        self.log_backup_count: int = int(cfg["log_backup_count"])

        # Error codes
        self.error_code_internal: str = cfg["error_code_internal"]
        self.error_code_not_found: str = cfg["error_code_not_found"]
        self.error_code_store_corrupted: str = cfg["error_code_store_corrupted"]
        self.error_code_validation: str = cfg["error_code_validation"]
        self.error_code_task_already_completed: str = cfg["error_code_task_already_completed"]
        self.error_msg_internal: str = cfg["error_msg_internal"]
        self.error_msg_store_corrupted: str = cfg["error_msg_store_corrupted"]
        self.error_msg_validation: str = cfg["error_msg_validation"]

        # Router
        self.tasks_prefix: str = cfg["tasks_prefix"]
        self.tasks_tag: str = cfg["tasks_tag"]
        self.agent_prefix: str = cfg["agent_prefix"]
        self.agent_tag: str = cfg["agent_tag"]
        self.agent_decision_path: str = cfg["agent_decision_path"]

        # Task model
        self.task_title_max_length: int = int(cfg["task_title_max_length"])
        self.task_priority_min: int = int(cfg["task_priority_min"])
        self.task_priority_max: int = int(cfg["task_priority_max"])
        self.task_title_empty_error: str = cfg["task_title_empty_error"]
        self.task_duration_min: float = float(cfg["task_duration_min"])

        # Exception messages
        self.exc_task_not_found_template: str = cfg["exc_task_not_found_template"]
        self.exc_task_already_completed_template: str = cfg["exc_task_already_completed_template"]

        # PostgreSQL
        self.pg_host: str = cfg["pg_host"]
        self.pg_port: int = int(cfg["pg_port"])
        self.pg_database: str = cfg["pg_database"]
        self.pg_user: str = cfg["pg_user"]
        self.pg_password: str = cfg["pg_password"]
        self.pg_min_connections: int = int(cfg["pg_min_connections"])
        self.pg_max_connections: int = int(cfg["pg_max_connections"])


def _build_settings() -> Settings:
    # Load .env first so its values are available as env vars
    _load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    cfg = _load_yaml(_find_config_yaml())
    _apply_env_overrides(cfg)
    return Settings(cfg)


settings: Settings = _build_settings()
