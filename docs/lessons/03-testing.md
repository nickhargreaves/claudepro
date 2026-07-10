# Phase 03 — Testing: making Claude prove it, not just claim it

**Goal:** Claude will tell you something works. This phase is about never
taking that on faith — for both regular code and the LLM-touching code,
which fails differently.

## Start here

```bash
git checkout tags/phase-02-done -b my-phase-03
```

## Steps

1. **Add a frontend test runner if you don't have one.** Vitest + Testing
   Library (or your stack's equivalent) — get it wired up and write a
   handful of characterization tests for whatever UI already exists, mocking
   your API layer at the module boundary rather than hitting the network.
2. **Run a real TDD loop.** Pick a small, genuine UI gap — something like
   "deleting should ask for confirmation first" — and write the failing
   test *before* touching the implementation. Run it, watch it fail for the
   right reason, then implement just enough to make it pass. Add the
   negative case too (what happens when the user cancels).
3. **Test the LLM-backed endpoint's failure path, not just its happy path.**
   Mock the Claude client so your test doesn't depend on a live API call,
   and write a case that forces the call to fail — confirm your endpoint
   degrades gracefully (a clean error, not a stack trace) instead of
   assuming the API always succeeds.
4. **Run `/verify` (or your equivalent end-to-end check) on one real
   feature change.** Don't just trust green tests — actually drive the
   feature in a running browser/app and watch it work. Compare what that
   catches to what the test suite alone told you.

## Checkpoint

- Frontend and backend both have a real test suite that runs green.
- At least one test deliberately breaks the Claude API call and asserts the
  fallback behavior, not just the happy path.
- You've watched `/verify` (or equivalent) drive the actual UI, not just
  read a "tests passed" summary.

## Watch out for

- Test-runner state can leak between test cases if you reset mocks the
  wrong way — e.g. calling something equivalent to "restore all mocks"
  when you meant "clear all mock call history" can silently strip your
  module-level mocks entirely. If call counts look wrong across tests, this
  is the first thing to check.
- If you're verifying a browser confirmation dialog
  (`window.confirm`-style), know that most headless browser automation
  auto-accepts native dialogs by default. You may not be able to visually
  screenshot the dialog text — the unit test asserting the exact message is
  often the only real check on that.

## Compare your work

```bash
git diff phase-02-done..phase-03-done --stat
```
