"""
Tests for CareerBridge AI REST API Endpoints
"""
import uuid
import pytest
from fastapi.testclient import TestClient
from app.backend.main import app

client = TestClient(app)

def test_health_endpoint():
    """Verify that GET /health returns 200 and correct status metadata."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "CareerBridge AI" in data["service"]
    assert "SDG 8" in data["sdg"]

def test_chat_endpoint_success():
    """Verify that POST /chat responds with 200 and expected schema."""
    session_id = f"test-session-{uuid.uuid4()}"
    payload = {
        "message": "Which skills should I learn for a career in AI?",
        "session_id": session_id
    }
    response = client.post("/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert len(data["response"]) > 0
    assert data["session_id"] == session_id
    assert "readiness_snapshot" in data

def test_chat_endpoint_empty_message():
    """Verify that POST /chat returns 400 on empty message."""
    payload = {
        "message": "   ",
        "session_id": "test-empty"
    }
    response = client.post("/chat", json=payload)
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data or "error" in data

def test_reset_endpoint():
    """Verify that POST /reset clears session and returns 200."""
    session_id = f"test-reset-{uuid.uuid4()}"
    # Add a chat message first
    client.post("/chat", json={"message": "I am learning Python", "session_id": session_id})

    # Reset
    response = client.post("/reset", json={"session_id": session_id})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["session_id"] == session_id
