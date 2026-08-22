from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.models.job_description import JobDescription
from app.schemas.analysis import JobDetail, JobSummary

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model=list[JobSummary])
def list_jobs(db: DbSession, user: CurrentUser) -> list[JobDescription]:
    return list(
        db.execute(
            select(JobDescription)
            .where(JobDescription.user_id == user.id)
            .order_by(JobDescription.created_at.desc())
        ).scalars()
    )


@router.get("/{job_id}", response_model=JobDetail)
def get_job(job_id: int, db: DbSession, user: CurrentUser) -> JobDescription:
    job = db.execute(
        select(JobDescription).where(
            JobDescription.id == job_id, JobDescription.user_id == user.id
        )
    ).scalar_one_or_none()
    if job is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Job description not found")
    return job
