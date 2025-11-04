import os
from typing import Optional, List, Literal
from pydantic import Field
from pydantic_settings import BaseSettings

Provider = Literal["openai", "ollama"]

class Settings(BaseSettings):
    # Generic LLM config
    LANGCHAIN_PROVIDER: Provider = Field("openai", env="LANGCHAIN_PROVIDER")
    MODEL: str = Field("gpt-4o-mini", env="LLM_MODEL")
    TEMPERATURE: float = Field(0.0, env="LLM_TEMPERATURE")
    MAX_TOKENS: Optional[int] = Field(None, env="LLM_MAX_TOKENS")

    # OpenAI / Azure OpenAI
    OPENAI_API_KEY: Optional[str] = Field(None, env=("LLM_API_KEY", "OPENAI_API_KEY"))

    # Ollama
    OLLAMA_MODEL: str = Field("llama3.2", env="OLLAMA_MODEL")
    OLLAMA_BASE_URL: str = Field("http://localhost:11434", env="OLLAMA_BASE_URL")

    # App config
    API_VERSION: str = Field("v1", env="API_VERSION")
    API_TITLE: str = Field("Resume Chatbot API", env="API_TITLE")
    API_DESCRIPTION: str = Field("An API for generating resumes with AI assistance.", env="API_DESCRIPTION")
    DATABASE_URL: str = Field("sqlite:///./test.db", env="DATABASE_URL")
    DEBUG: bool = Field(False, env="DEBUG")
    ALLOWED_HOSTS: List[str] = Field(["*"], env="ALLOWED_HOSTS")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def create_chat_llm(self):
        """
        Returns a provider-specific LangChain ChatModel with a unified interface.
        Use .invoke()/ainvoke()/.stream()/astream().
        """
        provider = self.LANGCHAIN_PROVIDER.lower()

        if provider == "openai":
            # OpenAI
            try:
                from langchain_openai import ChatOpenAI
            except Exception as exc:
                raise RuntimeError("Missing deps. Install: pip/uv add langchain-openai openai") from exc

            if self.OPENAI_API_KEY:
                os.environ.setdefault("OPENAI_API_KEY", self.OPENAI_API_KEY)

            return ChatOpenAI(
                model=self.MODEL,
                temperature=self.TEMPERATURE,
                max_tokens=self.MAX_TOKENS,
            )

        if provider == "ollama":
            try:
                from langchain_ollama import ChatOllama
            except Exception as exc:
                raise RuntimeError("Missing deps. Install: langchain-ollama httpx") from exc

            return ChatOllama(
                base_url=self.OLLAMA_BASE_URL,
                model=self.OLLAMA_MODEL,
                temperature=self.TEMPERATURE,
                # max_tokens ignored by some local models; safe to include if supported
            )

        raise ValueError(f"Unsupported LANGCHAIN_PROVIDER: {provider}")


# instantiate once for app-wide usage
settings = Settings()

class Config:
    API_VERSION = os.getenv("API_VERSION", settings.API_VERSION)
    API_TITLE = os.getenv("API_TITLE", settings.API_TITLE)
    API_DESCRIPTION = os.getenv("API_DESCRIPTION", settings.API_DESCRIPTION)
    LLM_API_KEY = settings.OPENAI_API_KEY
    LLM_MODEL = os.getenv("LLM_MODEL", settings.MODEL)
    LLM_PROVIDER = os.getenv("LANGCHAIN_PROVIDER", settings.LANGCHAIN_PROVIDER)
    LLM_TEMPERATURE = settings.TEMPERATURE
    DATABASE_URL = os.getenv("DATABASE_URL", settings.DATABASE_URL)
    DEBUG = os.getenv("DEBUG", str(settings.DEBUG)) == "True"
    # Tip: pydantic-settings expects JSON for list envs; if you export "['a','b']" it parses automatically.
    ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", ",".join(settings.ALLOWED_HOSTS)).split(",")
