
def test_rejects_missing_key(client):
    respomse = client.get("/")
    assert respomse.status_code in (401, 403)

def test_accepts_valid_key(client, valid_api_key, api_key_header_name):
    response = client.get("/", headers={api_key_header_name: valid_api_key})
    assert response.status_code == 200
    assert response.json().get("ok") is True

def test_chat_response(client,monkeypatch):
    """Test that /chat returns a suggestion field."""
    
    # Mock the LLMOperator.generate to avoid real API calls
    async def mock_generate(request):
        return "Here’s a mock resume suggestion."

    # Patch the LLMOperator inside the app's router
    from resume_chatbot_api.api import chat
    monkeypatch.setattr(chat.llm, "generate", mock_generate)

    response = client.post("/chat", json={"message": "Hello, I need help with my resume."})
    
    assert response.status_code == 200
    data = response.json()
    assert "suggestion" in data
    assert "raw_text" in data["suggestion"]
    assert "mock" in data["suggestion"]["raw_text"].lower()


def test_chat_invalid_input(client):
    """Test that empty message returns HTTP 400."""
    response = client.post("/chat", json={"message": ""})
    assert response.status_code == 400
    assert response.json() == {"detail": "Message cannot be empty."}

