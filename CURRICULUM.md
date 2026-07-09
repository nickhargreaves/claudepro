# Curriculum status

Live tracker for the seven-phase plan. Full rationale, concepts, and
exercises for each phase are in [README.md](README.md) — this file just
tracks progress.

## Status

- [x] 00 — Setup
- [x] 01 — Foundations (CLAUDE.md, plan mode)
- [ ] 02 — Agentic workflow (skills, subagents, hooks)
- [ ] 03 — Testing (pytest, Vitest, verify skill)
- [ ] 04 — CI/CD (GitHub Actions, code-review, ultrareview)
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

## Phase 02 — Agentic workflow (in progress)

- [x] `ANTHROPIC_API_KEY` wired via `pydantic-settings`, read from gitignored
      `backend/.env`
- [x] `/new-endpoint` project skill written (`.claude/commands/new-endpoint.md`)
- [x] Milestone: AI-triage endpoint (`POST /tasks/{id}/triage`) scaffolded
      with `/new-endpoint` — Claude tool-use call suggests a priority +
      rationale without mutating the task; 404/502 handled; tests mock the
      Claude call; frontend has a matching wrapper + "Suggest priority" button
- [ ] Hook: auto-run `ruff`/`oxlint` after edits
- [ ] Narrow the permission allowlist in `.claude/settings.json`
- [ ] Explore subagent exercise (delegate a "where does X happen" question)
