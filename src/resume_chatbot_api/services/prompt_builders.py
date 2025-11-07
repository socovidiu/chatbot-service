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
    schema = "quality/strengths/gaps/risks/recommendations/section_scores/keyword_clusters/anomalies"
    system = "You are a resume analyst for software/tech resumes."
    user = f"""
            Canonical profile (JSON):
            {_dump(profile)}

            Return a JSON object EXACTLY in this shape:
            {{
            "quality": 0,
            "strengths": [],
            "gaps": [],
            "risks": [],
            "recommendations": [],
            "section_scores": {{"summary": 0, "experience": 0, "education": 0, "skills": 0}},
            "keyword_clusters": {{"core": [], "tools": [], "soft": []}},
            "anomalies": []
            }}
            Rules:
            - DO NOT return empty lists unless truly none exist. If something is unclear, infer from the profile.
            - "quality": 0–100. Start at 50, add up to +25 for strong experience, +15 for quantified impact, +10 for breadth (tools/cloud), subtract for missing sections.
            - "strengths": at least 2 concrete strengths.
            - "gaps": at least 2 concrete gaps (e.g., “no metrics”, “missing cloud certs”).
            - "risks": mention timeline issues (date gaps, frequent short roles) if any; otherwise [].
            - "recommendations": 3–5 actionable next steps.
            - "section_scores": integers 0–5 for summary/experience/education/skills.
            - "keyword_clusters": split skills into core (languages/primary stacks), tools (DevOps, cloud, frameworks), soft (communication/leadership).
            - "anomalies": inconsistent dates, overlapping roles, etc.
            Return ONLY the JSON object.
            """.strip()
    return system, user, schema


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

            Return a JSON object exactly like this shape (values are examples):
            {{
            "skills": [],
            "keywords": [],
            "seniority": null,
            "nice_to_have": []
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

            Return a JSON object with this shape:
            {{
            "bullets": [],
            "removed": [],
            "focus": []
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

            Return a JSON object:
            {{ "summary": "" }}
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

            Return a JSON object:
            {{ "cover_letter": "" }}
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

            Return a JSON object with this shape:
            {{
            "score": 0,
            "gaps": [],
            "recommendations": [],
            "keyword_match": {{
                "present": [],
                "missing": []
            }}
            }}
            """.strip()

    return system, user, "score/gaps/recommendations/keyword_match"
