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

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


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
    bullets: List[str] = Field(
        default_factory=list,
        description="List of key responsibilities or achievements.",
    )


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
    skills: List[str] = Field(
        default_factory=list, description="List of skills or competencies."
    )
    experience: List[ExperienceItem] = Field(
        default_factory=list, description="List of experience items."
    )
    education: List[EducationItem] = Field(
        default_factory=list, description="List of education items."
    )


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

    profile: str | Dict[str, Any] = Field(
        ..., description="Raw text or structured JSON resume data."
    )


class AnalyzeResponse(BaseModel):
    """
    Response model containing the standardized resume representation.

    Attributes
    ----------
    canonical : CanonicalProfile
        Canonicalized profile structure derived from the input.
    """

    canonical: CanonicalProfile = Field(
        ..., description="Canonicalized resume profile."
    )


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

    skills: List[str] = Field(..., description="List of core technical skills.")
    keywords: List[str] = Field(..., description="List of general keywords extracted.")
    seniority: Optional[str] = Field(
        None, description="Seniority level inferred from the description."
    )
    nice_to_have: List[str] = Field(
        default_factory=list, description="List of optional or nice-to-have skills."
    )


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

    profile: CanonicalProfile | Dict[str, Any] = Field(
        ..., description="Canonical or raw profile data."
    )
    job_description: str = Field(..., description="Target job description text.")
    tone: Optional[str] = Field(
        "concise", description="Desired tone for tailored suggestions."
    )


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

    bullets: List[str] = Field(..., description="Tailored bullet points.")
    removed: List[str] = Field(
        default_factory=list, description="Removed or less relevant bullets."
    )
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

    profile: CanonicalProfile | Dict[str, Any] = Field(
        ..., description="Canonical or raw profile data."
    )
    job_description: Optional[str] = Field(
        None, description="Optional target job description."
    )


class SummaryResponse(BaseModel):
    """
    Response model containing a generated professional summary.

    Attributes
    ----------
    summary : str
        The AI-generated resume summary text.
    """

    summary: str = Field(..., description="Generated professional summary.")


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

    profile: CanonicalProfile | Dict[str, Any] = Field(
        ..., description="Profile data (canonical or raw)."
    )
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

    cover_letter: str = Field(..., description="Generated cover letter text.")


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

    resume_text: str = Field(..., description="Raw resume text.")
    job_description: str = Field(..., description="Target job description text.")


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

    score: int = Field(..., description="ATS score between 0 and 100.")
    gaps: List[str] = Field(..., description="List of missing or weak skills/sections.")
    recommendations: List[str] = Field(..., description="Improvement recommendations.")
    keyword_match: Dict[str, List[str]] = Field(
        ..., description="Matched/unmatched keyword mapping."
    )
