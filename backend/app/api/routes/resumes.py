from fastapi import APIRouter, File, HTTPException, UploadFile, status
from sqlalchemy import func, select

from app.api.deps import CurrentUser, DbSession
from app.models.resume import Resume
from app.schemas.analysis import (
    QualityCheckItem,
    QualityComponentItem,
    QualityScoreResponse,
)
from app.schemas.resume import ExtractedSkill, ResumeDetail, ResumeSkills, ResumeSummary
from app.services.analysis.quality_score import score_resume
from app.services.nlp.skill_extractor import extract_skills
from app.services.resume.pdf_extractor import MAX_FILE_BYTES, PdfError, extract_text

router = APIRouter(prefix="/resumes", tags=["resumes"])


def _get_owned(db: DbSession, resume_id: int, user: CurrentUser) -> Resume:
    """Fetch a resume, or 404 if it isn't this user's.

    user_id is part of the query, not a separate check afterwards — that's what
    makes it impossible to forget. Returning 404 rather than 403 also avoids
    confirming that someone else's resume exists.
    """
    resume = db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == user.id)
    ).scalar_one_or_none()
    if resume is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Resume not found")
    return resume


@router.post("/upload", response_model=ResumeDetail, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    db: DbSession, user: CurrentUser, file: UploadFile = File(...)
) -> Resume:
    data = await file.read()
    if len(data) > MAX_FILE_BYTES:
        raise HTTPException(status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, "File is too large")

    try:
        text, page_count = extract_text(data, file.filename or "resume.pdf")
    except PdfError as exc:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(exc)) from None

    # Version numbers are per user: v1, v2, v3... so the UI can label uploads
    # without asking the user to name them.
    previous = db.execute(
        select(func.count()).select_from(Resume).where(Resume.user_id == user.id)
    ).scalar_one()

    resume = Resume(
        user_id=user.id,
        version=previous + 1,
        filename=(file.filename or "resume.pdf")[:255],
        extracted_text=text,
        page_count=page_count,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


@router.get("", response_model=list[ResumeSummary])
def list_resumes(db: DbSession, user: CurrentUser) -> list[Resume]:
    return list(
        db.execute(
            select(Resume).where(Resume.user_id == user.id).order_by(Resume.created_at.desc())
        ).scalars()
    )


@router.get("/{resume_id}", response_model=ResumeDetail)
def get_resume(resume_id: int, db: DbSession, user: CurrentUser) -> Resume:
    return _get_owned(db, resume_id, user)


@router.get("/{resume_id}/skills", response_model=ResumeSkills)
def get_resume_skills(resume_id: int, db: DbSession, user: CurrentUser) -> ResumeSkills:
    resume = _get_owned(db, resume_id, user)
    found = extract_skills(resume.extracted_text)
    return ResumeSkills(
        resume_id=resume.id,
        filename=resume.filename,
        skills=[ExtractedSkill(name=s.name, category=s.category) for s in found],
        total=len(found),
    )


@router.get("/{resume_id}/quality", response_model=QualityScoreResponse)
def get_resume_quality(resume_id: int, db: DbSession, user: CurrentUser) -> QualityScoreResponse:
    """How strong this resume is on its own, with no job description involved."""
    resume = _get_owned(db, resume_id, user)
    quality = score_resume(resume.extracted_text)

    return QualityScoreResponse(
        resume_id=resume.id,
        filename=resume.filename,
        overall=quality.overall,
        components=[
            QualityComponentItem(
                key=c.key,
                label=c.label,
                score=c.score,
                checks=[
                    QualityCheckItem(
                        label=k.label, earned=k.earned, maximum=k.maximum, detail=k.detail
                    )
                    for k in c.checks
                ],
            )
            for c in quality.components
        ],
        weights=quality.weights,
    )


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(resume_id: int, db: DbSession, user: CurrentUser) -> None:
    db.delete(_get_owned(db, resume_id, user))
    db.commit()
