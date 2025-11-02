import pytest
from fastapi.testclient import TestClient
from app.src.app import app  # or ensure PYTHONPATH=app/src so `from app.app import app` works

@pytest.fixture
def client():
    return TestClient(app)

def test_chat_response(client):
    response = client.post("/chat", json={"message": "Hello, I need help with my resume."})
    assert response.status_code == 200
    assert "suggestion" in response.json()

def test_chat_invalid_input(client):
    response = client.post("/chat", json={"message": ""})
    assert response.status_code == 400
    assert response.json() == {"detail": "Message cannot be empty."}

def test_suggest_basic(client):
    payload = {"message": "Help me tailor my resume for a data scientist role.", "profile": "3 years as data analyst, Python, SQL"}
    r = client.post("/chat/suggest", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert "suggestion" in data
