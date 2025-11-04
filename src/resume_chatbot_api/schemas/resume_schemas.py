from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class ExperienceItem(BaseModel):
    company: str
    role: str
    start: Optional[str] = None
    end: Optional[str] = None
    bullets: List[str] = []

class EducationItem(BaseModel):
    school: str
    degree: Optional[str] = None
    year: Optional[str] = None

class CanonicalProfile(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    summary: Optional[str] = None
    skills: List[str] = []
    experience: List[ExperienceItem] = []
    education: List[EducationItem] = []

class AnalyzeRequest(BaseModel):
    profile: str | Dict[str, Any]

class AnalyzeResponse(BaseModel):
    canonical: CanonicalProfile

class JDRequest(BaseModel):
    job_description: str

class KeywordsResponse(BaseModel):
    skills: List[str]
    keywords: List[str]
    seniority: Optional[str] = None
    nice_to_have: List[str] = []

class TailorRequest(BaseModel):
    profile: CanonicalProfile | Dict[str, Any]
    job_description: str
    tone: Optional[str] = "concise"

class TailorResponse(BaseModel):
    bullets: List[str]
    removed: List[str] = []
    focus: List[str] = []

class SummaryRequest(BaseModel):
    profile: CanonicalProfile | Dict[str, Any]
    job_description: Optional[str] = None

class SummaryResponse(BaseModel):
    summary: str

class CoverLetterRequest(BaseModel):
    profile: CanonicalProfile | Dict[str, Any]
    job_description: str
    company: Optional[str] = None
    role: Optional[str] = None

class CoverLetterResponse(BaseModel):
    cover_letter: str

class ATSScoreRequest(BaseModel):
    resume_text: str
    job_description: str

class ATSScoreResponse(BaseModel):
    score: int
    gaps: List[str]
    recommendations: List[str]
    keyword_match: Dict[str, List[str]]
