from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN
from typing import Optional

from core.config import settings

# Build the header extractor dynamically from config
_api_key_header = APIKeyHeader(name=settings.api_key_header, auto_error=False)
print("Loaded API keys:", settings.api_key)  # should show your key(s)
print("Loaded API keys:", settings.api_key_header)  # should show your key(s)


def require_api_key(api_key: Optional[str] = Security(_api_key_header)) -> str:
    """
    Accepts requests *only* if the configured API key is present and valid.
    Returns the key so handlers can use it if needed.
    """

    if not settings.api_key:
        # Misconfiguration: no keys defined
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="API key auth not configured."
        )

    if not api_key:
        # No header provided -> 401 (so clients know to add credentials)
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED, detail="Missing API key header."
        )

    if api_key not in settings.api_key:
        raise HTTPException(status_code=HTTP_403_FORBIDDEN, detail="Invalid API key.")

    return api_key
