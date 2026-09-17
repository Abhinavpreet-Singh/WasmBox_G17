"""WebSocket /ws/executions endpoint tests — Week 2 Day 9."""

import json

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from src.api.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_ws_rejects_empty_source(client):
    with client.websocket_connect("/ws/executions") as ws:
        ws.send_text(
            json.dumps(
                {
                    "type": "run",
                    "source": "",
                }
            )
        )

        frame = json.loads(ws.receive_text())

    assert frame["event"] == "error"
    assert (
        "source" in frame["detail"].lower()
        or "artifact" in frame["detail"].lower()
    )


@patch("src.api.websocket.record_execution_result")
def test_ws_blocks_malicious_source(
    mock_record,
    client,
):
    with client.websocket_connect("/ws/executions") as ws:
        ws.send_text(
            json.dumps(
                {
                    "type": "run",
                    "source": 'open("/etc/passwd").read()',
                }
            )
        )

        frame = json.loads(ws.receive_text())

    assert frame["event"] == "done"
    assert frame["status"] == "blocked"

    mock_record.assert_called_once()


def test_ws_invalid_json(client):
    with client.websocket_connect("/ws/executions") as ws:
        ws.send_text("not json at all")

        frame = json.loads(ws.receive_text())

    assert frame["event"] == "error"


def test_ws_unknown_artifact_id_returns_error(client):
    with client.websocket_connect("/ws/executions") as ws:
        ws.send_text(
            json.dumps(
                {
                    "artifact_id": "nonexistent_artifact_xyz"
                }
            )
        )

        frame = json.loads(ws.receive_text())

        # First frame: execution started.
        assert frame["event"] == "start"

        # Second frame: artifact was not found.
        frame2 = json.loads(ws.receive_text())

        assert frame2["event"] == "error"