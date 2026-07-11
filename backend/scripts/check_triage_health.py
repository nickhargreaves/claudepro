#!/usr/bin/env python3
"""Simulated alerting: checks recent triage_call events against thresholds.

No webhook, no external service — this is the concept, demonstrated. Wire
it into a scheduled job (see .github/workflows/observability-check.yml)
and a threshold breach shows up as a failed run, which is a real,
visible signal even without a notification channel.

Exit 0 = healthy, exit 1 = threshold breached, exit 2 = the check itself
couldn't run (flyctl missing, auth failure, timeout) — kept distinct from
exit 1 so a red run in CI doesn't get misread as a real triage regression.

Usage:
    uv run scripts/check_triage_health.py
    uv run scripts/check_triage_health.py --file path/to.log
"""

import argparse
import subprocess
import sys

from triage_metrics import add_common_args, load_events_text, parse_events, summarize

# Thresholds — tune these for your own traffic volume and latency budget.
MAX_ERROR_RATE = 0.20
MAX_P95_LATENCY_MS = 5000.0
MIN_CALLS_TO_EVALUATE = 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    add_common_args(parser)
    args = parser.parse_args()

    try:
        text = load_events_text(args)
    except FileNotFoundError as exc:
        print(f"INFRA ERROR: {exc}", file=sys.stderr)
        return 2
    except subprocess.TimeoutExpired:
        print("INFRA ERROR: flyctl logs timed out", file=sys.stderr)
        return 2
    except subprocess.CalledProcessError as exc:
        print(f"INFRA ERROR: flyctl logs failed (exit {exc.returncode}): {exc.stderr}", file=sys.stderr)
        return 2

    summary = summarize(parse_events(text))

    if summary.total < MIN_CALLS_TO_EVALUATE:
        print(f"OK: only {summary.total} triage call(s) in this window — nothing to alert on")
        return 0

    error_rate = summary.error_count / summary.total
    breaches = []
    if error_rate > MAX_ERROR_RATE:
        breaches.append(
            f"error rate {error_rate:.0%} exceeds threshold {MAX_ERROR_RATE:.0%} "
            f"({summary.error_count}/{summary.total} calls failed)"
        )
    if summary.p95_latency_ms > MAX_P95_LATENCY_MS:
        breaches.append(
            f"p95 latency {summary.p95_latency_ms:.0f}ms exceeds threshold {MAX_P95_LATENCY_MS:.0f}ms"
        )

    if breaches:
        print("ALERT: triage health check failed")
        for breach in breaches:
            print(f"  - {breach}")
        return 1

    print(
        f"OK: {summary.total} calls, {error_rate:.0%} error rate, "
        f"{summary.p95_latency_ms:.0f}ms p95 latency"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
