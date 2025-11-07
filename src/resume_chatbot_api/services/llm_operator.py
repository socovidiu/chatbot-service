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
from typing import Any, Dict, Optional, Union
import json
import re

from langchain_core.messages import SystemMessage, HumanMessage
from . import prompt_builders as pb


class LLMOperator:
    """
    A unified asynchronous interface for executing resume-related tasks
    using a LangChain-compatible chat model.

    Parameters
    ----------
    chat_llm : Any
        A LangChain chat model instance, such as
        :class:`langchain_openai.ChatOpenAI` or
        :class:`langchain_ollama.ChatOllama`.

    Example
    -------
    >>> from core.config import settings
    >>> from services.llm_operator import LLMOperator
    >>> llm = LLMOperator(settings.create_chat_llm())
    >>> result = await llm.extract_keywords("Job description text here")
    """

    def __init__(self, chat_llm: Any):
        self.llm = chat_llm

    # ----------------------------------------------------------------------
    # Internal helpers
    # ----------------------------------------------------------------------
    async def _ainvoke_text(self, system: str, user: str) -> str:
        """
        Invoke the LLM asynchronously and return raw text content.

        Parameters
        ----------
        system : str
            System prompt defining the LLM's role and context.
        user : str
            User input prompt.

        Returns
        -------
        str
            The raw textual output of the LLM.
        """
        msgs = [
            SystemMessage(content=system.strip()),
            HumanMessage(content=user.strip()),
        ]
        resp = await self.llm.ainvoke(msgs)
        return getattr(resp, "content", str(resp))

    async def _invoke_json(
        self,
        system: str,
        user: str,
        schema_hint: Optional[str],
    ) -> Dict[str, Any]:
        """
        Invoke the LLM expecting a valid JSON response.

        This method enforces strict JSON output by appending a
        schema hint and parsing the model's response accordingly.

        Parameters
        ----------
        system : str
            System prompt defining task context and role.
        user : str
            User query prompt.
        schema_hint : Optional[str]
            Optional JSON schema hint to guide the model output.

        Returns
        -------
        dict
            Parsed JSON data returned by the LLM.

        Raises
        ------
        ValueError
            If the model fails to return valid JSON.
        """
        guard = (
            "\n\nReturn ONLY valid JSON that matches the schema. "
            "No backticks, no markdown, no extra commentary."
        )
        if schema_hint:
            guard += f"\nJSON schema (shape): {schema_hint}"

        raw = await self._ainvoke_text(system, user + guard)
        # Fast path
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass

        # Handle ```json ... ``` fenced blocks (some models still add them)
        fenced = re.search(r"```json\s*(\{.*?\}|\[.*?\])\s*```", raw, re.S | re.I)
        if fenced:
            return json.loads(fenced.group(1))

        # Extract first JSON-looking top-level object/array (non-greedy)
        m = re.search(r"(\{.*\}|\[.*\])", raw, re.S)
        if m:
            try:
                return json.loads(m.group(1))
            except json.JSONDecodeError as e:
                raise ValueError(f"JSON fragment invalid: {e}; fragment starts: {m.group(1)[:200]}")

        # Nothing JSON-like
        raise ValueError(f"Model did not return JSON. First 200 chars: {raw[:200]}")

    # ----------------------------------------------------------------------
    # Public task methods
    # ----------------------------------------------------------------------
    async def analyze_profile(
        self, profile: Union[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Analyze and canonicalize a resume profile.

        Extracts structured information (skills, education, experience)
        from raw text or JSON profile data.

        Parameters
        ----------
        profile : str | dict
            The user's resume or structured profile data.

        Returns
        -------
        dict
            Analysis result of the profile as a JSON-compatible dictionary.
        """
        system, user, schema = pb.analyze_profile(profile)
        return await self._invoke_json(system, user, schema)

    async def extract_keywords(self, jd: str) -> Dict[str, Any]:
        """
        Extract relevant keywords from a job description.

        Parameters
        ----------
        jd : str
            The job description text.

        Returns
        -------
        dict
            Keywords grouped by type (e.g., skills, qualifications).
        """
        system, user, schema = pb.extract_keywords(jd)
        return await self._invoke_json(system, user, schema)

    async def tailor_bullets(
        self, profile: Dict[str, Any], jd: str, tone: str = "concise"
    ) -> Dict[str, Any]:
        """
        Tailor resume bullet points to a specific job description.

        Parameters
        ----------
        profile : dict
            Canonicalized user profile data.
        jd : str
            Target job description.
        tone : str, optional
            Desired tone of the tailored bullets (default is "concise").

        Returns
        -------
        dict
            Tailored bullet points and rationale.
        """
        system, user, schema = pb.tailor_bullets(profile, jd, tone)
        return await self._invoke_json(system, user, schema)

    async def write_summary(
        self, profile: Dict[str, Any], jd: Optional[str]
    ) -> Dict[str, Any]:
        """
        Generate a professional summary for the resume.

        Parameters
        ----------
        profile : dict
            Canonicalized user profile data.
        jd : Optional[str]
            Target job description, if available.

        Returns
        -------
        dict
            Generated summary and supporting details.
        """
        system, user, schema = pb.write_summary(profile, jd)
        return await self._invoke_json(system, user, schema)

    async def write_cover_letter(
        self,
        profile: Dict[str, Any],
        jd: str,
        company: Optional[str],
        role: Optional[str],
    ) -> Dict[str, Any]:
        """
        Generate a customized cover letter.

        Parameters
        ----------
        profile : dict
            Canonicalized user profile data.
        jd : str
            Job description text.
        company : Optional[str]
            Target company name.
        role : Optional[str]
            Target role title.

        Returns
        -------
        dict
            Generated cover letter text and structure.
        """
        system, user, schema = pb.write_cover_letter(profile, jd, company, role)
        return await self._invoke_json(system, user, schema)

    async def ats_score(self, resume_text: str, jd: str) -> Dict[str, Any]:
        """
        Compute an ATS (Applicant Tracking System) compatibility score.

        Parameters
        ----------
        resume_text : str
            Raw resume text.
        jd : str
            Target job description.

        Returns
        -------
        dict
            Contains the computed ATS score, matching breakdown, and suggestions.
        """
        system, user, schema = pb.ats_score(resume_text, jd)
        return await self._invoke_json(system, user, schema)

    # --- NEW: simple freeform chat entrypoint ------------------------------
    async def chat(
        self,
        prompt: str,
        profile: Optional[Union[str, Dict[str, Any]]] = None,
        system: Optional[str] = None,
    ) -> str:
        """
        Lightweight chat method for ad-hoc prompts (used by /chat).
        If a profile is provided, it’s injected as context.
        """
        ctx = ""
        if isinstance(profile, dict):
            import json as _json
            ctx = f"\n\nUser profile (JSON):\n{_json.dumps(profile, ensure_ascii=False)}"
        elif isinstance(profile, str) and profile.strip():
            ctx = f"\n\nUser profile (text):\n{profile.strip()}"

        system = system or (
            "You are a resume-writing assistant. Be concise and helpful. "
            "Return plain text; no markdown, no code fences."
        )
        user = f"{prompt.strip()}{ctx}"
        return await self._ainvoke_text(system, user)