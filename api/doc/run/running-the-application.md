# Running the application

Two ways to run agent-related code: the **HTTP API** (production-style) and **LangGraph dev** (local graph + Studio). Both need Python dependencies, `config.yaml`, and a reachable PostgreSQL instance unless you only mock tests.

---

## 1. FastAPI (REST API)

### Prerequisites

- **PostgreSQL** running, with schema matching what `repositories/task_repository.py` expects (`public.tasks`, etc.).
- **`api/config.yaml`** present (defaults; secrets usually overridden by env).
- **`api/.env`** (optional but typical) for secrets. The app loads `.env` before YAML; env vars override config. Commonly set:
  - `OPENAI_API_KEY`
  - `PG_HOST`, `PG_PORT`, `PG_DATABASE`, `PG_USER`, `PG_PASSWORD`
  - Optionally `LANGSMITH_API_KEY` / `LANGCHAIN_API_KEY`, `LANGCHAIN_TRACING_V2`, `LANGCHAIN_PROJECT` for tracing

### Install and start

From the **`api`** directory (the folder that contains `app/`, `config.yaml`, and `requirements.txt`):

```bash
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Or use the port/host from `config.yaml` (`port`, `host`, `reload`).

### Verify

- **Swagger UI:** `http://localhost:8000/docs`
- **List tasks:** `GET /tasks/`
- **Agent decision:** `GET /agent/decision` (calls OpenAI; requires valid `OPENAI_API_KEY` and DB)

On startup, the app **initializes the DB pool** in the FastAPI lifespan. The agent’s `get_tasks` tool uses the same `TaskService` / repository as the tasks API.

---

## 2. LangGraph dev (Studio, graph view)

Use this to attach **LangSmith Studio** to a local Agent Server and step through the **compiled graph** (`agent_graph.py`). This is **not** the same process as Uvicorn; it listens on port **2024** by default.

### Prerequisites

Same **`.env`** / DB / OpenAI expectations as above so `get_tasks` can query PostgreSQL. The repository can **lazy-initialize** the pool on first query if the FastAPI lifespan never ran, but credentials must still be valid.

### Install and start

From **`api`**:

```bash
pip install -r requirements-dev.txt
langgraph dev --allow-blocking
```

**Why `--allow-blocking`:** LangGraph’s dev server flags synchronous calls inside async runs. LangChain / OpenAI stacks often trigger that (for example via `os.getcwd()` or tokenizers). The flag is the supported way to run locally without false-positive `BlockingError` during development.

### Connect Studio

The CLI prints a **Studio** URL, typically:

`https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024`

Use **graph** mode as needed. Provide **system** + **user** messages consistent with `config.yaml` (`agent_system_prompt`, `agent_user_prompt`). The model should call **`get_tasks`** to load tasks from the database (no pasted task JSON required).

### Relationship to FastAPI

| | FastAPI | LangGraph dev |
|---|---------|----------------|
| **Port** | 8000 (default) | 2024 (default) |
| **Entry** | `app.main:app` | `langgraph.json` → `agent_graph.py:graph` |
| **Retry / validation loop** | Yes, in `decide()` | No — raw graph only; Studio sees ReAct + tools |

You may run **both** at once on different ports; they are independent processes.
