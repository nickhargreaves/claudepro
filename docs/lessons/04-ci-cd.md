# Phase 04 — CI/CD: Claude as reviewer, not just author

**Goal:** writing code is half the job. This phase wires Claude into the
gate that decides whether code merges — a genuinely different skill from
writing it.

## Start here

```bash
git checkout tags/phase-03-done -b my-phase-04
```

## Steps

1. **Write a CI workflow covering both halves of the stack** — lint, test,
   and (for a frontend) build, running on every push/PR to your default
   branch. Two independent jobs if your stack splits cleanly (e.g. backend
   vs. frontend); no need to force them into one.
2. **Open a real PR to exercise it.** Don't test the pipeline with a no-op
   — build one small, genuine feature on a branch and push it through. If
   CI has never actually run before, expect it to fail on something you
   didn't anticipate (a missing environment variable, a config path that
   works locally but not in a clean container) — that's normal, not a sign
   you did something wrong.
3. **Run a code review on the PR diff before merging.** Use whatever
   review tooling your Claude Code setup offers, at a normal effort level
   for a routine change. Read the findings; for anything real but out of
   scope for this PR, don't silently fix it inline — decide explicitly
   whether it belongs in this change or as a follow-up.
4. **Turn on branch protection.** Require your CI checks to pass before
   merge. If you're on a private repo on a free plan, you may hit a real
   platform limit here (GitHub requires a paid plan or a public repo for
   branch protection on private repos) — that's worth knowing before you
   assume protection is configurable everywhere.
5. **Prove enforcement, don't just configure it.** Try to get a change onto
   your protected branch without going through a green PR — a direct push,
   or merging before checks finish. Watch it actually get rejected.

## Checkpoint

- CI runs and passes on a real PR, covering the whole stack.
- You ran an automated review on that PR's diff and made an explicit call
  on each finding (fix now vs. defer).
- You watched a merge get blocked for real — not "the docs say it would
  be," but an actual rejected push or a merge button GitHub itself refused.

## Watch out for

- `pydantic-settings` (or any startup-time config validation) will crash
  your test suite in CI if a required environment variable only exists in
  your local `.env`. If your tests mock every real external call anyway, a
  non-secret placeholder value in the CI env is usually enough — you don't
  need the real credential in CI.
- Branch protection APIs (classic and the newer "rulesets") both gate on
  the same GitHub Pro / public-repo requirement for private repos. If you
  hit a 403 on one, the other will likely 403 too — it's a platform
  restriction, not a bug in your request.
- If your own safety tooling blocks a destructive-looking action (like a
  direct push to a protected branch), that's a second, independent gate
  doing its job — don't route around it without deciding on purpose to.

## Compare your work

```bash
git diff phase-03-done..phase-04-done --stat
```
