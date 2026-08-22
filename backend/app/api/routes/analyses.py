import hashlib

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.models.analysis import Analysis
from app.models.job_description import JobDescription
from app.models.resume import Resume
from app.schemas.analysis import AnalyseRequest, AnalysisDetail, AnalysisSummary
from app.services.matching.engine import analyse

router = APIRouter(prefix="/analyses", tags=["analyses"])


def _owned_analysis(db: DbSession, analysis_id: int, user: CurrentUser) -> Analysis:
    """404 rather than 403 for someone else's analysis — a 403 would confirm it exists."""
    row = db.execute(
        select(Analysis).where(Analysis.id == analysis_id, Analysis.user_id == user.id)
    ).scalar_one_or_none()
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Analysis not found")
    return row


def _get_or_create_job(db: DbSession, user_id: int, title: str, description: str) -> JobDescription:
    """Reuse an identical posting rather than storing it once per analysis."""
    digest = hashlib.sha256(description.strip().encode("utf-8")).hexdigest()

    existing = db.execute(
        select(JobDescription).where(
            JobDescription.user_id == user_id, JobDescription.content_hash == digest
        )
    ).scalar_one_or_none()
    if existing is not None:
        return existing

    job = JobDescription(
        user_id=user_id, title=title, description=description, content_hash=digest
    )
    db.add(job)
    db.flush()  # assign job.id without committing yet
    return job


@router.post("", response_model=AnalysisDetail, status_code=status.HTTP_201_CREATED)
def create_analysis(payload: AnalyseRequest, db: DbSession, user: CurrentUser) -> Analysis:
    resume = db.execute(
        select(Resume).where(Resume.id == payload.resume_id, Resume.user_id == user.id)
    ).scalar_one_or_none()
    if resume is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Resume not found")

    result = analyse(resume.extracted_text, payload.job_description)
    job = _get_or_create_job(db, user.id, payload.job_title.strip(), payload.job_description)

    as_dicts = lambda skills: [{"name": s.name, "category": s.category} for s in skills]  # noqa: E731

    analysis = Analysis(
        user_id=user.id,
        resume_id=resume.id,
        job_description_id=job.id,
        # Denormalised so history stays readable if the resume is later deleted.
        resume_filename=resume.filename,
        job_title=payload.job_title.strip(),
        match_score=result.overall_score,
        text_similarity=result.text_similarity,
        semantic_similarity=result.semantic_similarity,
        skill_match=result.skill_match,
        keyword_match=result.keyword_match,
        weights=result.weights,
        matched_skills=as_dicts(result.matched_skills),
        missing_skills=as_dicts(result.missing_skills),
        extra_skills=as_dicts(result.extra_skills),
        keywords=[{"term": k.term, "found": k.found} for k in result.keywords],
        sections=result.sections,
        recommendations=[{"category": r.category, "message": r.message} for r in result.recommendations],
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis


@router.get("", response_model=list[AnalysisSummary])
def list_analyses(db: DbSession, user: CurrentUser) -> list[Analysis]:
    """Newest first. Served by the (user_id, created_at) composite index."""
    return list(
        db.execute(
            select(Analysis)
            .where(Analysis.user_id == user.id)
            .order_by(Analysis.created_at.desc(), Analysis.id.desc())
        ).scalars()
    )


@router.get("/{analysis_id}", response_model=AnalysisDetail)
def get_analysis(analysis_id: int, db: DbSession, user: CurrentUser) -> Analysis:
    return _owned_analysis(db, analysis_id, user)


@router.delete("/{analysis_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_analysis(analysis_id: int, db: DbSession, user: CurrentUser) -> None:
    db.delete(_owned_analysis(db, analysis_id, user))
    db.commit()
