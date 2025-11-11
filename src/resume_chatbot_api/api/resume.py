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
    AnalyzeRequest, AnalyzeResponse,
    JDRequest, KeywordsResponse,
    TailorRequest, TailorResponse,
    SummaryRequest, SummaryResponse,
    CoverLetterRequest, CoverLetterResponse,
    ATSScoreRequest, ATSScoreResponse,
)
from services.prompts import (
    SYSTEM_ANALYZE, SYSTEM_KEYWORDS, SYSTEM_TAILOR,
    SYSTEM_SUMMARY, SYSTEM_COVER_LETTER, SYSTEM_ATS,
    build_analyze_user, build_keywords_user, build_tailor_user,
    build_summary_user, build_cover_letter_user, build_ats_user,
)



# Define router and instantiate LLM operator
router = APIRouter(prefix="/resume", tags=["resume"])
llm = LLMOperator()

# build chains once per endpoint
analyze_chain = llm.create_chain(SYSTEM_ANALYZE, AnalyzeResponse)
keywords_chain = llm.create_chain(SYSTEM_KEYWORDS, KeywordsResponse)
tailor_chain = llm.create_chain(SYSTEM_TAILOR, TailorResponse)
summary_chain = llm.create_chain(SYSTEM_SUMMARY, SummaryResponse)
cover_chain = llm.create_chain(SYSTEM_COVER_LETTER, CoverLetterResponse)
ats_chain = llm.create_chain(SYSTEM_ATS, ATSScoreResponse)     

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest):
    try:
        msg = build_analyze_user(req)
        raw = await analyze_chain.ainvoke({"user": msg})
        # raw may be dict or LC Message; normalize then validate:
        data = raw if isinstance(raw, dict) else getattr(raw, "content", raw)
        return AnalyzeResponse.model_validate(data)  # <- enforces schema
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"analyze failed: {e}")

@router.post("/keywords", response_model=KeywordsResponse)
async def keywords(req: JDRequest):
    try:
        msg = build_keywords_user(req)
        return await keywords_chain.ainvoke({"user": msg})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"keywords failed: {e}")

@router.post("/tailor", response_model=TailorResponse)
async def tailor(req: TailorRequest):
    try:
        msg = build_tailor_user(req)
        return await tailor_chain.ainvoke({"user": msg})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"tailor failed: {e}")

@router.post("/summary", response_model=SummaryResponse)
async def summary(req: SummaryRequest):
    try:
        msg = build_summary_user(req)
        return await summary_chain.ainvoke({"user": msg})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"summary failed: {e}")

@router.post("/cover-letter", response_model=CoverLetterResponse)
async def cover_letter(req: CoverLetterRequest):
    try:
        msg = build_cover_letter_user(req)
        return await cover_chain.ainvoke({"user": msg})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"cover-letter failed: {e}")

@router.post("/ats-score", response_model=ATSScoreResponse)
async def ats_score(req: ATSScoreRequest):
    try:
        msg = build_ats_user(req)
        return await ats_chain.ainvoke({"user": msg})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ats-score failed: {e}")