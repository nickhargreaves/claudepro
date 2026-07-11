import time

import anthropic

from app.config import settings
from app.logging_config import log_event
from app.models import Task, TaskPriority, TriageSuggestion

_client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

# Verify against https://www.anthropic.com/pricing before trusting
# estimated_cost_usd for real budgeting — these are illustrative constants,
# not pulled from a live pricing source, and will go stale.
_INPUT_COST_PER_MTOK = 1.00
_OUTPUT_COST_PER_MTOK = 5.00

_TRIAGE_TOOL = {
    "name": "suggest_priority",
    "description": "Suggest a priority level for a task with a short rationale.",
    "input_schema": {
        "type": "object",
        "properties": {
            "priority": {"type": "string", "enum": ["low", "medium", "high"]},
            "rationale": {
                "type": "string",
                "description": "One sentence explaining the suggestion.",
            },
        },
        "required": ["priority", "rationale"],
    },
}


def suggest_priority(task: Task) -> TriageSuggestion:
    start = time.perf_counter()
    try:
        message = _client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=200,
            tools=[_TRIAGE_TOOL],
            tool_choice={"type": "tool", "name": "suggest_priority"},
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Suggest a priority for this task.\n\n"
                        f"Title: {task.title}\n"
                        f"Description: {task.description or '(none)'}"
                    ),
                }
            ],
        )
    except Exception:
        _log_triage_call(task, start, status="error")
        raise

    for block in message.content:
        if block.type == "tool_use" and block.name == "suggest_priority":
            try:
                suggestion = TriageSuggestion(
                    priority=TaskPriority(block.input["priority"]),
                    rationale=block.input["rationale"],
                )
            except (KeyError, ValueError):
                # Model returned a tool call that doesn't match our schema
                # (e.g. a priority outside the enum) — log it as the
                # failure it is, not as a successful call.
                _log_triage_call(task, start, status="error")
                raise
            _log_triage_call(
                task,
                start,
                status="ok",
                priority=suggestion.priority.value,
                input_tokens=message.usage.input_tokens,
                output_tokens=message.usage.output_tokens,
            )
            return suggestion

    _log_triage_call(task, start, status="error")
    raise RuntimeError("Claude did not return a triage suggestion")


def _log_triage_call(
    task: Task,
    start: float,
    *,
    status: str,
    priority: str | None = None,
    input_tokens: int = 0,
    output_tokens: int = 0,
) -> None:
    estimated_cost_usd = round(
        (input_tokens * _INPUT_COST_PER_MTOK + output_tokens * _OUTPUT_COST_PER_MTOK) / 1_000_000,
        6,
    )
    log_event(
        "triage_call",
        task_id=task.id,
        status=status,
        priority=priority,
        latency_ms=round((time.perf_counter() - start) * 1000, 2),
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        estimated_cost_usd=estimated_cost_usd,
    )
