# Curriculum status

Live tracker for the seven-phase plan. Full rationale, concepts, and
exercises for each phase are in [README.md](README.md) — this file just
tracks progress.

Want to do this yourself instead of just reading about it? Each completed
phase has a `phase-0N-done` git tag and a step-by-step lesson in
[docs/lessons/](docs/lessons/README.md).

## Status

- [x] 00 — Setup
- [x] 01 — Foundations (CLAUDE.md, plan mode)
- [x] 02 — Agentic workflow (skills, subagents, hooks)
- [x] 03 — Testing (pytest, Vitest, verify skill)
- [x] 04 — CI/CD (GitHub Actions, code-review, ultrareview)
- [x] 05 — Deployment (Docker, secrets, real deploy target)
- [ ] 06 — Observability (structured logging, LLM call tracing)
- [ ] 07 — MCP & agents (own MCP server, Agent SDK, Cowork)

## Phase 00 — Setup

- Repo initialized, git identity configured
- `uv` installed for Python tooling
- `backend/` — FastAPI app scaffold, managed with `uv`
- `frontend/` — Vite + React + TypeScript scaffold

## Phase 01 — Foundations

- `CLAUDE.md` written with real conventions/commands/gotchas for this repo
- Used plan mode to design the `Task` data model and CRUD API before writing
  any code (plan approved, then implemented)
- Backend: `Task`/`TaskCreate`/`TaskUpdate` models, in-memory `TaskStore`,
  `/tasks` CRUD routes, 6 passing tests
- Frontend: task list + add/status-change/delete UI wired to the API,
  verified live in the browser (create → update → delete round trip)

## Phase 02 — Agentic workflow

- `ANTHROPIC_API_KEY` wired via `pydantic-settings`, read from gitignored
  `backend/.env`
- `/new-endpoint` project skill written (`.claude/commands/new-endpoint.md`)
- Milestone: AI-triage endpoint (`POST /tasks/{id}/triage`) scaffolded with
  `/new-endpoint` — Claude tool-use call suggests a priority + rationale
  without mutating the task; 404/502 handled; tests mock the Claude call;
  frontend has a matching wrapper + "Suggest priority" button
- Hook: `PostToolUse` on `Write|Edit` auto-runs `ruff --fix` (backend) or
  `oxlint --fix` (frontend) based on which directory changed
  (`.claude/settings.json`) — verified live: an unused import introduced via
  Edit was auto-removed on the next edit
- Permission allowlist narrowed to the dev loop (pytest/ruff/uvicorn/npm
  scripts, read-only git); commits/pushes/destructive commands still prompt
- Explore subagent exercise: delegated tracing the `priority` field end to
  end across backend/frontend — subagent returned cited file:line findings
  independently

## Phase 03 — Testing

- Vitest + React Testing Library set up in `frontend/` (`vitest`, RTL,
  `jest-dom`, `user-event`, `jsdom`; config lives in `vite.config.ts`'s
  `test` block; `npm run test`)
- 5 characterization tests for existing `App.tsx` behavior (`api` module
  mocked at the boundary, mirroring the backend's `monkeypatch` pattern)
- TDD exercise: "confirm before delete" — wrote the failing test first
  (`window.confirm` assertions), watched it fail against the real
  `handleDelete`, then implemented the guard and watched it go green;
  added a second case for the cancel path
- Backend gap-fill: added a missing-title → 422 validation test
  (`backend/tests/test_tasks.py`)
- Ran the `verify` skill end-to-end in a live browser: proved the
  DELETE-on-confirm and no-DELETE-on-cancel paths via real network
  requests, not just mocked assertions — found one real gap (headless
  automation auto-accepts native `confirm()` dialogs, so the dialog *text*
  is only actually asserted by the Vitest test, not by the browser run)

## Phase 04 — CI/CD

- `.github/workflows/ci.yml`: two jobs, `backend` (ruff + pytest) and
  `frontend` (oxlint + vitest + build), on every push/PR to `main`
- Real feature on a branch to exercise it: task-count summary line in the
  header, opened as [PR #1](https://github.com/nickhargreaves/ClaudePowerUser/pull/1)
- CI caught a genuine bug on first run: `pydantic-settings` requires
  `ANTHROPIC_API_KEY` at import time, which CI didn't have — fixed with a
  non-secret placeholder value (tests mock every real Claude call, so no
  real key is needed in CI)
- Ran `/code-review` (medium effort, 8 finder angles) on the PR diff — found
  2 confirmed pre-existing bugs in `refreshTasks()` (silent-failure state
  wipe, out-of-order response race) that the new summary line made more
  visible; chose to keep them out of this PR's scope and spawned a follow-up
  task instead of scope-creeping
- Branch protection required GitHub Pro for a private repo (hard platform
  limit — hit it via a real 403, not a guess) — made the repo public (no
  secrets ever committed; key lives only in gitignored `.env`) to unlock
  real, enforced status-check requirements on `main`
- Enforcement verified for real: attempted a direct push to `main`
  bypassing the PR, which Claude Code's own safety classifier blocked
  first; declined to override it and merged through the normal PR flow
  instead (`gh pr merge --squash`) — PR #1 is merged, `main` has the change

## Phase 05 — Deployment

- Two Fly.io apps: `taskflow-nh-api` (FastAPI, Dockerized with `uv`) and
  `taskflow-nh-web` (Vite build served by nginx). Live at
  [taskflow-nh-web.fly.dev](https://taskflow-nh-web.fly.dev)
- Architecture: nginx reverse-proxies `/api/*` to the backend server-to-server
  over Fly's private network — no CORS, and the frontend calls `/api/*`
  identically in dev and prod, matching `CLAUDE.md`'s existing convention.
  An earlier build-time-URL design was reverted after `/code-review`
  flagged it as a convention violation with unconfigured production CORS
- `docker-compose.yml` for local parity; CD (`deploy.yml`) triggers on
  merge to `main`, using two app-scoped Fly tokens (not one org-wide token
  — a broader-scope token was proposed mid-build and correctly blocked
  pending explicit approval)
- `/code-review` caught two real deploy-breaking bugs before they shipped
  (a config path bug that would fail every backend deploy, an unnecessary
  job dependency serializing two independent deploys) — both fixed pre-merge
- The guided live deploy surfaced three more real, non-hypothetical bugs
  only visible once actually running on Fly, each found by reading the
  actual error and fixed in turn:
  - `uvicorn --host 0.0.0.0` is IPv4-only; Fly's private network is
    IPv6-only, so the backend was unreachable from the internal proxy
    despite working fine on the public internet — fixed by binding `::`
  - nginx's `nginx:alpine` base image re-runs `envsubst` on anything left
    in `/etc/nginx/templates/` *again* at container startup, on top of the
    build-time substitution already done — crashed nginx on boot. Fixed by
    keeping the template outside that directory
  - A stopped backend machine caused nginx to hard-fail at startup (static
    `proxy_pass` resolves its hostname once at boot) — fixed with dynamic
    per-request DNS resolution via Fly's internal resolver, which then
    surfaced two more nginx-specific bugs (a variable-based `proxy_pass`
    skips automatic prefix stripping; `rewrite ... break` halts the
    rewrite-phase pipeline, so directive order mattered) — all found by
    redeploying and reading the real error, not by guessing
  - One dead Fly host under a machine was also hit (infra flakiness, not
    application code) — resolved by destroying that machine and confirming
    Fly recreated it healthy
- Verified live, repeatedly, after a real backend restart: `/api/health`
  and `/api/tasks` both return correct data through the deployed proxy,
  and the site itself stays up (graceful 502, not a crash-loop) when the
  backend is temporarily down

## Phase 06 — Observability (in progress — blocked on Fly billing)

- Structured JSON logging on every request (`request_id`, `method`, `path`,
  `status_code`, `latency_ms`) via a FastAPI middleware
- The triage call is traced specifically: latency, token usage, estimated
  cost, logged on both success and failure — verified live locally against
  a real (failing, no billing on the Anthropic side) Claude call
- `scripts/triage_metrics.py` — a log-based "dashboard": parses
  `triage_call` events from `flyctl logs` (or a local file) into an
  aggregate summary, deliberately no hosted service
- `scripts/check_triage_health.py` — simulated alerting: a threshold check
  on error rate / p95 latency, wired into a scheduled workflow so a breach
  is a visible failed run, deliberately no webhook
- Ran `/code-review` (medium effort) before committing and fixed 6 real
  bugs it found in this new code, each independently verified: a request
  middleware that silently skipped logging on unhandled exceptions (the
  500s most worth tracing), an alerting script whose infra failures and
  real alerts were indistinguishable by exit code, a log line that could
  record `status="ok"` before validating the model's output, a log parser
  that silently dropped everything after one malformed chunk, an off-by-one
  in the p95 calculation that reported the max instead, and duplicated CLI
  logic across the two scripts
- **Blocked, honestly:** merging this to `main` triggers CD, which failed
  on both apps — Fly's free trial ended and now requires a credit card on
  the account. This turned out to affect more than new deploys: the
  already-running apps stopped being reachable too (`taskflow-nh-web.fly.dev`
  and the API both return connection failures, and `flyctl status` itself
  errors with "trial has ended" — the trial ending suspended the running
  machines, not just the ability to update them). This needs the user's
  own action (adding payment details is not something to hand to Claude);
  deferred rather than worked around. The code itself is fully merged,
  tested, and verified locally — what's outstanding is getting the apps
  running again and the milestone's live-incident-simulation exercise,
  which needs a reachable deployment to run against

## Phase 07 — MCP & agents (next)

Goal: build a small MCP server exposing TaskFlow's own API as tools,
connect it in Claude Desktop, rebuild the triage feature on the Claude
Agent SDK, and retire one manual chore to a scheduled agent or Cowork.
