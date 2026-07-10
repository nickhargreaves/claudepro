# Phase 06 — Observability: watching an LLM-backed system in the wild

**Goal:** traditional observability plus one new problem: LLM calls fail
silently, drift in latency, and cost real money per request. This phase is
about seeing that.

> This phase hasn't been built in this repo yet — there's no `phase-06-done`
> tag to diff against. Depends on Phase 05 actually being deployed
> somewhere, since "observability" needs a running system to observe.

## Start here

```bash
git checkout tags/phase-04-done -b my-phase-06
# (ideally after you've also done your own Phase 05)
```

## Steps

1. Add structured logging to every route — request id, latency, status —
   not just print statements.
2. Instrument your LLM-calling endpoint specifically: which prompt version
   ran, token counts, latency, and estimated cost per call.
3. Build even a minimal dashboard from these logs — it doesn't need to be
   fancy, it needs to answer "is the triage call slow or expensive right
   now."
4. Set up alerting on LLM-specific failure modes (API error rate, latency
   spikes) — not just generic HTTP 500 monitoring, which won't catch a
   model that's technically responding but badly.
5. Simulate an incident on purpose — a bad prompt, a forced timeout — and
   use Claude Code itself to diagnose it from logs alone, without you
   pointing it at the cause first.

## Checkpoint

- A dashboard (even a rough one) shows LLM-call latency and cost over time.
- You've deliberately broken something and watched Claude root-cause it
  from logs, not from you explaining what you changed.
