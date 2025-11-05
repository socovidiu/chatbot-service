"""
Chat API Routes
===============

This module defines the FastAPI router for handling chatbot interactions.
It exposes endpoints that interact with the LLMOperator to generate
resume-related suggestions based on user messages and optional profile data.

The routes here are automatically included in the main FastAPI app.
"""

from fastapi import APIRouter, HTTPException
from schemas.chat_schema import ChatRequest, ChatResponse, ResumeSuggestion
from services.llm_operator import LLMOperator
from core.config import settings

# Initialize FastAPI router
router = APIRouter()

# Instantiate the LLM operator with the configured provider
llm = LLMOperator(settings.create_chat_llm())


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Generate AI-powered resume suggestions.

    This endpoint receives a user message and an optional resume profile,
    then uses the configured LLM (e.g., OpenAI, Ollama) to generate tailored
    resume suggestions.

    Parameters
    ----------
    request : ChatRequest
        The user's message and optional resume/profile data.

    Returns
    -------
    ChatResponse
        A structured response containing the original request and the
        generated AI suggestions.

    Raises
    ------
    HTTPException
        - 400: If the message field is empty or missing.
        - 500: If an internal error occurs during LLM processing.

    Example
    -------
    >>> POST /chat
    {
        "message": "Help me improve my resume summary for a data scientist role.",
        "profile": "3 years as data analyst, proficient in Python and SQL"
    }

    Response
    --------
    {
        "original": {...},
        "suggestion": {
            "raw_text": "Consider emphasizing your analytical experience..."
        }
    }
    """
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    try:
        text = await llm.generate(request)
        return ChatResponse(
            original=request, suggestion=ResumeSuggestion(raw_text=text)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
