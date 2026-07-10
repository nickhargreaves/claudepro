# Phase 02 — The agentic workflow: skills, subagents, hooks

**Goal:** this is where Claude Code stops being "a chatbot with file
access" and becomes a configurable system you shape to your project.

## Start here

```bash
git checkout tags/phase-01-done -b my-phase-02
```

## Steps

1. **Get an API key into the project the right way.** If your app is going
   to call the Claude API itself (recommended — it gives the rest of this
   curriculum something real to test/observe/deploy), get an Anthropic API
   key yourself and drop it straight into a gitignored `.env` file. Don't
   paste it into chat — have Claude wire up config (e.g.
   `pydantic-settings`) to read it, without ever seeing the value itself.
2. **Write your first project skill.** Pick a repetitive scaffolding task —
   "add a new API route" is a good one — and write a custom slash command
   (`.claude/commands/your-command.md`) that encodes your team's convention
   for doing it: which files get touched together, what tests are
   mandatory, whether it should ask before committing. Write the
   instructions yourself; this is the part that teaches you to think in
   skills, not just use them.
3. **Use your own skill for something real.** Pick a genuine feature — an
   AI-touching endpoint is a good choice since it exercises the API key
   from step 1 — and build it by invoking the skill you just wrote. Notice
   where the skill's instructions were ambiguous or missing something; that
   feedback loop is the point.
4. **Add a hook.** Wire a `PostToolUse` hook in `.claude/settings.json` that
   auto-runs your linter/formatter after every edit. Prove it actually
   fires — introduce a real, fixable violation and watch it get cleaned up
   without you running the command yourself.
5. **Narrow your permissions.** Add an explicit `allow` list for the
   commands you run constantly (test runner, linter, dev server, read-only
   git) so they stop prompting — while leaving anything that touches git
   history, secrets, or the filesystem outside the repo still gated.
6. **Delegate one real question to a subagent.** Once your codebase has a
   few files in it, ask an Explore-type subagent something like "where does
   X happen and what touches it" and have it report back with cited
   locations, instead of answering from your own context.

## Checkpoint

- The skill file exists, is checked in, and you can point to a real feature
  built with it.
- The hook demonstrably fires — you saw it fix something, not just read the
  config.
- Your permission allowlist is narrower than default, and you can name what
  it does *not* cover.

## Watch out for

- If you add a hook to `.claude/settings.json` mid-session, the file
  watcher may only pick up `.claude/` directories that existed when the
  session started. If your hook doesn't fire, try restarting the session
  before assuming the config is wrong.
- Hook commands that use `jq` will fail silently-ish (a "command not
  found") if it isn't installed. Check before you build the hook around it.
- Skills that call an LLM API need something to mock in tests later — write
  the skill so the API call is isolated in its own function/module now,
  not inlined into a route handler. Future-you (Phase 03) will thank you.

## Compare your work

```bash
git diff phase-01-done..phase-02-done --stat
```
