from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.models.resume import Resume
from app.schemas.analysis import AnalyseRequest, AnalysisResponse, KeywordItem, SkillItem
from app.services.matching.engine import analyse

router = APIRouter(prefix="/analyses", tags=["analyses"])


@router.post("", response_model=AnalysisResponse)
def create_analysis(
    payload: AnalyseRequest, db: DbSession, user: CurrentUser
) -> AnalysisResponse:
    """Score a resume against a job description.

    Phase 5 computes and returns; Phase 7 will also persist the result.
    """
    resume = db.execute(
        select(Resume).where(Resume.id == payload.resume_id, Resume.user_id == user.id)
    ).scalar_one_or_none()
    if resume is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Resume not found")

    result = analyse(resume.extracted_text, payload.job_description)

    to_items = lambda skills: [SkillItem(name=s.name, category=s.category) for s in skills]  # noqa: E731

    return AnalysisResponse(
        resume_id=resume.id,
        resume_filename=resume.filename,
        job_title=payload.job_title.strip(),
        overall_score=result.overall_score,
        text_similarity=result.text_similarity,
        skill_match=result.skill_match,
        keyword_match=result.keyword_match,
        weights=result.weights,
        matched_skills=to_items(result.matched_skills),
        missing_skills=to_items(result.missing_skills),
        extra_skills=to_items(result.extra_skills),
        keywords=[KeywordItem(term=k.term, found=k.found) for k in result.keywords],
    )
