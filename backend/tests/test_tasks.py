from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_and_list_task() -> None:
    response = client.post("/tasks", json={"title": "Write CLAUDE.md"})
    assert response.status_code == 201
    created = response.json()
    assert created["title"] == "Write CLAUDE.md"
    assert created["status"] == "todo"
    assert created["priority"] == "medium"

    listed = client.get("/tasks").json()
    assert any(task["id"] == created["id"] for task in listed)


def test_get_task() -> None:
    created = client.post("/tasks", json={"title": "Design data model"}).json()
    fetched = client.get(f"/tasks/{created['id']}")
    assert fetched.status_code == 200
    assert fetched.json()["id"] == created["id"]


def test_update_task() -> None:
    created = client.post("/tasks", json={"title": "Ship phase 01"}).json()
    updated = client.patch(f"/tasks/{created['id']}", json={"status": "doing"})
    assert updated.status_code == 200
    body = updated.json()
    assert body["status"] == "doing"
    assert body["updated_at"] != created["updated_at"]


def test_delete_task() -> None:
    created = client.post("/tasks", json={"title": "Delete me"}).json()
    deleted = client.delete(f"/tasks/{created['id']}")
    assert deleted.status_code == 204
    assert client.get(f"/tasks/{created['id']}").status_code == 404


def test_unknown_task_returns_404() -> None:
    assert client.get("/tasks/does-not-exist").status_code == 404
    assert client.patch("/tasks/does-not-exist", json={"status": "done"}).status_code == 404
    assert client.delete("/tasks/does-not-exist").status_code == 404


def test_create_task_without_title_is_rejected() -> None:
    response = client.post("/tasks", json={"description": "no title given"})
    assert response.status_code == 422
