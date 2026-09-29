# Warden

**An Autonomous SRE Agent with Safety Guardrails for Production Incident Remediation**

Warden is an AI agent that watches a live Kubernetes environment, reasons about incidents using a large language model, and remediates them automatically — inside a strict, auditable safety boundary. Every autonomous action is checked by a policy engine and, when risky, requires human approval before touching production.

---

## The Problem

Incident response today is manual and slow. Engineers correlate dashboards, logs, and traces under pressure, often at odd hours, before applying a fix. Many of these fixes are repetitive — restart, scale, rollback — yet still gated on a human being awake and available. At the same time, giving an AI agent unrestricted access to Kubernetes or cloud APIs is dangerous, since a wrong action can cascade faster than a human can intervene.

**Warden's goal:** an agent that is fast and context-aware like automation, but bounded and auditable like a well-governed human process.

---

## Architecture

```
Microservices (Kind cluster, Google Online Boutique)
│
▼
Prometheus + OpenTelemetry (metrics) ──► OTel Collector → Tempo → MinIO (traces)
│
▼
Incident Detector (burn-rate / multi-window alerting, SLO error-budget style)
│
▼
Warden Agent (LangGraph + LLM, RAG-grounded)
│
▼
OPA Policy Check
│
├── Low risk → Auto-execute
└── High risk → Human Approval (Slack + Dashboard)
│
▼
Kubernetes Executor
│
▼
Rollback Monitor (verify → revert if unresolved)
│
▼
Dashboard (live status + audit log)
```

---

## Key Capabilities

- **Incident detection** — burn-rate / multi-window alerting over live Prometheus metrics (SLO error-budget methodology, not static thresholds), grounded in the Google SRE Workbook
- **AI reasoning** — a LangGraph agent, grounded via RAG, correlates metrics and traces and drafts a remediation plan from real system context
- **Policy guardrails** — every proposed action is checked against OPA rules (e.g. minimum replica counts, protected namespaces) before execution
- **Human-in-the-loop** — high-risk actions pause for explicit approval via Slack interactive buttons and a live dashboard (combined by design — Slack for speed, Dashboard as the system of record)
- **Auto-rollback** — if a fix doesn't resolve the incident within a timeout, Warden reverts it automatically
- **Chaos validation** — fault injection via Chaos Mesh (plus manual pod-kill/network-delay) proves the full detect → decide → guard → act → rollback loop

---

## Tech Stack

| Layer              | Technology                                       |
| ------------------ | ------------------------------------------------ |
| Cluster            | Kind (Kubernetes in Docker), 3-node               |
| Monitoring         | Prometheus, Grafana, OpenTelemetry                |
| Tracing            | OTel Collector, Tempo, MinIO (S3-compatible store)|
| Agent              | LangGraph, LangChain, Groq (`openai/gpt-oss-120b`)|
| Policy             | Open Policy Agent (OPA) / Rego                   |
| Executor           | Python Kubernetes client                         |
| Human approval     | Slack (interactive buttons) + Dashboard          |
| Dashboard backend  | Python, FastAPI, managed with **uv**             |
| Dashboard frontend | React (Vite), managed with **pnpm**              |
| Chaos testing      | Chaos Mesh, k6                                    |

---

## Repository Structure

```
warden-ai/
├── README.md
├── .gitignore
├── docs/ # architecture notes, ADRs, diagrams, meeting notes
├── cluster/ # Kind cluster config
│ └── kind-config.yaml
├── monitoring/ # Prometheus, Grafana, OTel, Tempo configs
│ ├── prometheus/
│ └── grafana/dashboards/
├── detector/ # Incident detection logic (burn-rate alerting)
├── agent/ # LangGraph agent, prompts, RAG
│ ├── graph.py
│ ├── prompts/
│ └── rag/
├── policies/ # OPA / Rego policy files
├── executor/ # Executes approved actions on the cluster
│ ├── k8s_client.py
│ └── actions.py
├── rollback/ # Snapshot, verification, rollback logic
│ ├── snapshot.py
│ ├── verifier.py
│ └── rollback_manager.py
├── dashboard/ # Human approval web app
│ ├── backend/ # FastAPI app (managed with uv)
│ │ ├── pyproject.toml
│ │ ├── uv.lock
│ │ └── src/backend/
│ └── frontend/ # React app (Vite, managed with pnpm)
│ ├── src/
│ └── package.json
├── chaos/ # Fault injection scenarios, load scripts
├── tests/ # Unit and integration tests
├── pyproject.toml # Root Python project — managed with uv
└── uv.lock
```

> The demo application Warden monitors (Google Online Boutique, `GoogleCloudPlatform/microservices-demo`) is deployed separately to the `warden-demo` namespace and is not vendored into this repo. Instrumented service source will be published as a branch on a fork, linked here once finalized.

---

## Getting Started

### Prerequisites

- Docker Desktop
- kubectl
- Kind
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) — Python package/project manager
- Node.js ^20.19.0 or >=22.12.0 and [pnpm](https://pnpm.io/)
- A Groq API key

> The dashboard backend and frontend can run locally during development — Docker/Kind is needed for the cluster components.

### 1. Clone the repo
```bash
git clone https://github.com/Abjithbk/warden-ai.git
cd warden
```

### 2. Set up environment variables
Create a `.env` file inside `dashboard/backend/` (never commit this — it's gitignored):
```
LLM_API_KEY=your_key_here
KUBE_CONTEXT=kind-warden
```

### 3. Run the backend
```bash
cd dashboard/backend
uv run uvicorn backend.main:app --reload --port 8000
```
`uv` automatically creates a virtual environment and installs dependencies from `pyproject.toml` on first run. Visit `http://localhost:8000` — you should see `{"status": "Warden backend is running"}`. Interactive API docs are available at `http://localhost:8000/docs`.

To add a new backend dependency later:
```bash
uv add <package-name>
```

### 4. Run the frontend
```bash
cd dashboard/frontend
pnpm install
pnpm run dev
```
The dashboard should now be available at `http://localhost:5173`, talking to the FastAPI backend at `http://localhost:8000`.

### 5. (Later) Create the project's Kubernetes cluster
Only needed once you start deploying sample microservices for Warden to monitor:
```bash
kind create cluster --config cluster/kind-config.yaml --name warden-cluster
```

---

## Project Status

Under active development for a final-year capstone project. See `docs/` for design notes and `TASKS.md` for the current milestone tracker.

---

## Team

- Johny — [role/focus area]
- Abjith — [role/focus area]
- aiswaryanair79 — [role/focus area]

---

## References

See `docs/references.md` for the literature survey sources used in this project.