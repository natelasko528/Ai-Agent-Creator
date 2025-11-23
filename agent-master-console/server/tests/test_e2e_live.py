import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Ensure we are not in mock mode
os.environ["MOCK_MODE"] = "0"

if "OPENAI_API_KEY" not in os.environ:
    pytest.skip("Live agent test requires OPENAI_API_KEY", allow_module_level=True)

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from main import app

client = TestClient(app)

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"

def test_create_list_chat():
    payload = {
        "name": "TestAgent",
        "model": "gpt-4.1-mini",
        "system_prompt": "You are a friendly assistant.",
        "tools": []
    }
    res = client.post("/agents", json=payload)
    assert res.status_code == 200
    agent = res.json()
    agent_id = agent["id"]

    res = client.get("/agents")
    assert any(a["id"] == agent_id for a in res.json())

    with client.websocket_connect(f"/ws/{agent_id}") as ws:
        ws.send_text("hello")
        reply = ws.receive_text()
        assert isinstance(reply, str)
