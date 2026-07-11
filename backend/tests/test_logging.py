import logging

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_request_logging_emits_one_event_per_request(caplog) -> None:
    with caplog.at_level(logging.INFO, logger="taskflow"):
        response = client.get("/health")

    assert response.status_code == 200
    assert "X-Request-ID" in response.headers

    request_records = [r for r in caplog.records if r.name == "taskflow" and r.getMessage() == "request"]
    assert len(request_records) == 1

    fields = request_records[0].args
    assert fields["method"] == "GET"
    assert fields["path"] == "/health"
    assert fields["status_code"] == 200
    assert fields["request_id"] == response.headers["X-Request-ID"]
    assert isinstance(fields["latency_ms"], float)
