import logging
from types import SimpleNamespace

from fastapi.testclient import TestClient

import app.triage as triage_module
from app.main import app
from app.models import TaskPriority, TaskStatus, TriageSuggestion

client = TestClient(app)


def test_triage_returns_suggestion(monkeypatch) -> None:
    created = client.post("/tasks", json={"title": "Fix prod outage"}).json()

    def fake_suggest_priority(task):
        return TriageSuggestion(priority=TaskPriority.high, rationale="Outages are urgent.")

    monkeypatch.setattr("app.main.suggest_priority", fake_suggest_priority)

    response = client.post(f"/tasks/{created['id']}/triage")
    assert response.status_code == 200
    body = response.json()
    assert body["priority"] == "high"
    assert body["rationale"] == "Outages are urgent."


def test_triage_unknown_task_returns_404() -> None:
    assert client.post("/tasks/does-not-exist/triage").status_code == 404


def test_triage_upstream_failure_returns_502(monkeypatch) -> None:
    created = client.post("/tasks", json={"title": "Anything"}).json()

    def failing_suggest_priority(task):
        raise RuntimeError("Claude API unavailable")

    monkeypatch.setattr("app.main.suggest_priority", failing_suggest_priority)

    response = client.post(f"/tasks/{created['id']}/triage")
    assert response.status_code == 502


def _make_task() -> object:
    from datetime import UTC, datetime

    from app.models import Task

    now = datetime.now(UTC)
    return Task(
        id="t1",
        title="Fix prod outage",
        description="",
        status=TaskStatus.todo,
        priority=TaskPriority.medium,
        created_at=now,
        updated_at=now,
    )


def test_suggest_priority_logs_triage_call_on_success(monkeypatch, caplog) -> None:
    fake_message = SimpleNamespace(
        content=[
            SimpleNamespace(
                type="tool_use",
                name="suggest_priority",
                input={"priority": "high", "rationale": "Outages are urgent."},
            )
        ],
        usage=SimpleNamespace(input_tokens=42, output_tokens=7),
    )
    monkeypatch.setattr(triage_module._client.messages, "create", lambda **kwargs: fake_message)

    with caplog.at_level(logging.INFO, logger="taskflow"):
        result = triage_module.suggest_priority(_make_task())

    assert result.priority == TaskPriority.high

    events = [r for r in caplog.records if r.name == "taskflow" and r.getMessage() == "triage_call"]
    assert len(events) == 1
    fields = events[0].args
    assert fields["status"] == "ok"
    assert fields["task_id"] == "t1"
    assert fields["input_tokens"] == 42
    assert fields["output_tokens"] == 7
    assert fields["estimated_cost_usd"] > 0


def test_suggest_priority_logs_triage_call_on_failure(monkeypatch, caplog) -> None:
    def raise_error(**kwargs):
        raise RuntimeError("Claude API unavailable")

    monkeypatch.setattr(triage_module._client.messages, "create", raise_error)

    with caplog.at_level(logging.INFO, logger="taskflow"):
        try:
            triage_module.suggest_priority(_make_task())
        except RuntimeError:
            pass

    events = [r for r in caplog.records if r.name == "taskflow" and r.getMessage() == "triage_call"]
    assert len(events) == 1
    assert events[0].args["status"] == "error"
    assert events[0].args["task_id"] == "t1"
