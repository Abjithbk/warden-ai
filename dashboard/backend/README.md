# Warden Dashboard Backend

FastAPI service for the Warden dashboard: incident list and detail, human
approve/reject, Slack approval actions, overview stats, and an audit trail
with CSV export.

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- A database: PostgreSQL (Supabase) or a local SQLite file for quick tries
- Docker (optional, only to run the container)

## Setup

Run all commands inside `dashboard/backend/`.

1. Install dependencies:

```bash
   uv sync
```

2. Create your settings file and fill in the values:

```bash
   cp .env.example .env
```

   Never commit `.env`. It contains secrets.

3. Create the database tables:

```bash
   uv run alembic upgrade head
```

4. Add realistic fake incidents:

```bash
   uv run python scripts/seed.py
```

   **Warning:** this deletes all existing incidents and related rows in the
   database that `DATABASE_URL` points to, then recreates demo data. Never run
   it against a database that holds data you want to keep.

## Run

```bash
uv run uvicorn backend.main:app --reload
```

- Health check: http://localhost:8000/healthz
- API docs (Swagger): http://localhost:8000/docs

## Test and lint

```bash
uv run pytest
uv run ruff check .
uv run mypy src
```

Tests use an in-memory SQLite database and never touch your real data.

## Docker

```bash
docker build -t warden-backend .
docker run --rm -p 8000:8000 --env-file .env warden-backend
```

The image runs as a non-root user. Docker does not strip quotes from
`--env-file`, so write values in `.env` without quotes if you use it this way.

## Environment variables

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `DATABASE_URL` | Yes | none | Database connection, e.g. `postgresql+psycopg://user:pass@host:5432/warden` |
| `SLACK_SIGNING_SECRET` | For Slack | empty | Verifies Slack requests. If empty, Slack requests are rejected |
| `ENVIRONMENT` | No | `local` | `local`, `staging` or `production`. Controls log format |
| `APP_NAME` | No | `Warden Dashboard API` | Title shown in `/docs` |
| `API_V1_PREFIX` | No | `/api/v1` | URL prefix for versioned routes |
| `CORS_ORIGINS` | No | `["http://localhost:5173"]` | Allowed frontend origins (JSON list) |
| `RATE_LIMIT_DEFAULT` | No | `60/minute` | Default API rate limit |

## API overview

All routes are under `/api/v1` except `/healthz`. See `/docs` for full details.

| Method | Path | Purpose |
|---|---|---|
| GET | `/overview/stats` | Dashboard summary numbers |
| GET | `/overview/recent-actions` | Latest remediation actions |
| GET | `/incidents` | List incidents (filters: `status`, `severity`) |
| GET | `/incidents/{id}` | Full incident trace |
| POST | `/incidents/{id}/approve` | Approve remediation |
| POST | `/incidents/{id}/reject` | Reject remediation |
| POST | `/slack/actions` | Slack button callback |
| GET | `/audit` | Audit log |
| GET | `/audit/export` | Audit log as CSV |