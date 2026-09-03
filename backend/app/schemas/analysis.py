from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AnalyseRequest(BaseModel):
    resume_id: int
    job_title: str = Field(default="", max_length=200)
    company: str = Field(default="", max_length=160)
    job_description: str = Field(min_length=50, max_length=20_000)


class SkillItem(BaseModel):
    name: str
    category: str


class KeywordItem(BaseModel):
    term: str
    found: bool


class QualityCheckItem(BaseModel):
    label: str
    earned: float
    maximum: float
    detail: str


class QualityComponentItem(BaseModel):
    key: str
    label: str
    score: float
    checks: list[QualityCheckItem]


class QualityScoreResponse(BaseModel):
    resume_id: int
    filename: str
    overall: float
    components: list[QualityComponentItem]
    weights: dict[str, float]


class PartialSkillItem(BaseModel):
    """A required skill backed by related experience rather than named directly."""

    name: str
    category: str
    evidence: list[str]
    shared_tags: list[str]


class JobRequirementsItem(BaseModel):
    role: str
    required_skills: list[SkillItem]
    preferred_skills: list[SkillItem]
    soft_skills: list[str]
    education: str
    experience: str
    min_years: int | None
    confidence: dict[str, bool] = Field(
        description="Which fields were found in the text rather than left blank"
    )


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
    resume_quality_score: float | None = None
    created_at: datetime


class AnalysisDetail(AnalysisSummary):
    resume_id: int | None
    job_description_id: int | None

    text_similarity: float
    semantic_similarity: float | None = Field(
        default=None,
        description="Local sentence-embedding similarity. null when the optional "
        "model is not installed. Reported for comparison; not part of match_score.",
    )
    skill_match: float | None = Field(
        default=None, description="null when the job description names no skills we recognise"
    )
    keyword_match: float
    weights: dict[str, float]

    resume_quality_score: float | None = None
    quality_breakdown: list[QualityComponentItem] = Field(default_factory=list)

    matched_skills: list[SkillItem]
    partial_skills: list[PartialSkillItem]
    missing_skills: list[SkillItem]
    extra_skills: list[SkillItem]
    keywords: list[KeywordItem]
    sections: dict[str, bool]
    recommendations: list[RecommendationItem]
    requirements: JobRequirementsItem | None = None


class JobSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    company: str = ""
    role: str = ""
    created_at: datetime


class JobDetail(JobSummary):
    description: str
    company: str
    role: str
    parsed: dict = Field(default_factory=dict)
