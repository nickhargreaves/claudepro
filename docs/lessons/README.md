# How to use these lessons

This is a fork-and-follow curriculum, not a read-only writeup. Each phase
below is a lesson you do yourself, in your own copy of this repo, with your
own Claude Code session — not a description of what someone else already
built.

## Setup (once)

1. Fork or clone this repo.
2. Install [Claude Code](https://claude.com/claude-code), and confirm it can
   run in this directory.
3. Install [`uv`](https://docs.astral.sh/uv/) for the backend and Node 22+
   for the frontend. (Phase 00 covers this if you're starting from scratch.)

## Picking a phase

Every phase ends on a tagged commit — the reference state after that
phase's milestone was hit:

```
phase-00-done   phase-01-done   phase-02-done   phase-03-done   phase-04-done
```

To start phase `N`, check out the tag from the phase before it (or work
from a totally fresh clone for phase 00):

```bash
git checkout tags/phase-0<N-1>-done -b my-phase-0N
```

Then open [`0N-<name>.md`](.) and follow it.

## While you work

- Read the lesson's **Goal** first — know what you're aiming for before you
  start typing prompts.
- The **Steps** are things to *do*, usually by talking to Claude Code, not
  a script to paste. Expect to make judgment calls Claude will ask you
  about (data model shape, which feature to build, how much to automate) —
  that back-and-forth is the actual skill being practiced.
- Hit the **Checkpoint** before moving on. If it doesn't pass, you're not
  done yet, regardless of how confident Claude sounds.
- **Watch out for** lists real problems hit while building this repo the
  first time — not hypotheticals. You may hit the same ones.

## After you're done

For phases 00-04 (already built once, here, for real), diff your result
against the reference:

```bash
git diff phase-0<N-1>-done..phase-0N-done --stat
```

This is **a** solution, not **the** solution. Your data model, your test
cases, your skill's wording will differ — that's expected. Use the diff to
check you covered the same ground, not to match it line for line.

## Phases

| # | Lesson | Focus |
|---|---|---|
| 00 | [Setup](00-setup.md) | Repo, CLI, environment |
| 01 | [Foundations](01-foundations.md) | CLAUDE.md, plan mode |
| 02 | [Agentic workflow](02-agentic-workflow.md) | Skills, hooks, subagents, permissions |
| 03 | [Testing](03-testing.md) | TDD, mocking LLM calls, the `verify` skill |
| 04 | [CI/CD](04-ci-cd.md) | GitHub Actions, `/code-review`, branch protection |
| 05 | [Deployment](05-deployment.md) | Docker, secrets, a real deploy target |
| 06 | [Observability](06-observability.md) | Logging, tracing an LLM call, incident debugging |
| 07 | [MCP & agents](07-mcp-agents.md) | Your own MCP server, Agent SDK, Cowork |
