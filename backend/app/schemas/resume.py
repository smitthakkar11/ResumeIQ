from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ResumeSummary(BaseModel):
    """List view — no text, so the history page stays light."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    page_count: int
    created_at: datetime


class ResumeDetail(ResumeSummary):
    extracted_text: str


class ExtractedSkill(BaseModel):
    name: str
    category: str


class ResumeSkills(BaseModel):
    resume_id: int
    filename: str
    skills: list[ExtractedSkill]
    total: int
