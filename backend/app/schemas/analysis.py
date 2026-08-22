from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AnalyseRequest(BaseModel):
    resume_id: int
    job_title: str = Field(default="", max_length=200)
    job_description: str = Field(min_length=50, max_length=20_000)


class SkillItem(BaseModel):
    name: str
    category: str


class KeywordItem(BaseModel):
    term: str
    found: bool


class RecommendationItem(BaseModel):
    category: str
    message: str


class AnalysisSummary(BaseModel):
    """History list view — no JSON blobs, so the list stays light."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    job_title: str
    resume_filename: str
    match_score: float
    created_at: datetime


class AnalysisDetail(AnalysisSummary):
    resume_id: int | None
    job_description_id: int | None

    text_similarity: float
    skill_match: float | None = Field(
        default=None, description="null when the job description names no skills we recognise"
    )
    keyword_match: float
    weights: dict[str, float]

    matched_skills: list[SkillItem]
    missing_skills: list[SkillItem]
    extra_skills: list[SkillItem]
    keywords: list[KeywordItem]
    sections: dict[str, bool]
    recommendations: list[RecommendationItem]


class JobSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    created_at: datetime


class JobDetail(JobSummary):
    description: str
