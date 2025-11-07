"""
Resume Schemas
==============

This module defines the Pydantic data models used for resume analysis,
keyword extraction, tailoring, and ATS scoring.

Each schema represents either a request or a response model for the
`/resume` API routes, ensuring type safety and well-documented payloads
for both developers and clients.

These models are used in conjunction with the
:class:`services.llm_operator.LLMOperator` class.
"""

from pydantic import BaseModel, Field, ConfigDict, model_validator
from typing import List, Optional, Dict


# ----------------------------------------------------------------------
# Base Resume Data Structures
# ----------------------------------------------------------------------
class ExperienceItem(BaseModel):
    """
    Representation of a single work experience entry.

    Attributes
    ----------
    company : str
        Name of the company or organization.
    role : str
        Job title or position held.
    start : Optional[str]
        Start date or year of the role.
    end : Optional[str]
        End date or year of the role.
    bullets : List[str]
        Key achievements or responsibilities in bullet form.
    """

    company: str = Field(..., description="Name of the company or organization.")
    role: str = Field(..., description="Job title or position held.")
    start: Optional[str] = Field(None, description="Start date or year of the role.")
    end: Optional[str] = Field(None, description="End date or year of the role.")
    bullets: List[str] = Field(default_factory=list, description="Key bullets.")


class EducationItem(BaseModel):
    """
    Representation of a single education entry.

    Attributes
    ----------
    school : str
        Name of the educational institution.
    degree : Optional[str]
        Degree obtained or pursued.
    year : Optional[str]
        Year of graduation or attendance.
    """

    school: str = Field(..., description="Name of the school or institution.")
    degree: Optional[str] = Field(None, description="Degree obtained or pursued.")
    year: Optional[str] = Field(None, description="Year of graduation or attendance.")


class CanonicalProfile(BaseModel):
    """
    Canonical structured resume representation.

    This model standardizes parsed resume data into a consistent format
    for use across AI tasks such as tailoring, summary generation,
    and ATS scoring.

    Attributes
    ----------
    name : Optional[str]
        Candidate's full name.
    title : Optional[str]
        Professional or role title.
    summary : Optional[str]
        Short profile summary or professional overview.
    skills : List[str]
        List of core skills or competencies.
    experience : List[ExperienceItem]
        List of work experience items.
    education : List[EducationItem]
        List of educational qualifications.
    """

    name: Optional[str] = Field(None, description="Candidate's name.")
    title: Optional[str] = Field(None, description="Professional or role title.")
    summary: Optional[str] = Field(None, description="Brief professional summary.")
    skills: List[str] = Field(default_factory=list, description="List of skills or competencies.")
    experience: List[ExperienceItem] = Field(default_factory=list, description="List of experience items.")
    education: List[EducationItem] = Field(default_factory=list, description="List of education items.")


# ----------------------------------------------------------------------
# Analyze Profile
# ----------------------------------------------------------------------
class AnalyzeRequest(BaseModel):
    """
    Request model for analyzing and canonicalizing a resume profile.

    Attributes
    ----------
    profile : str | dict
        Raw resume text or structured JSON profile.
    """

    model_config = ConfigDict(extra="forbid")
    canonical: CanonicalProfile


class AnalyzeResponse(BaseModel):
    """
    Response model containing the standardized resume representation.

    Attributes
    ----------
    canonical : CanonicalProfile
        Canonicalized profile structure derived from the input.
    """
    model_config = ConfigDict(extra="allow")

    quality: int = Field(0, ge=0, le=100, description="Overall resume quality score (0–100).")
    strengths: List[str] = Field(default_factory=list, description="What is working well.")
    gaps: List[str] = Field(default_factory=list, description="Missing skills/sections/content.")
    risks: List[str] = Field(default_factory=list, description="Potential red flags (date gaps, job-hopping, etc.).")
    recommendations: List[str] = Field(default_factory=list, description="Concrete, actionable improvements.")
    section_scores: Dict[str, int] = Field(
        default_factory=dict,
        description="Per-section scores 0–5, e.g. {'summary':4,'experience':3,'education':5,'skills':4}",
    )
    keyword_clusters: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Clustered keywords, e.g. {'core':[],'tools':[],'soft':[]}",
    )
    anomalies: List[str] = Field(default_factory=list, description="Parsing/timeline anomalies to check.")


# ----------------------------------------------------------------------
# Job Description and Keyword Extraction
# ----------------------------------------------------------------------
class JDRequest(BaseModel):
    """
    Request model for keyword extraction from a job description.

    Attributes
    ----------
    job_description : str
        The raw job description text.
    """
    model_config = ConfigDict(extra="forbid")
    job_description: str = Field(..., description="Text of the job description.")


class KeywordsResponse(BaseModel):
    """
    Response model containing extracted job-relevant keywords.

    Attributes
    ----------
    skills : List[str]
        Extracted hard or technical skills.
    keywords : List[str]
        General keywords from the job posting.
    seniority : Optional[str]
        Seniority level inferred from the job description.
    nice_to_have : List[str]
        Optional or secondary skills mentioned in the posting.
    """

    model_config = ConfigDict(extra="allow")

    skills: List[str] = Field(default_factory=list, description="List of core technical skills.")
    keywords: List[str] = Field(default_factory=list, description="List of general keywords extracted.")
    seniority: Optional[str] = Field(None, description="Seniority level inferred from the description.")
    nice_to_have: List[str] = Field(default_factory=list, description="Optional or nice-to-have skills.")


# ----------------------------------------------------------------------
# Tailoring and Summary
# ----------------------------------------------------------------------
class TailorRequest(BaseModel):
    """
    Request model for tailoring resume bullet points.

    Attributes
    ----------
    profile : CanonicalProfile | dict
        User's canonical or raw profile data.
    job_description : str
        Target job description for tailoring.
    tone : Optional[str]
        Desired tone for suggestions (default: 'concise').
    """

    model_config = ConfigDict(extra="forbid")

    profile: CanonicalProfile = Field(..., description="Canonical profile data.")
    job_description: str = Field(..., description="Target job description text.")
    tone: Optional[str] = Field("concise", description="Desired tone for tailored suggestions.")


class TailorResponse(BaseModel):
    """
    Response model containing tailored bullet points and focus areas.

    Attributes
    ----------
    bullets : List[str]
        Tailored bullet points aligned with the job description.
    removed : List[str]
        Bullets that were removed or de-emphasized.
    focus : List[str]
        Key focus areas recommended for improvement.
    """

    model_config = ConfigDict(extra="allow")

    bullets: List[str] = Field(default_factory=list, description="Tailored bullet points.")
    removed: List[str] = Field(default_factory=list, description="Removed or less relevant bullets.")
    focus: List[str] = Field(default_factory=list, description="Suggested focus areas.")


class SummaryRequest(BaseModel):
    """
    Request model for generating a professional summary.

    Attributes
    ----------
    profile : CanonicalProfile | dict
        User's profile or canonical resume data.
    job_description : Optional[str]
        Target job description for contextualization.
    """

    model_config = ConfigDict(extra="forbid")

    profile: CanonicalProfile = Field(..., description="Canonical profile data.")
    job_description: Optional[str] = Field(None, description="Optional target job description.")


class SummaryResponse(BaseModel):
    """
    Response model containing a generated professional summary.

    Attributes
    ----------
    summary : str
        The AI-generated resume summary text.
    """

    model_config = ConfigDict(extra="allow")

    summary: str = Field("", description="Generated professional summary.")


# ----------------------------------------------------------------------
# Cover Letter Generation
# ----------------------------------------------------------------------
class CoverLetterRequest(BaseModel):
    """
    Request model for generating a tailored cover letter.

    Attributes
    ----------
    profile : CanonicalProfile | dict
        Canonicalized or raw resume profile data.
    job_description : str
        Job description to tailor the letter for.
    company : Optional[str]
        Target company name.
    role : Optional[str]
        Target role or job title.
    """

    model_config = ConfigDict(extra="forbid")

    profile: CanonicalProfile = Field(..., description="Canonical profile data.")
    job_description: str = Field(..., description="Job description text.")
    company: Optional[str] = Field(None, description="Target company name.")
    role: Optional[str] = Field(None, description="Target role or title.")


class CoverLetterResponse(BaseModel):
    """
    Response model containing the generated cover letter text.

    Attributes
    ----------
    cover_letter : str
        The AI-generated cover letter text.
    """

    model_config = ConfigDict(extra="allow")

    cover_letter: str = Field("", description="Generated cover letter text.")

# ----------------------------------------------------------------------
# ATS Scoring
# ----------------------------------------------------------------------
class ATSScoreRequest(BaseModel):
    """
    Request model for ATS (Applicant Tracking System) scoring.

    Attributes
    ----------
    resume_text : str
        The raw resume text to evaluate.
    job_description : str
        Target job description for comparison.
    """
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
    Response model for ATS scoring results.

    Attributes
    ----------
    score : int
        Computed ATS compatibility score (0–100).
    gaps : List[str]
        Missing or weak areas detected in the resume.
    recommendations : List[str]
        Suggestions to improve the score.
    keyword_match : Dict[str, List[str]]
        Mapping of matched and unmatched keywords by category.
    """

    model_config = ConfigDict(extra="allow")

    score: int = Field(0, description="ATS score between 0 and 100.")
    gaps: List[str] = Field(default_factory=list, description="Missing or weak skills/sections.")
    recommendations: List[str] = Field(default_factory=list, description="Improvement recommendations.")
    keyword_match: Dict[str, List[str]] = Field(default_factory=dict, description="Matched/unmatched keyword mapping.")
