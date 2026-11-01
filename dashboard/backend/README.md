# Warden Dashboard Backend

> **Autonomous SRE Human-in-the-Loop & Incident Governance Service**  
> Built with **FastAPI**, **SQLAlchemy 2.0**, **Alembic**, and **Pydantic v2**, managed using **uv**.

The Dashboard Backend serves as the central API and governance layer for Warden. It persists incident detections, exposes AI reasoning traces from LangGraph, coordinates OPA policy decisions, executes human-in-the-loop approvals (both via web dashboard and interactive Slack notifications), records an append-only audit trail, and serves telemetry to the React frontend.

---

## Table of Contents

- [Features](#features)
- [Directory Structure](#directory-structure)
- [Domain Model & Architecture](#domain-model--architecture)
- [API Design & Endpoints](#api-design--endpoints)
- [Security & Governance](#security--governance)
- [Quickstart & Setup](#quickstart--setup)
- [Developer Workflow (Makefile)](#developer-workflow-makefile)
- [Docker & Containerization](#docker--containerization)
- [Configuration Reference](#configuration-reference)

---

## Features

- **Thin-Router / Thick-Service Layering**: Complete separation between HTTP request parsing, business validation, and database operations.
- **Incident Governance Trace**: Persists the full pipeline lifecycle: `Detection` $\to$ `AgentDecision` $\to$ `PolicyCheck` $\to$ `ApprovalRequest` $\to$ `RemediationAction` $\to$ `AuditLogEntry`.
- **Bidirectional Human Gate**: Approvals and rejections are actioned seamlessly from either the Web Dashboard or Slack interactive buttons with **409 Conflict race-condition prevention**.
- **HMAC-SHA256 Slack Security**: Replay-attack prevention and cryptographically verified webhook requests from Slack.
- **Rate-Limiting & Protection**: Distributed rate limiting via SlowAPI and strict CORS controls.
- **Audit Compliance**: Append-only audit logging with streaming CSV export for governance reporting.

---

## Directory Structure

This service follows an **industrial-level src-layout**:

```text
dashboard/backend/
├── pyproject.toml              # Dependencies, project metadata, and tool configs (ruff, pytest)
├── uv.lock                     # Deterministic pinned lockfile
├── .python-version             # Python version pin (3.12+)
├── .env.example                # Documented environment variable template
├── .gitignore                  # Backend-specific ignore rules
├── Dockerfile                  # Multi-stage, non-root production Docker image
├── docker-compose.yml          # Local development stack (PostgreSQL + Backend)
├── Makefile                    # Developer shortcut tasks (make dev, make test, etc.)
├── alembic.ini                 # Alembic configuration (script_location = migrations)
├── README.md                   # ← THIS FILE
├── migrations/                 # Alembic database schema migrations
│   ├── env.py                  # Migration environment & metadata binding
│   ├── script.py.mako          # Migration template
│   └── versions/               # Historical schema migration files
├── scripts/
│   └── seed.py                 # Realistic demo incident generator with full trace
├── src/
│   └── backend/
│       ├── __init__.py
│       ├── main.py             # FastAPI application factory & lifespan
│       ├── config.py           # Pydantic Settings configuration loader
│       ├── dependencies.py     # Shared FastAPI Depends (DB session, API key auth)
│       ├── logging.py          # Structured JSON / console logger
│       ├── core/
│       │   ├── __init__.py
│       │   ├── middleware.py   # CORS, SlowAPI rate limiting, error handlers
│       │   └── security.py     # HMAC Slack verification & Dashboard auth
│       ├── db/
│       │   ├── __init__.py
│       │   ├── base.py         # Declarative Base
│       │   └── session.py      # SQLAlchemy Engine & SessionLocal maker
│       ├── api/
│       │   ├── __init__.py
│       │   ├── router.py       # Root API router assembling health and v1 endpoints
│       │   └── v1/
│       │       ├── __init__.py
│       │       ├── health.py   # Liveness/readiness probe (/healthz)
│       │       ├── incidents.py# Incident list, detail trace, approve/reject
│       │       ├── overview.py # High-level system stats & recent actions
│       │       ├── audit.py    # Audit trail query & CSV export
│       │       └── slack.py    # Inbound Slack interactive button callbacks
│       ├── models/             # SQLAlchemy 2.0 ORM domain models
│       │   ├── __init__.py     # Re-exports models for Alembic autogenerate
│       │   ├── enums.py        # Centralized status, severity, and action enums
│       │   ├── incident.py     # Incident, Detection, Decision, Policy, Approval, Action
│       │   └── audit.py        # AuditLogEntry model
│       ├── schemas/            # Pydantic v2 DTOs (Request / Response validation)
│       │   ├── __init__.py
│       │   ├── incident.py     # IncidentOut, IncidentListOut, IncidentDetailOut
│       │   ├── approval.py     # ApproveRequest, RejectRequest, ActionResponse
│       │   ├── overview.py     # OverviewStatsOut, RecentActionOut
│       │   ├── audit.py        # AuditLogQuery, AuditEntryOut
│       │   └── slack.py        # SlackPayload, SlackNotifyOut
│       └── services/           # Core business logic layer
│           ├── __init__.py
│           ├── incident_service.py # Querying incidents, filtering, trace reconstruction
│           ├── approval_service.py # State machine for approve/reject & race guards
│           ├── audit_service.py    # Append-only logging & CSV streaming
│           ├── overview_service.py # Sentinel score calculation & dashboard telemetry
│           └── slack_service.py    # Slack Block Kit building & outbound webhooks
└── tests/                      # Automated test suite (isolated from src/)
    ├── conftest.py             # SQLite in-memory DB fixture & TestClient setup
    ├── unit/                   # Isolated unit tests
    └── integration/            # End-to-end API integration tests
```

---

## Domain Model & Architecture

Every incident detected in the cluster creates an `Incident` entity. Child records link directly via `incident_id`, producing an immutable end-to-end trace:

```mermaid
erDiagram
    INCIDENT ||--o{ DETECTION : "triggered by"
    INCIDENT ||--o{ AGENT_DECISION : "analyzed by"
    INCIDENT ||--o{ POLICY_CHECK : "validated by"
    INCIDENT ||--o{ APPROVAL_REQUEST : "gated by"
    INCIDENT ||--o{ REMEDIATION_ACTION : "executed by"
    INCIDENT ||--o{ AUDIT_LOG_ENTRY : "audited by"

    INCIDENT {
        int id PK
        string title
        string service
        string namespace
        string severity "low | medium | high | critical"
        string status "active | awaiting_approval | remediating | resolved | failed"
        datetime created_at
        datetime resolved_at
    }

    DETECTION {
        int id PK
        int incident_id FK
        string source "prometheus | k8s"
        string signal "OOMKilled | HighLatency"
        json raw_payload
    }

    AGENT_DECISION {
        int id PK
        int incident_id FK
        json reasoning_trace "Step-by-step LangGraph reasoning"
        string proposed_action "restart_pod | rollout_restart | scale_deployment | rollback_deployment"
        string target
        float confidence
    }

    POLICY_CHECK {
        int id PK
        int incident_id FK
        int agent_decision_id FK
        string verdict "approved | denied | review_required"
        string reason
        string policy_name
    }

    APPROVAL_REQUEST {
        int id PK
        int incident_id FK
        int policy_check_id FK
        string status "pending | approved | rejected | timed_out"
        string actioned_by
        datetime actioned_at
        string slack_channel
        string slack_message_ts
    }

    REMEDIATION_ACTION {
        int id PK
        int incident_id FK
        int approval_request_id FK
        string action_type
        string target
        string status "pending | running | succeeded | failed"
        json result
    }

    AUDIT_LOG_ENTRY {
        int id PK
        int incident_id FK
        string actor "dashboard:user | slack:U123 | system"
        string action "incident_created | approved | rejected | action_succeeded"
        json detail
    }
```

---

## API Design & Endpoints

All application routes are prefixed with `/api/v1` except the root health check. Interactive Swagger documentation is available at `http://localhost:8000/docs`.

### 1. Health & Telemetry
| Method | Endpoint | Description | Response |
| :--- | :--- | :--- | :--- |
| `GET` | `/healthz` | Kubernetes liveness/readiness probe | `{"status": "ok"}` |
| `GET` | `/` | Service root confirmation | `{"status": "Warden backend is running"}` |

### 2. Overview Dashboard
| Method | Endpoint | Description | Key Query Params |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/overview/stats` | Top-level metrics (sentinel score, active counts, pending approvals) | — |
| `GET` | `/api/v1/overview/recent-actions` | Latest remediation actions across all services | `limit` (default: 10) |

### 3. Incidents
| Method | Endpoint | Description | Key Query Params / Body |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/incidents` | Paginated incident list | `status`, `severity`, `limit`, `offset` |
| `GET` | `/api/v1/incidents/{id}` | Full incident pipeline detail with all child traces | — |
| `POST` | `/api/v1/incidents/{id}/approve` | Approve high-risk remediation action | `{"actioned_by": "username"}` |
| `POST` | `/api/v1/incidents/{id}/reject` | Reject high-risk remediation action | `{"actioned_by": "username", "reason": "text"}` |

### 4. Slack Human-in-the-Loop
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/v1/slack/actions` | Inbound interactive button callback (Approve / Reject clicked in Slack) |
| `GET` | `/api/v1/slack/status` | Current Slack integration health and bot configuration state |
| `POST` | `/api/v1/slack/test` | Trigger a test Slack Block Kit message to verified channel |

### 5. Audit Trail & Compliance
| Method | Endpoint | Description | Key Query Params |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/audit` | Paginated audit trail records | `incident_id`, `actor`, `limit`, `offset` |
| `GET` | `/api/v1/audit/export` | Stream full audit log as a CSV attachment | `incident_id`, `actor` |

---

## Security & Governance

### Anti-Race Condition Protection (409 Conflict)
When an incident requires human approval, Warden notifies both the Dashboard UI and the Slack incident channel simultaneously. 
- If an engineer approves via Slack and another rejects via Dashboard simultaneously, `approval_service` checks `actioned_at`.
- The first action locks the row. The losing action immediately receives **HTTP 409 Conflict** (`"This approval request has already been actioned"`), completely eliminating split-brain remediation.

### Slack Cryptographic Verification
Inbound webhooks to `/api/v1/slack/actions` verify the `X-Slack-Signature` header:
1. Rejects any request older than 5 minutes (`X-Slack-Request-Timestamp`) to prevent replay attacks.
2. Computes `HMAC-SHA256(v0:{timestamp}:{body}, SLACK_SIGNING_SECRET)`.
3. Verifies match using `hmac.compare_digest` (constant time to prevent timing attacks).

---

## Quickstart & Setup

### Prerequisites
- **Python 3.12+**
- **[uv](https://docs.astral.sh/uv/)** installed
- PostgreSQL (or local SQLite for lightweight testing)

### 1. Install Dependencies
```bash
cd dashboard/backend
uv sync
```

### 2. Configure Environment
```bash
cp .env.example .env
```
Edit `.env` to configure your database connection string and secrets.

### 3. Run Migrations
```bash
uv run alembic upgrade head
```

### 4. Seed Demo Data
Populate the database with realistic incidents, LangGraph reasoning traces, policy checks, and approvals:
```bash
uv run python scripts/seed.py
```

### 5. Launch Development Server
```bash
uv run uvicorn backend.main:app --reload --port 8000
```
- API Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health Probe: [http://localhost:8000/healthz](http://localhost:8000/healthz)

---

## Developer Workflow (Makefile)

If `make` is installed on your machine:

| Command | Action |
| :--- | :--- |
| `make dev` | Start local uvicorn server with hot reloading |
| `make test` | Run pytest test suite |
| `make lint` | Run Ruff linter |
| `make format` | Automatically fix and format code with Ruff |
| `make migrate` | Apply latest Alembic database migrations |
| `make seed` | Re-seed database with realistic demo incidents |

*(On Windows without `make`, you can run the commands directly using `uv run ...`)*.

---

## Docker & Containerization

### Building the Production Container
The Dockerfile uses a multi-stage build that drops unnecessary compilation dependencies and runs as an unprivileged system user (`appuser`):

```bash
docker build -t warden-backend .
```

### Running with Docker Compose
To launch PostgreSQL and the Backend together locally:
```bash
docker compose up -d
```

---

## Configuration Reference

| Variable | Type | Default | Description |
| :--- | :---: | :---: | :--- |
| `DATABASE_URL` | String | *Required* | SQLAlchemy connection URL (e.g., `postgresql+psycopg://user:pass@localhost:5432/warden` or `sqlite:///./warden.db`) |
| `ENVIRONMENT` | String | `local` | Environment name (`local`, `staging`, `production`). Switches structured log formats. |
| `APP_NAME` | String | `Warden Dashboard API` | Application title exposed in OpenAPI documentation. |
| `API_V1_PREFIX` | String | `/api/v1` | URL path prefix for version 1 routers. |
| `CORS_ORIGINS` | JSON list | `["http://localhost:5173"]` | Authorized frontend origin domains. |
| `RATE_LIMIT_DEFAULT` | String | `60/minute` | Default SlowAPI rate limit threshold. |
| `SLACK_SIGNING_SECRET` | String | `""` | Secret key used to verify incoming Slack webhooks. |
| `SLACK_BOT_TOKEN` | String | `""` | Bot token (`xoxb-...`) used for posting approval cards to Slack. |
| `SLACK_CHANNEL_ID` | String | `""` | Target Slack channel ID for automated incident broadcasts. |
| `DASHBOARD_API_KEY` | String | `""` | Optional shared bearer token for authenticating dashboard requests. |
| `DASHBOARD_BASE_URL` | String | `http://localhost:5173`| Frontend URL included in Slack buttons for deep-linking. |