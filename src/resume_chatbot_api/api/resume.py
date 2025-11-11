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
from resume_chatbot_api.services.llm_operator import LLMOperator
from resume_chatbot_api.schemas.resume_schemas import (
    AnalyzeRequest, AnalyzeResponse,
    JDRequest, KeywordsResponse,
    TailorRequest, TailorResponse,
    SummaryRequest, SummaryResponse,
    CoverLetterRequest, CoverLetterResponse,
    ATSScoreRequest, ATSScoreResponse,
)
from resume_chatbot_api.services.prompts import (
    SYSTEM_ANALYZE, SYSTEM_KEYWORDS, SYSTEM_TAILOR,
    SYSTEM_SUMMARY, SYSTEM_COVER_LETTER, SYSTEM_ATS,
    build_analyze_user, build_keywords_user, build_tailor_user,
    build_summary_user, build_cover_letter_user, build_ats_user,
)


# ----------------------------------------------------------------------
# Router and LLM Initialization
# ----------------------------------------------------------------------
router = APIRouter(prefix="/resume", tags=["resume"])
"""
FastAPI router for all resume-related endpoints.

Routes under this router handle structured NLP tasks such as:
- Resume analysis (`/resume/analyze`)
- Keyword extraction (`/resume/keywords`)
- Tailoring for job descriptions (`/resume/tailor`)
- Summary generation (`/resume/summary`)
- Cover letter writing (`/resume/cover-letter`)
- ATS scoring (`/resume/ats-score`)

Each endpoint communicates with the :class:`services.llm_operator.LLMOperator`
and enforces structured output validation through
:mod:`schemas.resume_schemas`.
"""



llm = LLMOperator()

# Prebuild structured-output chains for all endpoints
analyze_chain = llm.create_chain(SYSTEM_ANALYZE, AnalyzeResponse)
keywords_chain = llm.create_chain(SYSTEM_KEYWORDS, KeywordsResponse)
tailor_chain = llm.create_chain(SYSTEM_TAILOR, TailorResponse)
summary_chain = llm.create_chain(SYSTEM_SUMMARY, SummaryResponse)
cover_chain = llm.create_chain(SYSTEM_COVER_LETTER, CoverLetterResponse)
ats_chain = llm.create_chain(SYSTEM_ATS, ATSScoreResponse)


# ----------------------------------------------------------------------
# Endpoints
# ----------------------------------------------------------------------

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest):
    """
    Perform an AI-driven resume quality and content analysis.

    The model evaluates the candidate’s profile and produces:
    - Quality score (0–100)
    - Strengths, gaps, and risks
    - Section-level scores
    - Keyword clusters and recommendations

    Parameters
    ----------
    req : AnalyzeRequest
        The canonical resume profile data.

    Returns
    -------
    AnalyzeResponse
        Structured analysis including scores, recommendations, and keyword insights.

    Raises
    ------
    HTTPException
        If the LLM fails to produce a valid structured response.
    """
    try:
        msg = build_analyze_user(req)
        raw = await analyze_chain.ainvoke({"user": msg})
        data = raw if isinstance(raw, dict) else getattr(raw, "content", raw)
        return AnalyzeResponse.model_validate(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"analyze failed: {e}")


@router.post("/keywords", response_model=KeywordsResponse)
async def keywords(req: JDRequest):
    """
    Extract skills, keywords, and seniority indicators from a job description.

    Parameters
    ----------
    req : JDRequest
        The job description text.

    Returns
    -------
    KeywordsResponse
        Parsed keyword clusters and inferred seniority information.
    """
    try:
        msg = build_keywords_user(req)
        return await keywords_chain.ainvoke({"user": msg})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"keywords failed: {e}")


@router.post("/tailor", response_model=TailorResponse)
async def tailor(req: TailorRequest):
    """
    Generate tailored resume bullet points aligned with a target job description.

    Parameters
    ----------
    req : TailorRequest
        The canonical profile, target JD, and tone preference.

    Returns
    -------
    TailorResponse
        Tailored bullet suggestions, keywords to emphasize, and items to de-emphasize.
    """
    try:
        msg = build_tailor_user(req)
        return await tailor_chain.ainvoke({"user": msg})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"tailor failed: {e}")


@router.post("/summary", response_model=SummaryResponse)
async def summary(req: SummaryRequest):
    """
    Generate a concise, 2–3 line professional summary.

    Parameters
    ----------
    req : SummaryRequest
        The canonical profile and optional target job description.

    Returns
    -------
    SummaryResponse
        A validated short summary string optimized for resumes.
    """
    try:
        msg = build_summary_user(req)
        return await summary_chain.ainvoke({"user": msg})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"summary failed: {e}")


@router.post("/cover-letter", response_model=CoverLetterResponse)
async def cover_letter(req: CoverLetterRequest):
    """
    Generate a short, tailored cover letter (≤180 words).

    Parameters
    ----------
    req : CoverLetterRequest
        The canonical profile, job description, and optional company/role.

    Returns
    -------
    CoverLetterResponse
        A concise and specific cover letter text.
    """
    try:
        msg = build_cover_letter_user(req)
        return await cover_chain.ainvoke({"user": msg})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"cover-letter failed: {e}")


@router.post("/ats-score", response_model=ATSScoreResponse)
async def ats_score(req: ATSScoreRequest):
    """
    Compute an ATS (Applicant Tracking System) compatibility score.

    The model compares resume content against a job description to evaluate:
    - Match score (0–100)
    - Keyword coverage
    - Missing elements
    - Actionable recommendations

    Parameters
    ----------
    req : ATSScoreRequest
        Raw resume text or canonical profile, and the target job description.

    Returns
    -------
    ATSScoreResponse
        Structured ATS evaluation with keyword match metrics and recommendations.
    """
    try:
        msg = build_ats_user(req)
        return await ats_chain.ainvoke({"user": msg})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ats-score failed: {e}")
