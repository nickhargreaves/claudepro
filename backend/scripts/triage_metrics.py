#!/usr/bin/env python3
"""Log-based dashboard for the triage endpoint.

Reads `triage_call` structured log events (see app/logging_config.py) and
prints an aggregate summary: call count, success/error split, avg + p95
latency, total estimated cost.

Usage:
    uv run scripts/triage_metrics.py                    # flyctl logs --json -a taskflow-nh-api --no-tail
    uv run scripts/triage_metrics.py --file path/to.log  # local JSON-lines file
    uv run scripts/triage_metrics.py --app my-app-name   # a different Fly app
"""

import argparse
import json
import statistics
import subprocess
import sys
from dataclasses import dataclass, field


@dataclass
class TriageEvent:
    status: str
    latency_ms: float
    input_tokens: int
    output_tokens: int
    estimated_cost_usd: float


@dataclass
class Summary:
    events: list[TriageEvent] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.events)

    @property
    def ok_count(self) -> int:
        return sum(1 for e in self.events if e.status == "ok")

    @property
    def error_count(self) -> int:
        return sum(1 for e in self.events if e.status == "error")

    @property
    def avg_latency_ms(self) -> float:
        if not self.events:
            return 0.0
        return sum(e.latency_ms for e in self.events) / len(self.events)

    @property
    def p95_latency_ms(self) -> float:
        latencies = [e.latency_ms for e in self.events]
        if not latencies:
            return 0.0
        if len(latencies) == 1:
            return latencies[0]
        # statistics.quantiles over a hand-rolled index, so the nearest-rank
        # math (easy to get off-by-one) is stdlib-tested, not ours to trust.
        return statistics.quantiles(latencies, n=100, method="inclusive")[94]

    @property
    def total_cost_usd(self) -> float:
        return sum(e.estimated_cost_usd for e in self.events)


def extract_app_event(raw_value: dict) -> dict | None:
    """A raw decoded JSON value is either our app's event directly (local
    JSON-lines) or a Fly log envelope with our event JSON-encoded inside
    `message` (flyctl logs --json). Returns the app event dict, or None if
    this value isn't one of our structured events."""
    if "event" in raw_value:
        return raw_value
    message = raw_value.get("message")
    if isinstance(message, str):
        try:
            decoded = json.loads(message)
        except json.JSONDecodeError:
            return None
        if isinstance(decoded, dict) and "event" in decoded:
            return decoded
    return None


def parse_events(text: str) -> list[dict]:
    """Fly's --json output is multiple pretty-printed JSON objects
    concatenated back to back (not JSON-lines, not a JSON array), so a
    plain json.loads() or line-by-line split doesn't work. Decode one
    top-level value at a time instead.

    A malformed chunk (a truncated log stream, a partial write) advances
    past just that one bad character and keeps scanning, rather than
    aborting the whole parse — one corrupt entry shouldn't silently drop
    every real event that follows it in the stream.
    """
    decoder = json.JSONDecoder()
    events = []
    idx = 0
    length = len(text)
    skipped = 0
    while idx < length:
        while idx < length and text[idx].isspace():
            idx += 1
        if idx >= length:
            break
        try:
            value, end = decoder.raw_decode(text, idx)
        except json.JSONDecodeError:
            idx += 1
            skipped += 1
            continue
        idx = end
        if isinstance(value, dict):
            app_event = extract_app_event(value)
            if app_event is not None:
                events.append(app_event)
    if skipped:
        print(f"warning: skipped {skipped} unparseable byte(s) in log stream", file=sys.stderr)
    return events


def fetch_logs(app: str) -> str:
    result = subprocess.run(
        ["flyctl", "logs", "-a", app, "--json", "--no-tail"],
        capture_output=True,
        text=True,
        timeout=30,
        check=True,
    )
    return result.stdout


def load_events_text(args: argparse.Namespace) -> str:
    """Shared --file-or-flyctl-logs loading, used by both this script and
    check_triage_health.py so the two don't drift out of sync."""
    if args.file:
        with open(args.file) as f:
            return f.read()
    return fetch_logs(args.app)


def add_common_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--file", help="Read events from a local JSON-lines file instead of flyctl logs")
    parser.add_argument("--app", default="taskflow-nh-api", help="Fly app name (default: taskflow-nh-api)")


def summarize(events: list[dict]) -> Summary:
    summary = Summary()
    for event in events:
        if event.get("event") != "triage_call":
            continue
        summary.events.append(
            TriageEvent(
                status=event.get("status", "unknown"),
                latency_ms=float(event.get("latency_ms", 0)),
                input_tokens=int(event.get("input_tokens", 0)),
                output_tokens=int(event.get("output_tokens", 0)),
                estimated_cost_usd=float(event.get("estimated_cost_usd", 0)),
            )
        )
    return summary


def print_report(summary: Summary) -> None:
    print("Triage call summary")
    print("--------------------")
    print(f"Total calls:     {summary.total}")
    print(f"  ok:            {summary.ok_count}")
    print(f"  error:         {summary.error_count}")
    print(f"Avg latency:     {summary.avg_latency_ms:.1f} ms")
    print(f"p95 latency:     {summary.p95_latency_ms:.1f} ms")
    print(f"Total est. cost: ${summary.total_cost_usd:.6f}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    add_common_args(parser)
    args = parser.parse_args()

    text = load_events_text(args)
    summary = summarize(parse_events(text))
    print_report(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
