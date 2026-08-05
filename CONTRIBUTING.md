# Contributing Guidelines — Warden

These rules apply to every team member, on every branch, for the duration of the project. They exist so that four people can build in parallel (per the architecture's module breakdown) without integration turning into a mess later in the timeline.

---

## 1. AI Tool Policy

Writing code entirely by hand is not required. Using AI is fine. What's not fine is the "ask GPT, paste it, move on" pattern — that's the thing this policy exists to stop.

- **No AI autocomplete / agentic IDE plugins.** Copilot, Cursor, Windsurf, Codeium, or any IDE extension that auto-suggests or auto-writes code inline is not allowed. This isn't about purity — it's so that every line put into a file passed through a moment where you actively chose to type or paste it, not accepted it on reflex.
- **Web-based AI chat tools are allowed** — claude.ai, chatgpt.com, or similar — for generating code, explanations, debugging help, or design discussion.
- **No blind copy-pasting, full stop.** 

---

## 2. Every Change Must Be Committed, Documented, and Updated

- No uncommitted work sitting on a laptop overnight. If you stop for the day, commit (a WIP commit on your branch is fine — see Section 5).
- Every change that affects behavior, an interface (API endpoint, module input/output, OPA policy schema), or a requirement gets a matching update to the relevant doc (README, module docstring, `docs/`, or architecture notes) **in the same PR**. Code and docs drift apart the moment they're separated into different PRs — don't let that happen.
- Commit messages describe **what and why**, not just "fix" or "update":
  - Good: `fix(executor): correct replica count check before scale-down (FR-3.2)`
  - Bad: `changes`
- Reference the relevant requirement/feature ID (e.g. `FR-3.2`, `NFR-1.1`, or the Slide 7 capability it maps to) in the commit message or PR description when the change implements or fixes one.

---

## 3. Verify and Test Before Opening a PR(Later we will add testing not now)

- Run the module's tests locally and confirm they pass before pushing.
- If there's no test yet for the thing you changed, write one — don't rely on "it looked right when I ran it once."
- For anything touching incident detection, agent reasoning, or policy checks, manually verify with at least 2–3 example scenarios (e.g. injected pod failure, simulated high latency) and confirm the output/behavior makes sense — not just that the code didn't crash.
- Never open a PR with a known-failing test or a `# TODO: fix this later` on the critical path (detect → reason → guard → act → rollback).

---

## 4. Pull Request Checklist

Every PR description must confirm:

- [ ] Code was written/reviewed by me, not blind-pasted from an AI tool
- [ ] No AI autocomplete/agentic IDE plugin was used to generate this code
- [ ] Relevant docs (README, module docstrings, `docs/`) updated to match this change
- [ ] Tests written/updated and passing locally
- [ ] Manually verified with at least one real scenario, not just unit tests
- [ ] Linked requirement/feature ID(s), if applicable

---

## 5. Branching and Review

- **One feature/module per branch** — name it after the module and what it does, e.g. `feature/detector-threshold-rules`, `feature/opa-min-replica-policy`, `feature/dashboard-approval-ui`.
- **At least one other team member reviews and approves before merging to `main`.** No self-merging — this is enforced via GitHub branch protection, not just an honor system.
- **`main` should always be in a state that runs end-to-end**, even if some features are still basic — a broken `main` blocks everyone else's integration work.
- Delete your feature branch after it's merged, to keep the branch list clean.

---

## 6. Ownership

Each core module has one clearly responsible owner per the team's work split. If you're touching someone else's module, loop them in before opening a PR, not after.

| Module | Folder | Owner |
|---|---|---|
| Cluster + sample services + chaos testing | `cluster/`, `chaos/` | [Name] |
| Monitoring + Incident Detector | `monitoring/`, `detector/` | [Name] |
| Agent (LangGraph + RAG) | `agent/` | [Name] |
| Policies + Executor + Rollback + Dashboard | `policies/`, `executor/`, `rollback/`, `dashboard/` | [Name] |

*(Adjust this table to match your actual team split.)*

---

## 7. Commit Style Reference

Use conventional-style prefixes where possible:
- `feat(...)` — new functionality
- `fix(...)` — bug fix
- `docs(...)` — documentation only
- `test(...)` — adding or updating tests
- `refactor(...)` — code change that doesn't change behavior
- `chore(...)` — tooling, dependencies, config

Example: `feat(agent): add RAG retrieval step for incident context (Slide 7 capability)`