# Warden — Project Task Tracker

**Autonomous SRE Agent with Safety Guardrails for Production Incident Remediation**

---

## Milestone 1: Detect and See (Foundation — no AI yet) — ✅ CLOSED

**Goal:** Working Kubernetes cluster with real metrics flowing into a dashboard.

- [x] Install Docker, Kind, kubectl, Helm
- [x] Create `cluster/kind-config.yaml` (3-node, cluster `warden`, context `kind-warden`)
- [x] Spin up local Kind cluster
- [x] Deploy Google Online Boutique demo app to `warden-demo` namespace
- [x] Instrument `frontend` and `checkoutservice` to expose Prometheus metrics
- [x] Install `kube-prometheus-stack` via Helm (Prometheus + Grafana separately)
- [x] Confirm Prometheus scraping both instrumented services (Targets UI, UP)
- [x] Build Grafana dashboard: "Warden — Service Overview" (request rate, p95 latency)
- [x] Manually kill a pod and confirm it's visible on the dashboard
- [x] Document setup steps and gotchas (see `decisions-and-learnings.md`)

## Milestone 2: Tracing Pipeline — ✅ CLOSED

- [x] OTel Collector deployed (contrib image, Helm)
- [x] Tempo + MinIO (S3-compatible backend) deployed
- [x] Fixed `unknown_service:*` naming issue via `OTEL_SERVICE_NAME`
- [x] Real traces (PlaceOrder, CurrencyService, Health Check) confirmed flowing end-to-end

---

## Milestone 3: Incident Detector — 🔶 ACTIVE

**Goal:** Automatic incident flagging via burn-rate / multi-window alerting (SLO error-budget style, per Google SRE Workbook) — **not** static thresholds.

> ⚠️ Flag: the original task list here described a custom Python polling script. That's the wrong design for this milestone — the locked decision is PrometheusRule + Alertmanager based burn-rate alerting. Rewriting this checklist to match is pending confirmation.

- [ ] Decide: PrometheusRule as raw CRs vs. Helm-templated (open question)
- [ ] Write multi-window burn-rate PrometheusRule(s) with `release: prometheus` label
- [ ] Wire Alertmanager routing for the fired alerts
- [ ] Confirm rules fire correctly against a real induced incident
- [ ] Document detection logic and burn-rate windows used

---

## Milestone 4: LangGraph Agent (reasoning, no execution yet) — ✅ CLOSED (2026-09-25)

**Goal:** Agent reads an incident and proposes a fix — doesn't act yet.

- [x] `agent/` folder (`graph.py`, `prompts/`, `rag/`)
- [x] LLM: Groq `openai/gpt-oss-120b` (Llama 3.3 70B unavailable on this account's key)
- [x] LangGraph flow: input incident → gather context → reason → output proposed action
- [x] Structured JSON output validated: 20/20 valid schema, 20/20 correct action after prompt fix
- [x] Real-incident validation: forced OOM crashloop on checkoutservice, agent correctly diagnosed and proposed `rollout_restart`
- [x] Documented known limitation: no resource-limit remediation action in the vocabulary yet
- [ ] Wire graph to live M3 detector alerts (currently manually-typed targets) — deferred, not blocking M5

---

## Milestone 5: Policy Guardrails (OPA) — ⬜ NOT STARTED

- [ ] Install OPA locally
- [ ] Create `policies/` folder
- [ ] Write initial Rego policies (min replica count, protected namespaces, blocked actions)
- [ ] Script/service to send agent's proposed action to OPA, get allow/deny
- [ ] Test against valid and invalid proposed actions
- [ ] Document each policy rule and rationale

---

## Milestone 6: Slack Human-in-the-Loop Approval — ⬜ NOT STARTED

- [ ] Slack app with interactive approve/reject buttons
- [ ] FastAPI webhook to receive Slack interaction payloads
- [ ] Wire high-risk OPA-flagged actions to trigger a Slack message
- [ ] Confirm approve/reject decision reaches the orchestrator

---

## Milestone 7: Executor & Rollback — ⬜ NOT STARTED

- [ ] `executor/` folder (`k8s_client.py`, `actions.py`, `executor.py`)
- [ ] Implement `restart_pod()`, `rollout_restart()`, `scale_deployment()`, `rollback_deployment()`
- [ ] Connect executor to receive only OPA-approved + Slack/Dashboard-approved actions
- [ ] `rollback/` — snapshot, verifier, rollback_manager
- [ ] Verifier re-checks Prometheus metrics post-fix within a timeout
- [ ] Rollback trigger if unresolved in time
- [ ] Test: wrong fix → rollback fires; correct fix → rollback doesn't fire

---

## Milestone 8: Dashboard — 🔶 IN PROGRESS (backend owned by teammate, issue #8)

- [ ] `dashboard/backend` — FastAPI (uv), Postgres StatefulSet + PVC in Kind, Alembic migrations, thin-router/thick-service layering
- [ ] `dashboard/frontend` — React (TypeScript, TanStack Query, pnpm/Vite)
- [ ] Seed script (`seed.py`) so frontend can build against real endpoints early
- [ ] Endpoints: list pending high-risk actions, receive approve/reject
- [ ] Frontend: incident feed + approve/reject buttons wired to backend
- [ ] Embedded Grafana panels

---

## Milestone 9: Chaos Testing & Validation — ⬜ NOT STARTED

- [ ] Chaos Mesh installed in Kind cluster
- [ ] Fault injection scenarios: pod kill, latency injection, CPU spike
- [ ] Load generation (k6/Locust) for realistic traffic
- [ ] Record detection time, diagnosis accuracy, policy correctness, rollback correctness per scenario
- [ ] Results table for evaluation slide

---

## Milestone 10: Integration, Polish & Presentation Prep — ⬜ NOT STARTED

- [ ] Full end-to-end run-through, no manual steps
- [ ] Final README with setup, architecture diagram, demo steps
- [ ] Live demo script + backup video
- [ ] Slides with real screenshots/results
- [ ] Rehearse expected panel/viva questions

---

## Notes

- **Git Tags:** tag after each milestone (`git tag milestone-N-done`)
- **MVP Scope:** M1–M7 are the core MVP; M8–M9 (dashboard polish, chaos) can be scoped down if the timeline is tight
- Scoped-out-by-design (document as engineering tradeoffs, not gaps): managed cloud Kubernetes, long-term metrics storage (Thanos/Mimir) — see ADR 0001