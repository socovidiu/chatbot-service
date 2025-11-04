from fastapi import APIRouter, HTTPException
from core.config import settings
from services.llm_operator import LLMOperator
from schemas.resume_schemas import (
    AnalyzeRequest, AnalyzeResponse, CanonicalProfile,
    JDRequest, KeywordsResponse,
    TailorRequest, TailorResponse,
    SummaryRequest, SummaryResponse,
    CoverLetterRequest, CoverLetterResponse,
    ATSScoreRequest, ATSScoreResponse
)

router = APIRouter(prefix="/resume", tags=["resume"])
llm = LLMOperator(settings.create_chat_llm())

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest):
    try:
        data = await llm.analyze_profile(req.profile)
        canonical = CanonicalProfile(**data)
        return AnalyzeResponse(canonical=canonical)
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/keywords", response_model=KeywordsResponse)
async def keywords(req: JDRequest):
    try:
        data = await llm.extract_keywords(req.job_description)
        return KeywordsResponse(**data)
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/tailor", response_model=TailorResponse)
async def tailor(req: TailorRequest):
    try:
        profile = req.profile if isinstance(req.profile, dict) else req.profile.model_dump()
        data = await llm.tailor_bullets(profile, req.job_description, tone=req.tone or "concise")
        return TailorResponse(**data)
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/summary", response_model=SummaryResponse)
async def summary(req: SummaryRequest):
    try:
        profile = req.profile if isinstance(req.profile, dict) else req.profile.model_dump()
        data = await llm.write_summary(profile, req.job_description)
        return SummaryResponse(**data)
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/cover-letter", response_model=CoverLetterResponse)
async def cover_letter(req: CoverLetterRequest):
    try:
        profile = req.profile if isinstance(req.profile, dict) else req.profile.model_dump()
        data = await llm.write_cover_letter(profile, req.job_description, req.company, req.role)
        return CoverLetterResponse(**data)
    except Exception as e:
        raise HTTPException(500, str(e))

@router.post("/ats-score", response_model=ATSScoreResponse)
async def ats(req: ATSScoreRequest):
    try:
        data = await llm.ats_score(req.resume_text, req.job_description)
        return ATSScoreResponse(**data)
    except Exception as e:
        raise HTTPException(500, str(e))
