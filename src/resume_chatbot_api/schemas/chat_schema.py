from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ChatRequest(BaseModel):
    """Incoming request from the user."""
    message: str
    profile: Optional[str] = None   # User's resume text or structured profile
    user_id: Optional[str] = None


class ResumeSuggestion(BaseModel):
    """Structured output returned by the LLM (for resume advice)."""
    summary: Optional[str] = Field(
        None, description="Short one-sentence overview or context summary"
    )
    bullets: Optional[List[str]] = Field(
        None, description="Concise bullet-point suggestions"
    )
    skills: Optional[List[str]] = Field(
        None, description="Extracted or recommended skills"
    )
    raw_text: Optional[str] = Field(
        None, description="Raw text response (for fallback if JSON parse fails)"
    )


class ChatResponse(BaseModel):
    """API response combining input and structured LLM output."""
    original: ChatRequest
    suggestion: ResumeSuggestion


class ChatMessage(BaseModel):
    """Represents a single user or assistant message in chat history."""
    user_id: str
    message: str
    timestamp: datetime


class ChatSchema(BaseModel):
    """A full conversation snapshot."""
    messages: List[ChatMessage]
    response: ChatResponse
