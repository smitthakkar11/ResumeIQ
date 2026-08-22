from pydantic import BaseModel, Field


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


class AnalysisResponse(BaseModel):
    resume_id: int
    resume_filename: str
    job_title: str

    overall_score: float
    text_similarity: float
    skill_match: float | None = Field(
        description="null when the job description names no skills we recognise"
    )
    keyword_match: float
    weights: dict[str, float]

    matched_skills: list[SkillItem]
    missing_skills: list[SkillItem]
    extra_skills: list[SkillItem]
    keywords: list[KeywordItem]
