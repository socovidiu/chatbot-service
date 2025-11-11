"""
Application Entry Point
=======================

This module initializes the FastAPI application for the **Resume Chatbot API**.

It wires together all API routers (chat, resume, etc.) and configures the
main metadata used in both Sphinx-generated documentation and the FastAPI
OpenAPI schema (Swagger UI).

Modules
-------
- :mod:`api.chat` — Chat endpoints for AI-assisted resume suggestions.
- :mod:`api.resume` — Resume analysis, tailoring, and keyword extraction endpoints.
- :mod:`core.config` — Environment-based configuration and provider setup.

Usage
-----
You can run this app directly using:

.. code-block:: bash

    uv run uvicorn app:app --reload

The OpenAPI/Swagger UI is available at:
    http://localhost:8000/docs
"""

from fastapi import FastAPI, Security
from resume_chatbot_api.api import resume
from resume_chatbot_api.core.config import settings
from resume_chatbot_api.core.security import require_api_key
# ----------------------------------------------------------------------
# FastAPI Application Initialization
# ----------------------------------------------------------------------
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    dependencies=[Security(require_api_key)]
)


# ----------------------------------------------------------------------
# Router Registration
# ----------------------------------------------------------------------
app.include_router(resume.router, tags=["resume"])


# ----------------------------------------------------------------------
# Root Endpoint
# ----------------------------------------------------------------------
@app.get("/", tags=["root"])
def read_root():
    """
    Root endpoint for health check and basic information.

    Returns
    -------
    dict
        A simple JSON message confirming that the API is running.

    Example
    -------
    >>> GET /
    {
        "message": "Welcome to the Resume Chatbot API. Use the /chat endpoint to interact with the chatbot."
    }
    """
    return {
        "message": (
            "Welcome to the Resume Chatbot API. "
            "Use the /chat endpoint to interact with the chatbot."
        )
    }


# Export the app for ASGI servers (e.g., uvicorn, hypercorn)
export_app = app
"""
Alias for the FastAPI application object, to comply with ASGI export conventions.
"""
