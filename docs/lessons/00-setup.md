# Phase 00 — Setup

**Goal:** get the repo, the CLI, and your terminal habits in order before any
lesson, so later phases aren't fighting the environment.

## Start here

Fresh clone or fork — there's no prior tag for this one, you're building
the starting point.

Prerequisites: Claude Code installed and working in this directory; Python
3.11+ and Node 22+ available on your machine.

## Steps

1. `git init` (if you haven't already) and make a first commit — even an
   empty one. Claude Code reasons about the repo it's sitting in; starting
   from a clean, committed baseline means every later diff is legible.
2. Install [`uv`](https://docs.astral.sh/uv/) for Python tooling:
   `curl -LsSf https://astral.sh/uv/install.sh | sh`.
3. Ask Claude Code to scaffold a `backend/` FastAPI app managed with `uv`
   (`uv init`, add `fastapi` + `uvicorn[standard]`, a `/health` route) and a
   `frontend/` Vite + React + TypeScript app (`npm create vite@latest`).
4. Wire the frontend dev server to proxy `/api/*` to the backend, so both
   halves talk to each other in dev without a CORS dance.
5. Set up `.claude/launch.json` with entries for both dev servers, so you
   (and Claude, via preview tools) can start them without juggling two
   terminals.

## Checkpoint

- `uv run pytest -q` passes (even just the health-check test).
- `npm run build` succeeds with no TypeScript errors.
- Start both dev servers and confirm the frontend renders something proving
  it can actually reach the backend (not just a static page) — e.g. a
  "backend status: ok" line fetched from `/api/health`.

## Watch out for

- If `uv` isn't on `PATH` in a fresh shell, you'll need
  `source $HOME/.local/bin/env` (or restart the shell) before `uv` commands
  work.
- pytest needs to find your app package. If you get `ModuleNotFoundError:
  No module named 'app'`, add `pythonpath = ["."]` under
  `[tool.pytest.ini_options]` in `pyproject.toml`.

## Compare your work

```bash
git diff phase-00-done --stat
```
