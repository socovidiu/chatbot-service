"""
Application Configuration
=========================

This module defines configuration management for the Resume Chatbot API.
It leverages :class:`pydantic_settings.BaseSettings` to automatically load
environment variables and provides a consistent interface for managing
application-level and LLM-related configuration.

It also exposes a helper method, :meth:`Settings.create_chat_llm`, which
instantiates a LangChain-compatible chat model depending on the selected
provider (`openai` or `ollama`).

Usage
-----
Typical usage for the API service:

>>> from core.config import settings
>>> llm = settings.create_chat_llm()
>>> print(settings.LANGCHAIN_PROVIDER)
'openai'

The `settings` instance is meant to be imported across the app for unified
configuration access.
"""

import os
from typing import Optional, List, Literal
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# ----------------------------------------------------------------------
# Type aliases and constants
# ----------------------------------------------------------------------
Provider = Literal["openai", "ollama"]


class Settings(BaseSettings):
    """
    Application and LLM configuration model.

    This class centralizes environment variables and runtime configuration.
    It automatically loads variables from `.env` files, system environment,
    or defaults defined here.

    Attributes
    ----------
    LANGCHAIN_PROVIDER : Literal["openai", "ollama"]
        Which LLM provider to use for LangChain integration.
    MODEL : str
        Model identifier (e.g., ``gpt-4o-mini`` or ``llama3.2``).
    TEMPERATURE : float
        Controls randomness in LLM responses.
    MAX_TOKENS : Optional[int]
        Optional token limit for model completions.
    OPENAI_API_KEY : Optional[str]
        API key for OpenAI provider.
    OLLAMA_MODEL : str
        Model name used for Ollama.
    OLLAMA_BASE_URL : str
        Base URL for Ollama local API endpoint.
    API_VERSION : str
        Version identifier for the API.
    API_TITLE : str
        Human-readable title for API docs.
    API_DESCRIPTION : str
        Description used in FastAPI and Sphinx docs.
    DATABASE_URL : str
        Connection string for persistent storage (default: SQLite).
    DEBUG : bool
        Whether to enable debug mode for development.
    ALLOWED_HOSTS : List[str]
        Whitelisted hosts for CORS and network configuration.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",          # <- prevents “Extra inputs are not permitted”
    )

    # --- LLM config ---
    LANGCHAIN_PROVIDER: Provider = Field("openai", env="LANGCHAIN_PROVIDER")
    MODEL: str = Field("gpt-4o-mini", env="LLM_MODEL")
    TEMPERATURE: float = Field(0.0, env="LLM_TEMPERATURE")
    MAX_TOKENS: Optional[int] = Field(None, env="LLM_MAX_TOKENS")

    # OpenAI
    OPENAI_API_KEY: Optional[str] = Field(None, env=("LLM_API_KEY", "OPENAI_API_KEY"))

    # Ollama
    OLLAMA_MODEL: str = Field("llama3.2", env="OLLAMA_MODEL")
    OLLAMA_BASE_URL: str = Field("http://localhost:11434", env="OLLAMA_BASE_URL")

    # --- App config ---
    API_VERSION: str = Field("v1", env="API_VERSION")
    API_TITLE: str = Field("Resume Chatbot API", env="API_TITLE")
    API_DESCRIPTION: str = Field(
        "An API for generating resumes with AI assistance.", env="API_DESCRIPTION"
    )
    DATABASE_URL: str = Field("sqlite:///./test.db", env="DATABASE_URL")
    DEBUG: bool = Field(False, env="DEBUG")
    ALLOWED_HOSTS: List[str] = Field(["*"], env="ALLOWED_HOSTS")

    # API key header + keys for your own service
    API_KEY_HEADER: str = Field("X-API-Key", env="LLM_API_KEY_HEADER")
    API_KEYS: List[str] = Field(default_factory=list, env="LLM_API_KEYS")

    # Parse CSV strings (".env": LLM_API_KEYS=a,b,c) into lists
    @field_validator("ALLOWED_HOSTS", "API_KEYS", mode="before")
    @classmethod
    def _split_csv(cls, v):
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()]
        return v
    # ----------------------------------------------------------------------
    # LLM factory
    # ----------------------------------------------------------------------
    def create_chat_llm(self):
        """
        Create and return a LangChain ChatModel instance.

        This helper dynamically imports and initializes the correct chat model
        based on the selected `LANGCHAIN_PROVIDER`.

        Supported providers
        -------------------
        - **OpenAI** (`langchain_openai.ChatOpenAI`)
        - **Ollama** (`langchain_ollama.ChatOllama`)

        Returns
        -------
        ChatModel
            A LangChain-compatible chat model instance with unified interface.
            Supports `.invoke()`, `.ainvoke()`, `.stream()`, and `.astream()`.

        Raises
        ------
        RuntimeError
            If required dependencies are missing.
        ValueError
            If an unsupported provider is configured.

        Example
        -------
        >>> settings = Settings()
        >>> chat_model = settings.create_chat_llm()
        >>> response = await chat_model.ainvoke("Hello, world!")
        """
        provider = self.LANGCHAIN_PROVIDER.lower()

        if provider == "openai":
            try:
                from langchain_openai import ChatOpenAI
            except Exception as exc:
                raise RuntimeError(
                    "Missing deps. Install with: pip/uv add langchain-openai openai"
                ) from exc

            if self.OPENAI_API_KEY:
                os.environ.setdefault("OPENAI_API_KEY", self.OPENAI_API_KEY)

            return ChatOpenAI(
                model=self.MODEL,
                temperature=self.TEMPERATURE,
                model_kwargs={"response_format": {"type": "json_object"}},
                max_tokens=self.MAX_TOKENS,
            )

        if provider == "ollama":
            try:
                from langchain_ollama import ChatOllama
            except Exception as exc:
                raise RuntimeError(
                    "Missing deps. Install with: pip/uv add langchain-ollama httpx"
                ) from exc

            return ChatOllama(
                base_url=self.OLLAMA_BASE_URL,
                model=self.OLLAMA_MODEL,
                temperature=self.TEMPERATURE,
                model_kwargs={"format": "json"},
            )

        raise ValueError(f"Unsupported LANGCHAIN_PROVIDER: {provider}")


# ----------------------------------------------------------------------
# Global configuration instances
# ----------------------------------------------------------------------
settings = Settings()
"""
Global `Settings` instance loaded at import time.

Intended for application-wide use; imports this module once and reuses the
same settings across routers and services.
"""


class Config:
    """
    Lightweight static config wrapper for FastAPI and internal modules.

    This class mirrors a subset of environment variables to simplify
    access for components that do not depend on `pydantic-settings`.
    """

    API_VERSION = os.getenv("API_VERSION", settings.API_VERSION)
    API_TITLE = os.getenv("API_TITLE", settings.API_TITLE)
    API_DESCRIPTION = os.getenv("API_DESCRIPTION", settings.API_DESCRIPTION)
    LLM_API_KEY = settings.OPENAI_API_KEY
    LLM_MODEL = os.getenv("LLM_MODEL", settings.MODEL)
    LLM_PROVIDER = os.getenv("LANGCHAIN_PROVIDER", settings.LANGCHAIN_PROVIDER)
    LLM_TEMPERATURE = settings.TEMPERATURE
    DATABASE_URL = os.getenv("DATABASE_URL", settings.DATABASE_URL)
    DEBUG = os.getenv("DEBUG", str(settings.DEBUG)) == "True"
    ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", ",".join(settings.ALLOWED_HOSTS)).split(
        ","
    )
