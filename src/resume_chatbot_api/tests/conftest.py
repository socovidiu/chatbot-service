import pytest
import os

os.environ.setdefault("API_KEY", "test-key")
os.environ.setdefault("LANGCHAIN_PROVIDER", "ollama")
os.environ.setdefault("API_KEY_HEADER", "X-API-Key")

from fastapi.testclient import TestClient
from resume_chatbot_api.app import app
from resume_chatbot_api.core.config import settings
from resume_chatbot_api.core.security import require_api_key

app.dependency_overrides[require_api_key] = lambda: "test-key"


@pytest.fixture(scope="session")
def client():
    """Provides a reusable FastAPI test client."""
    return TestClient(app)

@pytest.fixture(scope="session")
def valid_api_key():
    """Provides a valid API key for authenticated requests."""
    # Fallback to a dummy key if not defined in env/settings
    return require_api_key if getattr(settings, "API_KEYS", None) else "test-key"

@pytest.fixture(scope="session")
def api_key_header_name():
    """Header name for the API key (if customizable)."""
    return getattr(settings, "api_key_header", "x-api-key")
