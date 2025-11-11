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
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from langchain.chat_models import init_chat_model
from resume_chatbot_api.core.config import settings


class LLMOperator:
    """
    A unified asynchronous interface for executing resume-related tasks
    using a LangChain-compatible chat model.

    """       
    def __init__(self):
        self.model = self._init_chat_model()

    def _init_chat_model(self):
        
        if settings.langchain_provider == "openai":
            # Requires: pip install -U langchain langchain-openai
            # api_key can also come from env; passing is fine too
            return init_chat_model(
                settings.openai_model,
                model_provider="openai",
                api_key=settings.openai_api_key,
                temperature=settings.llm_temperature,
            )
        else:  # ollama
            # Requires: pip install -U langchain langchain-ollama
            return init_chat_model(
                settings.ollama_model,
                model_provider="ollama",
                base_url=settings.ollama_base_url,
                temperature=settings.llm_temperature,
            )


    # ---------- Chains (most common) ----------
    def create_chain(self, system_prompt: str, schema: Type[Any]):
        """
        Returns a LangChain chat chain with standardized prompt and output parsing.
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),      
            ("user", "{user}"),
        ])

         # Prefer native structured output if available
        with_structured = getattr(self.model, "with_structured_output", None)
        if callable(with_structured):
            structured = self.model.with_structured_output(schema)  # returns a new Runnable
            chain = prompt | structured  # already returns a dict matching the schema
        else:
            # Fallback: force JSON and parse with Pydantic
            parser = PydanticOutputParser(pydantic_object=schema)
            json_mode = self.model.bind(response_format={"type": "json_object"})  # new Runnable
            chain = prompt | json_mode | StrOutputParser() | parser
            
        return chain
    
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

    