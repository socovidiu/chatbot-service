"""
Resume Schemas
==============

Pydantic models with rule-based validation:
- Counts (e.g., 3–5, >=2)
- Ranges (0–5, 0–100)
- Required dict keys (e.g., keyword clusters: core/tools/soft)
- Length limits (summary, cover letter)
- Shape checks for nested dicts (section_scores, keyword_match)

These models pair cleanly with LangChain's `with_structured_output(...)`.
"""

from __future__ import annotations
from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    model_validator,
    field_validator,
    conint,
)
from typing import List, Optional, Dict, Annotated

# aliases to avoid pylance warnings
Score100 = Annotated[int, Field(ge=0, le=100)]
Score5   = Annotated[int, Field(ge=0, le=5)]

# ----------------------------- Helpers -----------------------------

def _dedup(seq: List[str]) -> List[str]:
    seen = set()
    out = []
    for x in seq:
        k = x.strip()
        if k and k not in seen:
            out.append(k)
            seen.add(k)
    return out

def _require_keys(d: Dict, keys: List[str], name: str):
    for k in keys:
        if k not in d:
            raise ValueError(f"{name}.{k} is required")
        if not isinstance(d[k], list):
            raise ValueError(f"{name}.{k} must be a list")

def _between_len(v: List[str], lo: int, hi: int, label: str) -> List[str]:
    if not (lo <= len(v) <= hi):
        raise ValueError(f"{label} must contain {lo}–{hi} items")
    return v

def _min_len(v: List[str], lo: int, label: str) -> List[str]:
    if len(v) < lo:
        raise ValueError(f"{label} must contain at least {lo} items")
    return v


# --------------------- Base Resume Data Structures ---------------------

class ExperienceItem(BaseModel):
    company: str = Field(..., description="Name of the company or organization.")
    role: str = Field(..., description="Job title or position held.")
    start: Optional[str] = Field(None, description="Start date or year of the role.")
    end: Optional[str] = Field(None, description="End date or year of the role.")
    bullets: List[str] = Field(default_factory=list, description="Key bullets.")

    @field_validator("bullets")
    @classmethod
    def _dedup_bullets(cls, v: List[str]) -> List[str]:
        return _dedup(v)


class EducationItem(BaseModel):
    school: str = Field(..., description="Name of the school or institution.")
    degree: Optional[str] = Field(None, description="Degree obtained or pursued.")
    year: Optional[str] = Field(None, description="Year of graduation or attendance.")


class CanonicalProfile(BaseModel):
    name: Optional[str] = Field(None, description="Candidate's name.")
    title: Optional[str] = Field(None, description="Professional or role title.")
    summary: Optional[str] = Field(None, description="Brief professional summary.")
    skills: List[str] = Field(default_factory=list, description="List of skills or competencies.")
    experience: List[ExperienceItem] = Field(default_factory=list, description="List of experience items.")
    education: List[EducationItem] = Field(default_factory=list, description="List of education items.")

    @field_validator("skills")
    @classmethod
    def _dedup_skills(cls, v: List[str]) -> List[str]:
        return _dedup(v)


# ----------------------------- Analyze -----------------------------

class AnalyzeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    resumedata: CanonicalProfile


class SectionScores(BaseModel):
    summary: Score5 
    experience: Score5 
    education: Score5 
    skills: Score5 


class AnalyzeResponse(BaseModel):
    """
    Rules encoded:
    - quality: 0–100 (start 50; +25 strong exp; +15 quantified impact; +10 breadth; subtract for missing sections)
    - strengths: ≥2 items
    - gaps: ≥2 items
    - risks: can be empty; otherwise concrete timeline issues
    - recommendations: 3–5 items
    - section_scores: ints 0–5 for summary/experience/education/skills
    - keyword_clusters: dict with core/tools/soft (lists)
    - anomalies: list
    """
    model_config = ConfigDict(extra="allow")

    quality: Score100 = Field(..., description="Overall resume quality (0–100).")
    strengths: List[str] = Field(default_factory=list, description="Concrete strengths (≥2).")
    gaps: List[str] = Field(default_factory=list, description="Concrete gaps (≥2).")
    risks: List[str] = Field(default_factory=list, description="Timeline risks (can be []).")
    recommendations: List[str] = Field(default_factory=list, description="3–5 actionable next steps.")
    section_scores: SectionScores = Field(..., description="Per-section scores 0–5.")
    keyword_clusters: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="{'core':[], 'tools':[], 'soft':[]}",
    )
    anomalies: List[str] = Field(default_factory=list, description="Inconsistencies, overlaps, etc.")

    # list constraints & dedupe
    @field_validator("strengths", "gaps", "risks", "recommendations", "anomalies")
    @classmethod
    def _dedup_lists(cls, v: List[str]) -> List[str]:
        return _dedup(v)

    @field_validator("strengths")
    @classmethod
    def _min_strengths(cls, v: List[str]) -> List[str]:
        return _min_len(v, 2, "strengths")

    @field_validator("gaps")
    @classmethod
    def _min_gaps(cls, v: List[str]) -> List[str]:
        return _min_len(v, 2, "gaps")

    @field_validator("recommendations")
    @classmethod
    def _recs_3_5(cls, v: List[str]) -> List[str]:
        return _between_len(v, 3, 5, "recommendations")

    @field_validator("keyword_clusters")
    @classmethod
    def _clusters_shape(cls, v: Dict[str, List[str]]) -> Dict[str, List[str]]:
        _require_keys(v, ["core", "tools", "soft"], "keyword_clusters")
        v["core"] = _dedup(v["core"])
        v["tools"] = _dedup(v["tools"])
        v["soft"] = _dedup(v["soft"])
        return v


# ----------------------------- Keywords -----------------------------

class JDRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    job_description: str = Field(..., description="Text of the job description.")


class KeywordsResponse(BaseModel):
    model_config = ConfigDict(extra="allow")

    skills: List[str] = Field(default_factory=list, description="List of core technical skills.")
    keywords: List[str] = Field(default_factory=list, description="General keywords extracted.")
    seniority: Optional[str] = Field(None, description="Inferred seniority (optional).")
    nice_to_have: List[str] = Field(default_factory=list, description="Optional or nice-to-have skills.")

    @field_validator("skills", "keywords", "nice_to_have")
    @classmethod
    def _dedup_lists(cls, v: List[str]) -> List[str]:
        return _dedup(v)


# ----------------------------- Tailoring -----------------------------

class TailorRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    profile: CanonicalProfile = Field(..., description="Canonical profile data.")
    job_description: str = Field(..., description="Target job description text.")
    tone: Optional[str] = Field("concise", description="Desired tone for tailored suggestions.")


class TailorResponse(BaseModel):
    """
    Rules encoded:
    - bullets: 4–6; action-oriented; scope + tech + measurable impact
    - focus: 3–5 priority keywords to emphasize
    - removed: 2–4 to de-emphasize for THIS role
    """
    model_config = ConfigDict(extra="allow")

    bullets: List[str] = Field(default_factory=list, description="Tailored bullet points (4–6).")
    removed: List[str] = Field(default_factory=list, description="Items to de-emphasize (2–4).")
    focus: List[str] = Field(default_factory=list, description="Priority keywords (3–5).")

    @field_validator("bullets", "removed", "focus")
    @classmethod
    def _dedup_lists(cls, v: List[str]) -> List[str]:
        return _dedup(v)

    @field_validator("bullets")
    @classmethod
    def _bullets_4_6(cls, v: List[str]) -> List[str]:
        return _between_len(v, 4, 6, "bullets")

    @field_validator("focus")
    @classmethod
    def _focus_3_5(cls, v: List[str]) -> List[str]:
        return _between_len(v, 3, 5, "focus")

    @field_validator("removed")
    @classmethod
    def _removed_2_4(cls, v: List[str]) -> List[str]:
        return _between_len(v, 2, 4, "removed")


# ----------------------------- Summary -----------------------------

class SummaryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    profile: CanonicalProfile = Field(..., description="Canonical profile data.")
    job_description: Optional[str] = Field(None, description="Optional target JD.")


class SummaryResponse(BaseModel):
    """
    Rules encoded:
    - 2–3 lines, concise; enforce via length limits (approx)
    """
    model_config = ConfigDict(extra="allow")
    summary: str = Field("", description="Generated professional summary.")

    @field_validator("summary")
    @classmethod
    def _non_empty_and_short(cls, v: str) -> str:
        text = v.strip()
        if not text:
            raise ValueError("summary must not be empty")
        # soft length cap ~320 chars (~2–3 lines)
        if len(text) > 320:
            raise ValueError("summary should be concise (≤ ~320 characters)")
        return text


# --------------------------- Cover Letter ---------------------------

class CoverLetterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    profile: CanonicalProfile = Field(..., description="Canonical profile data.")
    job_description: str = Field(..., description="Job description text.")
    company: Optional[str] = Field(None, description="Target company name.")
    role: Optional[str] = Field(None, description="Target role or title.")


class CoverLetterResponse(BaseModel):
    """
    Rules encoded:
    - ≤ 180 words, specific; no fluff
    """
    model_config = ConfigDict(extra="allow")
    cover_letter: str = Field("", description="Generated cover letter text.")

    @field_validator("cover_letter")
    @classmethod
    def _limit_180_words(cls, v: str) -> str:
        text = v.strip()
        if not text:
            raise ValueError("cover_letter must not be empty")
        if len(text.split()) > 180:
            raise ValueError("cover_letter must be ≤ 180 words")
        return text


# ----------------------------- ATS Score -----------------------------

class ATSScoreRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    resume_text: Optional[str] = Field(None, description="Raw resume text.")
    canonical: Optional[CanonicalProfile] = Field(None, description="Canonical profile.")
    job_description: str = Field(..., description="Target job description text.")

    @model_validator(mode="after")
    def _require_one(self):
        if not (self.resume_text or self.canonical):
            raise ValueError("Provide 'resume_text' or 'canonical'.")
        return self


class ATSScoreResponse(BaseModel):
    """
    Rules encoded:
    - score: 0–100
    - gaps: list
    - recommendations: ≥3 items (actionable)
    - keyword_match: dict with 'present' and 'missing' (lists)
    """
    model_config = ConfigDict(extra="allow")

    score: Score100 = Field(0, description="ATS score (0–100).")
    gaps: List[str] = Field(default_factory=list, description="Missing or weak skills/sections.")
    recommendations: List[str] = Field(default_factory=list, description="Actionable recommendations (≥3).")
    keyword_match: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="{'present':[], 'missing':[]}",
    )

    @field_validator("gaps", "recommendations")
    @classmethod
    def _dedup_lists(cls, v: List[str]) -> List[str]:
        return _dedup(v)

    @field_validator("recommendations")
    @classmethod
    def _recs_min3(cls, v: List[str]) -> List[str]:
        return _min_len(v, 3, "recommendations")

    @field_validator("keyword_match")
    @classmethod
    def _km_shape(cls, v: Dict[str, List[str]]) -> Dict[str, List[str]]:
        _require_keys(v, ["present", "missing"], "keyword_match")
        v["present"] = _dedup(v["present"])
        v["missing"] = _dedup(v["missing"])
        return v
