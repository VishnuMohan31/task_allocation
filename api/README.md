# Productivity Agent API

FastAPI service for tasks (PostgreSQL) and an LLM-backed **productivity agent** that recommends a next task, score, and suggestion.

## Documentation

| Guide | File |
|--------|------|
| Run FastAPI + LangGraph Studio | [doc/run/running-the-application.md](doc/run/running-the-application.md) |
| What the app does (architecture, agent) | [doc/overview/application-overview.md](doc/overview/application-overview.md) |
| Index of `doc/` | [doc/README.md](doc/README.md) |

**Note:** `README.md` here is only the default file Git hosts show when you open the `api` folder. The detailed guides use explicit names above so you can link to them directly.

## Quick start (FastAPI)

1. Python 3.11+ recommended.
2. Copy or edit `config.yaml` and create `api/.env` (see [doc/run/running-the-application.md](doc/run/running-the-application.md)).
3. From the **`api`** directory:

```bash
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

4. Open `http://localhost:8000/docs` for interactive API docs.

## Project layout (high level)

- `app/` — FastAPI routers and lifespan (DB pool, optional LangSmith tracing).
- `core/` — Settings loaded from `config.yaml` plus environment overrides.
- `models/` — Pydantic models for tasks and agent responses.
- `repositories/` — PostgreSQL access (asyncpg).
- `services/` — Task service and agent (`decide`, LangGraph ReAct graph, tools).
- `agent_graph.py` + `langgraph.json` — entry for local **LangGraph dev** / Studio (see [doc/run/running-the-application.md](doc/run/running-the-application.md)).

## Dependencies

- **Runtime:** `requirements.txt`
- **LangGraph Studio locally:** `requirements-dev.txt` (includes `langgraph-cli[inmem]`)
