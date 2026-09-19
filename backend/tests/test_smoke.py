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
    r = client.put(f"/api/cards/{card['id']}", json={"title": "C2"})
    assert r.json()["title"] == "C2"


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
