"""
LLM Operator Service
====================

This module defines the :class:`LLMOperator`, a high-level asynchronous wrapper
around LangChain chat-based language models. It provides standardized methods
for performing resume-specific NLP tasks using an underlying LLM, including:

- Profile analysis and canonicalization
- Keyword extraction from job descriptions
- Tailoring bullet points
- Writing professional summaries and cover letters
- Computing ATS (Applicant Tracking System) compatibility scores

Each method delegates prompt construction to :mod:`services.prompt_builders`
and enforces a consistent JSON-based output schema.
"""

from __future__ import annotations
from typing import Any, List, Callable, Type
from langchain.agents import create_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain.chat_models import init_chat_model
# from langchain_openai import ChatOpenAI
# from langchain_ollama import ChatOllama
from core.config import settings


class LLMOperator:
    """
    A unified asynchronous interface for executing resume-related tasks
    using a LangChain-compatible chat model.

    """       
    def __init__(self):
        self.model = self._init_chat_model()

    def _init_chat_model(self):
        # Common kwargs
        common = {}
        if settings.llm_temperature is not None:
            common["temperature"] = settings.llm_temperature
        if settings.llm_max_tokens is not None:
            common["max_tokens"] = settings.llm_max_tokens

        if settings.langchain_provider == "openai":
            # Requires: pip install -U langchain langchain-openai
            # api_key can also come from env; passing is fine too
            return init_chat_model(
                settings.openai_model,
                model_provider="openai",
                api_key=settings.openai_api_key,
                **common,
            )
        else:  # ollama
            # Requires: pip install -U langchain langchain-ollama
            return init_chat_model(
                settings.ollama_model,
                model_provider="ollama",
                base_url=settings.ollama_base_url,
                **common,
            )

    # def create_chat_llm(self):
    #     if settings.langchain_provider == "ollama":
    #         return ChatOllama(
    #             model=settings.ollama_model,
    #             base_url=settings.ollama_base_url,
    #             temperature=settings.llm_temperature,
    #             # LangChain ChatOllama supports max_tokens via num_predict internally
    #             num_predict=settings.llm_max_tokens,
    #         )
    #     elif self.provider == "openai":
    #         return ChatOpenAI(
    #             model=settings.openai_model,
    #             temperature=settings.llm_temperature,
    #             max_tokens=settings.llm_max_tokens,
    #             # The response_format below tells GPT-4o to emit valid JSON
    #             model_kwargs={"response_format": {"type": "json_object"}},
    #             api_key=settings.openai_api_key,
    #         )
    #     else:
    #         raise ValueError(f"Unsupported provider: {self.provider}")
        
    # ---------- Chains (no tools, no memory, no recursion risk) ----------
    def create_chain(self, system_prompt: str, schema: Type[Any]):
        """
        Returns a Runnable chain: { 'user': <text> } -> Pydantic output.
        Prefer this for endpoints that don't need tools.
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", "{user}"),
        ])

        # Newer LangChain builds: model.with_structured_output(...)
        with_structured = getattr(self.model, "with_structured_output", None)
        if callable(with_structured):
            structured_model = self.model.with_structured_output(schema)
            return prompt | structured_model

        # Fallback: some builds accept response_format on the model
        return prompt | self.model.bind(response_format=schema)

    # ---------- Agents (only when you need tools) ----------
    def create_agent(self, tools: List[Callable], system_prompt: str, schema: Type[Any]):
        """
        Returns an Agent (plan/act). Use only if you really need tools.
        """
        agent = create_agent(
            model=self.model,
            tools=tools,
            system_prompt=system_prompt,
            response_format=schema,   # structured output without .with_structured_output
        )
        return agent

    