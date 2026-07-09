# TaskFlow — Claude Mastery Curriculum

A small AI-augmented task & project tracker — Python (FastAPI) backend,
TypeScript (React + Vite) frontend — built as the running project for a
seven-phase curriculum in using Claude Code, Claude Desktop, and Cowork at an
expert level: coding, agentic workflows, testing, CI/CD, deployment, and
observability.

**Full curriculum, phase-by-phase, with live progress:**
**[nickhargreaves.github.io/claudepro](https://nickhargreaves.github.io/claudepro/)**

For the raw status checklist, see [CURRICULUM.md](CURRICULUM.md).

## The project

TaskFlow uses the Claude API itself — to triage new tasks — which gives the
curriculum a real reason to touch every part of the lifecycle: an API to
test, a UI to ship, an LLM call to observe, and a deploy target to watch in
production.

**Stack:** FastAPI &middot; React + Vite + TypeScript &middot; pytest / vitest
&middot; GitHub Actions &middot; Docker &middot; Claude Agent SDK

## Running it locally

```bash
# backend
cd backend && uv run uvicorn app.main:app --reload --port 8000

# frontend (separate shell)
cd frontend && npm run dev
```

The frontend dev server proxies `/api/*` to `http://127.0.0.1:8000`.
