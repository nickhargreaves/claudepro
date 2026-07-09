# Curriculum status

Live tracker for the seven-phase plan. Full rationale, concepts, and
exercises for each phase are in [README.md](README.md) — this file just
tracks progress.

## Status

- [x] 00 — Setup
- [x] 01 — Foundations (CLAUDE.md, plan mode)
- [x] 02 — Agentic workflow (skills, subagents, hooks)
- [x] 03 — Testing (pytest, Vitest, verify skill)
- [x] 04 — CI/CD (GitHub Actions, code-review, ultrareview)
- [ ] 05 — Deployment (Docker, secrets, real deploy target)
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
  header, opened as [PR #1](https://github.com/nickhargreaves/claudepro/pull/1)
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

## Phase 05 — Deployment (next)

Goal: Dockerize the FastAPI service and build the frontend statically,
secrets management for the deploy target, CD gated on CI passing, and a
guided live deploy with risk narrated before each step.
