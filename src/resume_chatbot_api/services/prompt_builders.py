# services/prompt_builders.py
"""
Prompt Builders
===============

This module centralizes all prompt construction for resume-related tasks.
Each function returns a **(system, user, schema_hint)** tuple that can be
passed to the LLM operator. The `schema_hint` is a lightweight hint used by
the caller to enforce/validate JSON-shaped outputs.

Return type alias:
    SystemUserSchema = Tuple[str, str, Optional[str]]

Design goals
------------
- Keep prompt text small, explicit, and close to the target schema.
- Provide a minimal `schema_hint` string that describes the shape or fields.
- Avoid model/provider-specific tokens or formatting here; keep it generic.
"""

from __future__ import annotations
from typing import Any, Dict, Optional, Tuple, Union
import json

SystemUserSchema = Tuple[str, str, Optional[str]]
"""Tuple containing (system_prompt, user_prompt, optional_schema_hint)."""


def _dump(obj: Union[str, Dict[str, Any], None]) -> str:
    """
    Serialize a profile-like object for prompt inclusion.

    Parameters
    ----------
    obj : str | dict | None
        The object to serialize. Strings are returned as-is; dictionaries
        are converted to pretty JSON; None becomes an empty string.

    Returns
    -------
    str
        A human-readable string suitable for prompt embedding.
    """
    if obj is None:
        return ""
    if isinstance(obj, str):
        return obj
    return json.dumps(obj, ensure_ascii=False, indent=2)


def analyze_profile(profile: Union[str, Dict[str, Any]]) -> SystemUserSchema:
    """
    Build prompts to canonicalize a resume/profile into a standard shape.

    Parameters
    ----------
    profile : str | dict
        Raw resume text or structured JSON profile.

    Returns
    -------
    (system, user, schema_hint) : tuple[str, str, str]
        Instructional system prompt, user prompt with embedded data,
        and a short schema hint identifier.
    """
    system = "You are a resume structuring assistant."
    user = f"""
Input profile (may be free text or JSON):
{_dump(profile)}

Normalize into this shape:
{{
  "name": null | string,
  "title": null | string,
  "summary": null | string,
  "skills": [string, ...],
  "experience": [
    {{
      "company": string,
      "role": string,
      "start": null | string,
      "end": null | string,
      "bullets": [string, ...]
    }}
  ],
  "education": [
    {{
      "school": string,
      "degree": null | string,
      "year": null | string
    }}
  ]
}}
""".strip()
    return system, user, "CanonicalProfile"


def extract_keywords(jd: str) -> SystemUserSchema:
    """
    Build prompts to extract job-relevant keywords from a JD.

    Parameters
    ----------
    jd : str
        Job description text.

    Returns
    -------
    (system, user, schema_hint) : tuple[str, str, str]
        Prompts plus a schema hint describing expected keys.
    """
    system = "You extract skills and hiring signals from job descriptions."
    user = f"""
Job description:
{jd}

Return:
{{
  "skills": [string, ...],
  "keywords": [string, ...],
  "seniority": "junior|mid|senior|lead|principal|null",
  "nice_to_have": [string, ...]
}}
""".strip()
    return system, user, "skills/keywords/seniority"


def tailor_bullets(profile: Dict[str, Any], jd: str, tone: str) -> SystemUserSchema:
    """
    Build prompts to tailor resume bullets to a target JD.

    Parameters
    ----------
    profile : dict
        Canonicalized (or near-canonical) resume profile.
    jd : str
        Target job description text.
    tone : str
        Desired tone of output (e.g., 'concise', 'confident').

    Returns
    -------
    (system, user, schema_hint) : tuple[str, str, str]
        Prompts plus a schema hint describing bullets/focus/removed arrays.
    """
    system = "You write quantified, impact-focused resume bullets aligned to a job."
    user = f"""
Profile:
{_dump(profile)}

Job description:
{jd}

Tone: {tone}

Return:
{{
  "bullets": [string, ...],   // 4-6 bullets, STAR-style, quantified where possible
  "removed": [string, ...],   // skills/experiences not aligned to JD
  "focus": [string, ...]      // top 3-5 keywords to emphasize
}}
""".strip()
    return system, user, "bullets/removed/focus"


def write_summary(profile: Dict[str, Any], jd: Optional[str]) -> SystemUserSchema:
    """
    Build prompts to generate a crisp, 2–3 line professional summary.

    Parameters
    ----------
    profile : dict
        Canonicalized profile data.
    jd : Optional[str]
        Optional job description for contextual relevance.

    Returns
    -------
    (system, user, schema_hint) : tuple[str, str, str]
        Prompts plus a schema hint for the ``summary`` field.
    """
    system = "You write crisp professional summaries (2-3 lines)."
    user = f"""
Profile:
{_dump(profile)}

Job description (optional):
{jd or ""}

Return: {{ "summary": string }}
""".strip()
    return system, user, '{"summary": string}'


def write_cover_letter(
    profile: Dict[str, Any], jd: str, company: Optional[str], role: Optional[str]
) -> SystemUserSchema:
    """
    Build prompts to generate a short, specific cover letter (≤ 180 words).

    Parameters
    ----------
    profile : dict
        Canonicalized profile data.
    jd : str
        Job description text.
    company : Optional[str]
        Target company name (if known).
    role : Optional[str]
        Target role title (if known).

    Returns
    -------
    (system, user, schema_hint) : tuple[str, str, str]
        Prompts plus a schema hint for the ``cover_letter`` field.
    """
    system = "You draft short, specific cover letters (≤180 words)."
    user = f"""
Profile:
{_dump(profile)}

Job description:
{jd}

Company: {company or "Unknown"}
Role: {role or "Unknown"}

Return: {{ "cover_letter": string }}
""".strip()
    return system, user, '{"cover_letter": string}'


def ats_score(resume_text: str, jd: str) -> SystemUserSchema:
    """
    Build prompts to compute a heuristic ATS compatibility score.

    Parameters
    ----------
    resume_text : str
        Raw resume text to evaluate.
    jd : str
        Target job description text.

    Returns
    -------
    (system, user, schema_hint) : tuple[str, str, str]
        Prompts plus a schema hint describing score, gaps, and keyword_match.
    """
    system = "You are an ATS heuristic evaluator."
    user = f"""
Resume:
{resume_text}

Job description:
{jd}

Return:
{{
  "score": int,                  // 0-100
  "gaps": [string, ...],
  "recommendations": [string, ...],
  "keyword_match": {{
    "present": [string, ...],
    "missing": [string, ...]
  }}
}}
""".strip()
    return system, user, "score/gaps/recommendations/keyword_match"
