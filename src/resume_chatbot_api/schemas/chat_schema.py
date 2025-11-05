"""
Chat Schemas
============

This module defines Pydantic data models for the chatbot API.

These schemas represent:
- Incoming user requests
- AI-generated resume suggestions
- Chat responses and conversation history

They are used throughout the `/chat` endpoints and LLM operators to ensure
type safety, documentation, and automatic OpenAPI schema generation.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ChatRequest(BaseModel):
    """
    Incoming request from the user.

    This model represents the structure of data sent to the chatbot,
    containing the user message and optional profile or resume content.

    Attributes
    ----------
    message : str
        The user's message or question for the chatbot.
    profile : Optional[str]
        A resume text or structured profile (JSON string), used to
        personalize the chatbot’s suggestions.
    user_id : Optional[str]
        Optional unique user identifier (useful for chat history or
        personalization).
    """

    message: str = Field(..., description="User message or resume-related question.")
    profile: Optional[str] = Field(
        None,
        description="Optional resume or profile data to contextualize the response.",
    )
    user_id: Optional[str] = Field(
        None, description="Optional unique identifier for the user."
    )


class ResumeSuggestion(BaseModel):
    """
    Structured output returned by the LLM for resume-related suggestions.

    This schema is designed to capture both structured and fallback
    (raw text) responses from the LLM, providing flexibility for
    various model output formats.

    Attributes
    ----------
    summary : Optional[str]
        One-sentence summary or contextual overview.
    bullets : Optional[List[str]]
        List of concise bullet-point improvement suggestions.
    skills : Optional[List[str]]
        Extracted or recommended skills from the user's profile or message.
    raw_text : Optional[str]
        Raw text fallback in case structured parsing fails.
    """

    summary: Optional[str] = Field(
        None, description="Short one-sentence overview or context summary."
    )
    bullets: Optional[List[str]] = Field(
        None, description="Concise bullet-point suggestions."
    )
    skills: Optional[List[str]] = Field(
        None, description="Extracted or recommended skills."
    )
    raw_text: Optional[str] = Field(
        None, description="Raw text response (for fallback if JSON parse fails)."
    )


class ChatResponse(BaseModel):
    """
    Combined chatbot response model.

    Contains both the original user request and the structured
    AI-generated resume suggestion.

    Attributes
    ----------
    original : ChatRequest
        The original message and profile data submitted by the user.
    suggestion : ResumeSuggestion
        Structured AI response generated from the LLM.
    """

    original: ChatRequest = Field(..., description="The original user request.")
    suggestion: ResumeSuggestion = Field(..., description="AI-generated suggestions.")


class ChatMessage(BaseModel):
    """
    Representation of a single message in a conversation.

    This model can represent messages from either the user or
    the chatbot assistant, with a timestamp for chronological ordering.

    Attributes
    ----------
    user_id : str
        Unique identifier for the user or system participant.
    message : str
        Text content of the message.
    timestamp : datetime
        UTC timestamp marking when the message was sent.
    """

    user_id: str = Field(
        ..., description="Identifier for the sender (user or assistant)."
    )
    message: str = Field(..., description="Text content of the message.")
    timestamp: datetime = Field(..., description="Timestamp of message creation (UTC).")


class ChatSchema(BaseModel):
    """
    Snapshot of a full chat conversation.

    Useful for tracking multi-turn dialogue or generating
    summarized transcripts.

    Attributes
    ----------
    messages : List[ChatMessage]
        The ordered sequence of messages in the conversation.
    response : ChatResponse
        The most recent chatbot-generated response.
    """

    messages: List[ChatMessage] = Field(
        ..., description="List of all messages in the conversation."
    )
    response: ChatResponse = Field(
        ..., description="Latest chatbot response for the given messages."
    )
