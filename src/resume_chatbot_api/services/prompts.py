# services/prompts.py
"""
Minimal prompt helpers for resume endpoints.
- One system prompt constant per task
- Tiny user-message builders that inject request data
- No schema hints or JSON frames (schemas enforce shape)

Usage:
    from services.prompts import SYSTEM_ANALYZE, build_analyze_user
    agent = llm.create_agent(tools=[], system_prompt=SYSTEM_ANALYZE, schema=AnalyzeResponse)
    result = await agent.ainvoke({"messages": [{"role": "user", "content": build_analyze_user(req)}]})
"""

from __future__ import annotations
from pydantic import BaseModel


# -------------------------- System prompts --------------------------

SYSTEM_ANALYZE = """
You are an expert resume reviewer and ATS evaluator.
"Your task is to analyze the provided resume profile and return a JSON 
object that strictly follows the AnalyzeResponse schema.
Do not output extra text or keys. Do not leave any field empty or set to 0.
Provide concrete insights based on the resume content. Use factual phrasing.
""".strip()

SYSTEM_KEYWORDS = """
You extract skills and hiring signals from job descriptions.
Return only fields defined by the output schema. Be concise and useful for screening.
""".strip()

SYSTEM_TAILOR = """
You write quantified, impact-focused resume bullets tailored to a specific job.
Use truthful details from the profile, align with the JD, and prioritize measurable outcomes.
Follow the output schema strictly.
""".strip()

SYSTEM_SUMMARY = """
You craft crisp, 2–3 line professional summaries.
Be specific, outcome-oriented, and aligned with the target role. Follow the schema.
""".strip()

SYSTEM_COVER_LETTER = """
You write short, specific cover letters (≤180 words), tailored to the company and role.
Focus on fit, outcomes, and authenticity. Follow the schema.
""".strip()

SYSTEM_ATS = """
You are an ATS heuristic evaluator.
Compare resume content to the job description and produce a fair, actionable assessment.
Follow the schema strictly.
""".strip()


# -------------------------- User builders ---------------------------

def build_analyze_user(req: BaseModel) -> str:
    """For AnalyzeRequest: embed canonical profile JSON."""
    # req is AnalyzeRequest; it has .canonical
    return (
        "Analyze the following canonical profile and return ONLY the schema fields.\n\n"
        f"```json\n{req.model_dump_json()}\n```"
    )

def build_keywords_user(req: BaseModel) -> str:
    """For JDRequest: embed JD text."""
    jd = getattr(req, "job_description", "") or ""
    return (
        "Extract job-relevant skills/keywords/seniority from the following JD. "
        "Return ONLY the schema fields.\n\n"
        f"{jd}"
    )

def build_tailor_user(req: BaseModel) -> str:
    """For TailorRequest: embed profile JSON + JD + tone."""
    profile_json = getattr(req, "profile").model_dump_json()
    jd = getattr(req, "job_description", "") or ""
    tone = getattr(req, "tone", "concise") or "concise"
    return (
        "Tailor resume bullets to the job description below. "
        "Return ONLY the schema fields.\n\n"
        f"Tone: {tone}\n\n"
        f"Profile (JSON):\n```json\n{profile_json}\n```\n\n"
        f"Job Description:\n{jd}"
    )

def build_summary_user(req: BaseModel) -> str:
    """For SummaryRequest: 2–3 line summary; optional JD."""
    profile_json = getattr(req, "profile").model_dump_json()
    jd = getattr(req, "job_description", None)
    return (
        "Write a concise 2–3 line professional summary. "
        "Return ONLY the schema fields.\n\n"
        f"Profile (JSON):\n```json\n{profile_json}\n```\n\n"
        f"Job Description (optional):\n{jd or ''}"
    )

def build_cover_letter_user(req: BaseModel) -> str:
    """For CoverLetterRequest: ≤180 words; include company/role if present."""
    profile_json = getattr(req, "profile").model_dump_json()
    jd = getattr(req, "job_description", "") or ""
    company = getattr(req, "company", None) or "Unknown"
    role = getattr(req, "role", None) or "Unknown"
    return (
        "Write a short, specific cover letter (≤180 words). "
        "Return ONLY the schema fields.\n\n"
        f"Company: {company}\nRole: {role}\n\n"
        f"Profile (JSON):\n```json\n{profile_json}\n```\n\n"
        f"Job Description:\n{jd}"
    )

def build_ats_user(req: BaseModel) -> str:
    """For ATSScoreRequest: handle either resume_text or canonical profile."""
    jd = getattr(req, "job_description", "") or ""
    resume_text = getattr(req, "resume_text", None)
    canonical = getattr(req, "canonical", None)

    if canonical is not None:
        body = f"Canonical Profile (JSON):\n```json\n{canonical.model_dump_json()}\n```"
    else:
        body = f"Resume Text:\n{resume_text or ''}"

    return (
        "Compute a heuristic ATS score and related fields. "
        "Return ONLY the schema fields.\n\n"
        f"{body}\n\n"
        f"Job Description:\n{jd}"
    )
