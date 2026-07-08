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

## Phase 02 — Agentic workflow (next)

Goal: custom skills (`/new-endpoint`), hooks (auto-run ruff/oxlint on edit),
narrower permission allowlists, and an Explore subagent exercise once the
codebase has more surface area. Milestone: an AI-triage endpoint built using
a self-authored skill.
