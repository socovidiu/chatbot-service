# services/prompt_builders.py
from __future__ import annotations
from typing import Any, Dict, Optional, Tuple, Union
import json

SystemUserSchema = Tuple[str, str, Optional[str]]

def _dump(obj: Union[str, Dict[str, Any], None]) -> str:
    if obj is None:
        return ""
    if isinstance(obj, str):
        return obj
    return json.dumps(obj, ensure_ascii=False, indent=2)

def analyze_profile(profile: Union[str, Dict[str, Any]]) -> SystemUserSchema:
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
    system = "You write crisp professional summaries (2-3 lines)."
    user = f"""
Profile:
{_dump(profile)}

Job description (optional):
{jd or ""}

Return: {{ "summary": string }}
""".strip()
    return system, user, '{"summary": string}'

def write_cover_letter(profile: Dict[str, Any], jd: str, company: Optional[str], role: Optional[str]) -> SystemUserSchema:
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
