import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./test_smoke.db")

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Ensure static exists before app import
Path("static").mkdir(exist_ok=True)
Path("media").mkdir(exist_ok=True)

from app.main import app  # noqa: E402

client = TestClient(app)


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["version"] == "0.1.0-phase-0-1"
    assert body["phase"] == "0-1"
    assert "built_at" in body
    assert len(body["built_at"]) >= 10


def test_card_and_note_crud():
    card = client.post("/api/cards", json={"title": "C1"}).json()
    note = client.post("/api/notes", json={"title": "N1"}).json()
    assert card["title"] == "C1"
    assert note["title"] == "N1"
    assert isinstance(card.get("number"), int) and card["number"] >= 1
    assert isinstance(note.get("number"), int) and note["number"] >= 1
    assert card.get("created_at")
    assert note.get("created_at")
    card2 = client.post("/api/cards", json={"title": "C2"}).json()
    assert card2["number"] > card["number"]
    updated = client.put(f"/api/cards/{card['id']}", json={"title": "C1b", "number": 99999}).json()
    assert updated["number"] == card["number"]
    sized = client.put(
        f"/api/cards/{card['id']}",
        json={"width": 420, "height": 180},
    ).json()
    assert sized["width"] == 420
    assert sized["height"] == 180
    r = client.put(f"/api/cards/{card['id']}", json={"title": "C2"})
    assert r.json()["title"] == "C2"


def test_task_journal_parent_child():
    parent = client.post("/api/cards", json={"title": "Родитель"}).json()
    child = client.post(
        "/api/cards",
        json={"title": "Подзадача", "parent_id": parent["id"]},
    ).json()
    assert child["parent_id"] == parent["id"]
    reloaded = client.get(f"/api/cards/{child['id']}").json()
    assert reloaded["parent_id"] == parent["id"]


def test_note_task_attach_and_link():
    task = client.post("/api/cards", json={"title": "T1"}).json()
    note = client.post("/api/notes", json={"title": "N1"}).json()
    updated = client.put(
        f"/api/notes/{note['id']}",
        json={"task_id": task["id"]},
    ).json()
    assert updated["task_id"] == task["id"]
    link = client.post(
        "/api/task-links",
        json={
            "source_id": task["id"],
            "target_id": note["id"],
            "link_target_type": "note",
        },
    )
    assert link.status_code == 200
    note2 = client.get(f"/api/notes/{note['id']}").json()
    assert note2["task_id"] == task["id"]
    cleared = client.put(f"/api/notes/{note['id']}", json={"task_id": None}).json()
    assert cleared.get("task_id") is None


def test_note_attach_detach_editor_flow():
    """Mirrors store attachNoteToTask / detachNoteFromTask (task_id + task_link)."""
    task = client.post("/api/cards", json={"title": "Родитель"}).json()
    note = client.post("/api/notes", json={"title": "Заметка"}).json()

    client.put(f"/api/notes/{note['id']}", json={"task_id": task["id"]})
    link = client.post(
        "/api/task-links",
        json={
            "source_id": task["id"],
            "target_id": note["id"],
            "link_target_type": "note",
            "link_type": "depends_on",
        },
    ).json()

    after_attach = client.get(f"/api/notes/{note['id']}").json()
    assert after_attach["task_id"] == task["id"]
    links = client.get("/api/task-links").json()
    assert any(l["id"] == link["id"] for l in links)

    client.delete(f"/api/task-links/{link['id']}")
    client.put(f"/api/notes/{note['id']}", json={"task_id": None})

    after_detach = client.get(f"/api/notes/{note['id']}").json()
    assert after_detach.get("task_id") is None
    links_after = client.get("/api/task-links").json()
    assert not any(l.get("target_id") == note["id"] for l in links_after)


def test_create_note_with_task_id():
    task = client.post("/api/cards", json={"title": "T"}).json()
    note = client.post(
        "/api/notes",
        json={"title": "N", "task_id": task["id"]},
    ).json()
    assert note["task_id"] == task["id"]
    reloaded = client.get(f"/api/notes/{note['id']}").json()
    assert reloaded["task_id"] == task["id"]


def test_cascade_delete_task_with_subtasks_and_note():
    parent = client.post("/api/cards", json={"title": "Parent"}).json()
    child = client.post(
        "/api/cards",
        json={"title": "Child", "parent_id": parent["id"]},
    ).json()
    note = client.post(
        "/api/notes",
        json={"title": "Attached", "task_id": parent["id"]},
    ).json()
    r = client.delete(f"/api/cards/{parent['id']}", params={"cascade": True})
    assert r.status_code == 200
    assert client.get(f"/api/cards/{parent['id']}").status_code == 404
    assert client.get(f"/api/cards/{child['id']}").status_code == 404
    assert client.get(f"/api/notes/{note['id']}").status_code == 404


def test_task_link_cycle_rejected():
    a = client.post("/api/cards", json={"title": "A"}).json()
    b = client.post("/api/cards", json={"title": "B"}).json()
    client.post(
        "/api/task-links",
        json={"source_id": a["id"], "target_id": b["id"], "link_target_type": "task"},
    )
    r = client.post(
        "/api/task-links",
        json={"source_id": b["id"], "target_id": a["id"], "link_target_type": "task"},
    )
    assert r.status_code == 400
