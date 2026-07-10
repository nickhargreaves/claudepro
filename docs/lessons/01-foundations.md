# Phase 01 — Foundations: talking to Claude Code well

**Goal:** the highest-leverage skill is giving Claude the right context
before it writes a line. This phase is about the habits that separate
"prompt and pray" from deliberate collaboration.

## Start here

```bash
git checkout tags/phase-00-done -b my-phase-01
```

## Steps

1. **Write a real `CLAUDE.md` by hand first.** Don't ask Claude to generate
   it from nothing — draft your own take on: repo layout, the exact
   commands you run (dev server, tests, lint), and any gotchas you've
   already hit. Then ask Claude to critique it. A `CLAUDE.md` written by
   Claude about a codebase Claude just built tends to be generic; one you
   wrote yourself, grounded in commands you actually ran, isn't.
2. **Use plan mode before writing the data model.** Pick the core resource
   your app manages (a task, a note, whatever fits your project) and ask
   Claude to design it — fields, types, the CRUD API shape — *in plan mode*,
   so it explores and proposes before touching a file. Push back on the
   plan if something's off; that's the point of reviewing it before
   approving.
3. **Scaffold from the approved plan.** Once you accept the plan, let Claude
   implement it: the Pydantic models (or your stack's equivalent), an
   in-memory or lightweight store, the REST routes, and a test for each
   route in the same change.
4. **Build the matching frontend piece.** A list view that fetches from your
   new API and renders it — nothing fancy, just enough to prove the wiring
   works end to end.

## Checkpoint

- Backend tests pass and cover at least create + list + get-by-id for your
  resource.
- The frontend, running against the real backend (not a mock), shows live
  data fetched over the network — verify this by actually looking at it in
  a browser, not just trusting the code compiles.
- You have a `CLAUDE.md` you'd hand to a new teammate without embarrassment.

## Watch out for

- It's tempting to skip plan mode for "simple" changes. The data model is
  exactly the kind of decision worth pausing on — it's expensive to change
  later and easy to get subtly wrong on the first pass (e.g. which fields
  are server-set vs. client-set).
- Don't let Claude scaffold the CRUD routes *before* the plan is approved.
  If it starts writing code while still in the exploration phase, stop and
  redirect — that's the workflow, not a suggestion.

## Compare your work

```bash
git diff phase-00-done..phase-01-done --stat
```
