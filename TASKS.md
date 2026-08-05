# Warden — Project Task Tracker

**Autonomous SRE Agent with Safety Guardrails for Production Incident Remediation**

---

## Milestone 1: Detect and See (Foundation — no AI yet)
**Goal:** Working Kubernetes cluster with real metrics flowing into a dashboard.

- [ ] Install Docker, Kind, kubectl, Helm on all team machines
- [ ] Create `cluster/kind-config.yaml`
- [ ] Spin up local Kind cluster (`kind create cluster --config cluster/kind-config.yaml`)
- [ ] Containerize existing project components (write Dockerfile(s) if missing)
- [ ] Write Kubernetes manifests for the project (Deployment, Service, ConfigMap as needed)
- [ ] Load images into Kind (`kind load docker-image ...`)
- [ ] Deploy project to Kind cluster and confirm pods are healthy (`kubectl get pods`)
- [ ] Instrument app to expose Prometheus metrics (`/metrics` endpoint or OTel SDK)
- [ ] Install `kube-prometheus-stack` via Helm (Prometheus + Grafana)
- [ ] Confirm Prometheus is scraping the app (check Targets page in Prometheus UI)
- [ ] Build a Grafana dashboard: pod health, CPU/memory, request error rate, latency
- [ ] Export Grafana dashboard JSON, save to `monitoring/grafana/dashboards/`
- [ ] Manually kill a pod and confirm it's visible on the dashboard within seconds
- [ ] Document setup steps and gotchas in `docs/milestone1-notes.md`
- [ ] Commit and tag: `git tag milestone-1-done`

---

## Milestone 2: Incident Detector (still no LLM)
**Goal:** A script that watches Prometheus and flags incidents automatically.

- [ ] Create `detector/` folder
- [ ] Write a script to query Prometheus via its HTTP API (PromQL queries)
- [ ] Define simple threshold rules (e.g., error rate > 5%, latency > 500ms, pod restarts > N)
- [ ] Run detector on a loop/interval, print "INCIDENT DETECTED" with details when triggered
- [ ] Test: manually break something (kill pod, spike CPU) and confirm detector catches it
- [ ] Log detected incidents to a file or simple in-memory store (for the agent to consume later)
- [ ] Document detector logic and thresholds used in `docs/`

---

## Milestone 3: LangGraph Agent (reasoning, no execution yet)
**Goal:** Agent reads an incident and proposes a fix — doesn't act yet.

- [ ] Create `agent/` folder (`graph.py`, `prompts/`, `rag/`)
- [ ] Initialize root Python project with `uv` and install LangChain/LangGraph dependencies
- [ ] Set up LLM API access (Anthropic/OpenAI key in `.env`, gitignored)
- [ ] Design the LangGraph flow: input incident → gather context → reason → output proposed action
- [ ] Write initial prompt templates in `agent/prompts/`
- [ ] Feed the agent sample incident data manually, confirm it outputs a sensible fix
- [ ] (Optional/RAG) Set up a simple retrieval step: pull recent metrics/logs/past incidents as context before reasoning
- [ ] Test agent against 3-5 different simulated incident types, review output quality
- [ ] Document sample inputs/outputs in `docs/` for later evaluation slide

---

## Milestone 4: Policy Guardrails (OPA)
**Goal:** Every proposed action gets checked against explicit rules before anything executes.

- [ ] Install OPA locally
- [ ] Create `policies/` folder
- [ ] Write initial Rego policies (e.g., min replica count, protected namespaces, blocked actions list)
- [ ] Write a small script/service that sends the agent's proposed action to OPA and gets allow/deny
- [ ] Test policies against both valid and invalid proposed actions
- [ ] Document each policy rule and its rationale in `docs/`

---

## Milestone 5: Executor (real actions on the cluster)
**Goal:** Approved actions actually run against the Kubernetes cluster.

- [ ] Create `executor/` folder (`k8s_client.py`, `actions.py`, `executor.py`)
- [ ] Implement `restart_pod()`, `scale_deployment()`, `rollback_deployment()` functions
- [ ] Connect executor to receive only OPA-approved actions
- [ ] **Create the Main Orchestrator (`main.py`)**: Wire the Detector → Agent → OPA → Executor pipeline together
- [ ] Test each action manually against the Kind cluster
- [ ] Confirm executor never runs an action that wasn't approved

---

## Milestone 6: Rollback & Verification
**Goal:** Failed fixes get automatically undone.

- [ ] Create `rollback/` folder (`snapshot.py`, `verifier.py`, `rollback_manager.py`)
- [ ] Implement state snapshot before any executor action runs (or rely on K8s deployment history)
- [ ] Implement verifier: re-check Prometheus metrics after a fix, within a timeout window
- [ ] Implement rollback trigger if incident isn't resolved in time (e.g., `kubectl rollout undo`)
- [ ] Test: inject a fault, apply a deliberately wrong/ineffective fix, confirm rollback fires
- [ ] Test: inject a fault, apply a correct fix, confirm rollback does NOT fire

---

## Milestone 7: Human Approval Dashboard
**Goal:** A human can see incidents and approve/reject high-risk actions.

- [ ] Create `dashboard/backend/` — FastAPI app (managed with `uv`) exposing incidents, agent decisions, approval endpoints
- [ ] Create `dashboard/frontend/` — React (Vite) UI (managed with `pnpm`)
- [ ] Backend: endpoint to list pending high-risk actions
- [ ] Backend: endpoint to receive approve/reject decisions
- [ ] Frontend: incident feed view
- [ ] Frontend: approve/reject buttons wired to backend
- [ ] Connect approval flow back into main orchestrator (only proceed on approval)
- [ ] Test end-to-end: high-risk incident → shows on dashboard → click approve → executor runs it

---

## Milestone 8: Chaos Testing & Validation
**Goal:** Prove the full detect → reason → guard → act → verify → rollback loop works end to end.

- [ ] Create `chaos/` folder
- [ ] Install Chaos Mesh (or Litmus) in the Kind cluster
- [ ] Write fault injection scenarios: pod kill, latency injection, CPU spike
- [ ] Set up load generation with k6 or Locust to simulate realistic traffic
- [ ] Run each chaos scenario, record: detection time, diagnosis accuracy, policy correctness, rollback correctness
- [ ] Collect results into a table for your evaluation/results slide
- [ ] Document all chaos test scenarios and outcomes in `docs/`

---

## Milestone 9: Integration, Polish & Presentation Prep

- [ ] Full end-to-end run-through: break something → watch Warden handle it live, no manual steps
- [ ] Fix any rough edges found during full run-through
- [ ] Write final `README.md` with setup instructions, architecture diagram, demo steps
- [ ] Prepare live demo script (what you'll show, in what order, backup plan if live demo fails)
- [ ] Record a backup demo video in case live demo breaks during presentation
- [ ] Finalize slides with real screenshots/results from your own system
- [ ] Rehearse answers to expected panel questions (see project Q&A notes)

---

## Notes

- **Clean Repo:** Don't create folders for later milestones until you actually start that milestone — keeps the repo clean.
- **Git Tags:** Commit and tag after each milestone (`git tag milestone-N-done`) for clean checkpoints.
- **MVP Scope:** If the timeline is tight, **Milestones 1–6** are the core MVP. Milestones 7–8 (dashboard polish, chaos testing) can be scoped down and marked as partially complete / future work if needed.