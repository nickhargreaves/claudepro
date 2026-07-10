# Phase 07 — Going further: MCP servers and multi-agent design

**Goal:** the capstone — build the kind of tool you've been using all
along, and use orchestration patterns beyond single-agent chat.

> This phase hasn't been built in this repo yet — there's no `phase-07-done`
> tag to diff against.

## Start here

```bash
git checkout tags/phase-04-done -b my-phase-07
# (later phases as a base if you've built them)
```

## Steps

1. Write a small MCP server that exposes your app's own API as tools —
   e.g. list/create/update your core resource — and connect it in Claude
   Desktop. Manage your app by chatting with it instead of using its UI.
2. Rebuild one LLM-backed feature (like an earlier triage/classification
   endpoint) on the Claude Agent SDK instead of a raw API call, and notice
   what the SDK gives you for free that you were previously doing by hand.
3. Think about where multi-agent orchestration would actually help vs. add
   noise in your project — parallel subagents pay off when tasks are
   genuinely independent, not by default.
4. Retire one recurring manual chore — a weekly summary, a stale-item
   sweep — to a scheduled agent or Cowork, so it happens without you
   asking.

## Checkpoint

- You can manage your app's core resource from Claude Desktop via your own
  MCP server, not just the app's own UI.
- A scheduled/automated agent does one real recurring task without your
  manual trigger.
