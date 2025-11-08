# core/config.py
from __future__ import annotations
import json
from typing import Optional, List, Literal
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

Provider = Literal["openai", "ollama"]

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ---- Provider selection ----
    langchain_provider: Provider = Field("openai", env="LANGCHAIN_PROVIDER")

    # ---- OpenAI ----
    openai_model: str = Field("gpt-4o-mini", env=("OPENAI_MODEL", "LLM_MODEL"))
    openai_api_key: Optional[str] = Field(None, env=("OPENAI_API_KEY", "LLM_API_KEY"))

    # ---- Shared LLM params ----
    llm_temperature: float = Field(0.0, env="LLM_TEMPERATURE")
    llm_max_tokens: Optional[int] = Field(None, env="LLM_MAX_TOKENS")

    # ---- Ollama ----
    ollama_model: str = Field("llama3.2", env=("OLLAMA_MODEL", "LLM_MODEL"))
    ollama_base_url: str = Field("http://localhost:11434", env="OLLAMA_BASE_URL")


    # ---- API metadata ----
    API_TITLE: str = Field("Resume Chatbot API", env="API_TITLE")
    API_VERSION: str = Field("1.0.0", env="API_VERSION")
    API_DESCRIPTION: str = Field("An API for interacting with a resume chatbot powered by LLMs.", env="API_DESCRIPTION")
    # ---- API key auth ----
    api_key_header: str = Field("X-API-Key", env="API_KEY_HEADER")
    api_keys: List[str] = Field(default_factory=list, env="API_KEYS")

    @field_validator("api_keys", mode="before")
    @classmethod
    def parse_api_keys(cls, v):
        if not v:
            return []
        if isinstance(v, list):
            return v
        s = str(v).strip()
        # JSON list?
        if s.startswith("["):
            try:
                parsed = json.loads(s)
                return [str(x) for x in parsed]
            except Exception:
                pass
        # Comma-separated
        return [seg.strip() for seg in s.split(",") if seg.strip()]

    # ---- Helpers ----
    @property
    def resolved_model(self) -> str:
        return self.openai_model if self.langchain_provider == "openai" else self.ollama_model

    @property
    def resolved_base_url(self) -> Optional[str]:
        return None if self.langchain_provider == "openai" else self.ollama_base_url

settings = Settings()
