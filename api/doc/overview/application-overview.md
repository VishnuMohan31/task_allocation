# Application overview

This document describes what the **Productivity Agent API** does, how the pieces fit together, and how the LLM agent behaves relative to the REST surface.

---

## Purpose

The service helps a team **manage tasks** stored in **PostgreSQL** and exposes a **GET** endpoint that asks an **LLM agent** to:

- Assess overall productivity (a score from **0.0** to **1.0**).
- Pick a **single next task** (by id) when appropriate.
- Return a short **suggestion** and **reasoning** text.

The UI or other clients consume JSON; the agent does not replace CRUD on tasks—they use the tasks API separately.

---

## REST API (FastAPI)

| Area | Role |
|------|------|
| **`GET /tasks/`** | Lists tasks with optional filters (status, priority, sprint, assignee, phase). |
| **`GET /tasks/{id}`** | Fetches one task. |
| **`GET /agent/decision`** | Loads the current task list from the DB via `TaskService`, then runs **`decide(service)`** and returns an **`AgentDecision`** (next task object or `null`, score, suggestion, reasoning). |

Configuration is centralized in **`config.yaml`**, with overrides from **environment variables** (see `core/config.py`). **LangSmith** tracing can be enabled when `langsmith_tracing` is true and API keys are set; the app sets `LANGCHAIN_*` env vars during startup.

---

## Data layer

- **`PostgresTaskRepository`** uses **asyncpg** and a connection pool created in the FastAPI **lifespan** (`init_pool` / `close_pool`).
- If code paths run **without** that lifespan (for example **LangGraph dev**), **`list_tasks`** / **`get_task`** can **lazy-initialize** the pool on first use, as long as `PG_*` settings are valid.

---

## Agent design (`services/agent_service.py`)

### Graph (LangGraph ReAct)

- Built with **`create_react_agent`** and **ChatOpenAI** (model and temperature from settings).
- **Tools:**
  - **`get_tasks`** — **Async.** Calls **`await service.list_tasks(None)`** and returns a JSON string of normalized task fields (same shape everywhere via **`tasks_agent_json`**). This is the **live database** list, not text pasted by the user.
  - **`get_current_date_context`** — Returns today’s **ISO date** and **weekday** so the model can compare **`due_date`** without guessing “today.”

### HTTP orchestration (`decide`)

- **`decide` is async.** It builds **system** + **user** messages from **`agent_system_prompt`** and **`agent_user_prompt`** (no embedded task blob in the user message).
- It runs **`await agent.ainvoke(...)`** (up to two attempts).
- After each run it **parses the final assistant message** as JSON and **validates** `productivity_score`, `suggestion`, and `next_task_id` shape.
- If validation fails, it appends a **user** message with fixed feedback and **invokes again**.
- If both attempts fail, it returns a **fallback** `AgentDecision`.
- To resolve **`next_task_id`** to a full **`Task`** model for the response, it calls **`await service.list_tasks(None)`** again after each attempt so the API returns proper objects from the DB.

**LangGraph Studio** (`langgraph dev`) loads only the **compiled graph** from **`agent_graph.py`**. It does **not** execute the outer **`decide`** retry loop; that exists only on the **FastAPI** path.

---

## Local development files

- **`langgraph.json`** — Declares the **`agent`** graph and points **`env`** at **`./.env`**.
- **`agent_graph.py`** — Exports **`graph = build_agent_graph(_service)`** using the same **`TaskService`** instance as the tasks router.
- **`requirements-dev.txt`** — Adds **`langgraph-cli[inmem]`** for **`langgraph dev`**.

---

## Frontend (outside this folder)

A separate UI (for example under `../ui`) may call **`GET /agent/decision`** and **`/tasks/`**. CORS in `app/main.py` allows **`http://localhost:3000`** by default.
