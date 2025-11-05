import pytest
from fastapi.testclient import TestClient
from resume_chatbot_api.app import app
from resume_chatbot_api.core.config import settings  # adjust path if needed

@pytest.fixture(scope="session")
def client():
    """Provides a reusable FastAPI test client."""
    return TestClient(app)

@pytest.fixture(scope="session")
def valid_api_key():
    """Provides a valid API key for authenticated requests."""
    # Fallback to a dummy key if not defined in env/settings
    return settings.API_KEYS[0] if getattr(settings, "API_KEYS", None) else "test-key"

@pytest.fixture(scope="session")
def api_key_header_name():
    """Header name for the API key (if customizable)."""
    return getattr(settings, "API_KEY_HEADER", "x-api-key")
