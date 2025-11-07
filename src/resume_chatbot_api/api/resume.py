"""
Resume API Routes
=================

This module defines the FastAPI endpoints for AI-powered resume analysis,
keyword extraction, tailoring, and optimization. It integrates with the
:class:`services.llm_operator.LLMOperator` to perform specialized
resume-related NLP tasks such as:

- Parsing and canonicalizing user profiles.
- Extracting job-relevant keywords.
- Tailoring bullet points and summaries for specific roles.
- Generating cover letters.
- Computing ATS (Applicant Tracking System) compatibility scores.

Each route returns a structured Pydantic response defined in
:mod:`schemas.resume_schemas`.
"""

from fastapi import APIRouter, HTTPException
from core.config import settings
from services.llm_operator import LLMOperator
from schemas.resume_schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    CanonicalProfile,
    JDRequest,
    KeywordsResponse,
    TailorRequest,
    TailorResponse,
    SummaryRequest,
    SummaryResponse,
    CoverLetterRequest,
    CoverLetterResponse,
    ATSScoreRequest,
    ATSScoreResponse,
)

# Define router and instantiate LLM operator
router = APIRouter(prefix="/resume", tags=["resume"])
llm = LLMOperator(settings.create_chat_llm())


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest) -> AnalyzeResponse:
    """
    Analyze and canonicalize a user's resume profile.

    Takes a raw or structured resume profile, and returns a standardized
    representation including key fields such as experience, education,
    and skills.

    Parameters
    ----------
    req : AnalyzeRequest
        Input request containing the user's resume data.

    Returns
    -------
    AnalyzeResponse
        A structured canonical profile extracted from the input.

    Raises
    ------
    HTTPException
        500 if the LLM processing fails.
    """
    try:
        # If your operator expects a dict, send a dict:
        payload = req.canonical.model_dump()
        data: dict = await llm.analyze_profile(payload)  
        if "canonical" in data and isinstance(data["canonical"], dict):
            data = data["canonical"]
        return AnalyzeResponse(**data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"analyze failed: {e}")



@router.post("/keywords", response_model=KeywordsResponse)
async def keywords(req: JDRequest) -> KeywordsResponse:
    """
    Extract important keywords from a job description.

    This endpoint helps identify critical terms and skills to optimize
    resume tailoring and ATS scoring.

    Parameters
    ----------
    req : JDRequest
        Request containing a job description.

    Returns
    -------
    KeywordsResponse
        Extracted keywords grouped by categories such as skills,
        responsibilities, and soft skills.
    """
    try:
        data = await llm.extract_keywords(req.job_description)
        return KeywordsResponse(**data)
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/tailor", response_model=TailorResponse)
async def tailor(req: TailorRequest) -> TailorResponse:
    """
    Tailor resume bullet points to a specific job description.

    Uses the user profile and job description to rewrite or enhance
    bullet points that align with the desired role.

    Parameters
    ----------
    req : TailorRequest
        Profile, job description, and tone for the tailored suggestions.

    Returns
    -------
    TailorResponse
        Contains tailored resume bullet points and supporting context.
    """
    try:
        profile = (
            req.profile if isinstance(req.profile, dict) else req.profile.model_dump()
        )
        data = await llm.tailor_bullets(
            profile, req.job_description, tone=req.tone or "concise"
        )
        return TailorResponse(**data)
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/summary", response_model=SummaryResponse)
async def summary(req: SummaryRequest) -> SummaryResponse:
    """
    Generate a professional summary for a resume.

    Creates a concise and compelling profile summary based on the user's
    experience and the target job description.

    Parameters
    ----------
    req : SummaryRequest
        Profile data and target job description.

    Returns
    -------
    SummaryResponse
        Generated summary text and optional extracted keywords.
    """
    try:
        profile = (
            req.profile if isinstance(req.profile, dict) else req.profile.model_dump()
        )
        data = await llm.write_summary(profile, req.job_description)
        return SummaryResponse(**data)
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/cover-letter", response_model=CoverLetterResponse)
async def cover_letter(req: CoverLetterRequest) -> CoverLetterResponse:
    """
    Generate a tailored cover letter.

    Creates a professional cover letter based on a user’s profile,
    job description, target company, and desired role.

    Parameters
    ----------
    req : CoverLetterRequest
        Profile, job description, company, and role data.

    Returns
    -------
    CoverLetterResponse
        AI-generated cover letter text and optional analysis fields.
    """
    try:
        profile = (
            req.profile if isinstance(req.profile, dict) else req.profile.model_dump()
        )
        data = await llm.write_cover_letter(
            profile, req.job_description, req.company, req.role
        )
        return CoverLetterResponse(**data)
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/ats-score", response_model=ATSScoreResponse)
async def ats(req: ATSScoreRequest) -> ATSScoreResponse:
    """
    Compute an ATS (Applicant Tracking System) compatibility score.

    Evaluates how well a resume aligns with a given job description
    based on keyword matching and structure quality.

    Parameters
    ----------
    req : ATSScoreRequest
        Resume text and target job description.

    Returns
    -------
    ATSScoreResponse
        Contains the computed ATS score, key insights, and suggestions.
    """
    try:
        if req.resume_text:
            data = await llm.ats_score(req.resume_text, req.job_description)
        else:
            # Derive a text view if your operator wants text, or pass canonical if it supports it
            profile_dict = req.canonical.model_dump()
            data = await llm.ats_score_from_canonical(profile_dict, req.job_description)
        return ATSScoreResponse(**data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ats-score failed: {e}")
