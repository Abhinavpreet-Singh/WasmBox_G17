"""WebSocket /ws/executions endpoint tests — Week 2 Day 9."""

import json

import pytest
from fastapi.testclient import TestClient

from src.api.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_ws_rejects_empty_source(client):
    with client.websocket_connect("/ws/executions") as ws:
        ws.send_text(json.dumps({"type": "run", "source": ""}))
        frame = json.loads(ws.receive_text())
    assert frame["event"] == "error"
    assert "source" in frame["detail"].lower() or "artifact" in frame["detail"].lower()


def test_ws_blocks_malicious_source(client):
    with client.websocket_connect("/ws/executions") as ws:
        ws.send_text(json.dumps({"type": "run", "source": 'open("/etc/passwd").read()'}))
        frame = json.loads(ws.receive_text())
    assert frame["event"] == "done"
    assert frame["status"] == "blocked"


def test_ws_invalid_json(client):
    with client.websocket_connect("/ws/executions") as ws:
        ws.send_text("not json at all")
        frame = json.loads(ws.receive_text())
    assert frame["event"] == "error"


def test_ws_unknown_artifact_id_returns_error(client):
    with client.websocket_connect("/ws/executions") as ws:
        ws.send_text(json.dumps({"artifact_id": "nonexistent_artifact_xyz"}))
        frame = json.loads(ws.receive_text())  # start
        assert frame["event"] == "start"
        frame2 = json.loads(ws.receive_text())  # error — file not found
        assert frame2["event"] == "error"
