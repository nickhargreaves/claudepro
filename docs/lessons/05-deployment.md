# Phase 05 — Deployment: from laptop to a real URL

**Goal:** best practice here is less about Claude-specific tricks and more
about having Claude execute deployment discipline you'd want from any
engineer: reproducible builds, secrets handled correctly, no surprise
prod pushes.

> This phase hasn't been built in this repo yet — there's no `phase-05-done`
> tag to diff against. The steps below are the plan; if you're the one who
> ends up building it, it'd be worth turning this into a real lesson with a
> tag, same as 00-04.

## Start here

```bash
git checkout tags/phase-04-done -b my-phase-05
```

## Steps

1. Dockerize the backend service, and produce a static build for the
   frontend.
2. Set up secrets management so your Claude API key (or any credential)
   never lands in the repo or the container image — injected at deploy
   time only.
3. Pick a real deploy target (Fly.io, Render, a VPS — anything you can
   actually reach from a browser afterward) and commit to it.
4. Write a minimal `docker-compose` (or equivalent) so local dev has parity
   with what actually ships.
5. Wire CD: merge to your default branch → build → deploy, gated on CI
   passing — not a manual step you remember to run.
6. Do one deploy live, and have Claude narrate the risk of each
   destructive-adjacent step (overwriting a running service, rotating a
   secret) before it happens, rather than just doing it silently.

## Checkpoint

- The app is reachable at a real URL, not just `localhost`.
- The deploy was triggered by the pipeline, not a manual `scp`/`docker push`
  you ran by hand.
- Your API key is verifiably not in the repo, not in the image layers, and
  not in any log you can find.
