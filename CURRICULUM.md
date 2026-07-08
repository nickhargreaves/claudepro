# Claude Mastery Curriculum — TaskFlow

Seven phases, one running project. Each phase pairs a Claude Code capability with
a milestone on **TaskFlow** — an AI-augmented task manager with a Python
(FastAPI) backend and a TypeScript (React + Vite) frontend.

Full rationale and exercises: see the plan shared at project kickoff
(2026-07-08). This file tracks status as we move through it.

## Status

- [x] 00 — Setup
- [ ] 01 — Foundations (CLAUDE.md, plan mode)
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

## Phase 01 — Foundations (next)

Goal: write a real `CLAUDE.md` (conventions, run commands, gotchas), use plan
mode to design the task data model, then have Claude scaffold task CRUD from
that plan.
