"""Health-check endpoints.

Two distinct checks, because they answer different questions:
  * /health     — "is the Python process alive?"  (liveness)
  * /health/db  — "can it actually reach MySQL?"  (readiness)

A load balancer wants the first; an engineer debugging a broken deploy wants
the second.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import settings
from app.schemas.common import DatabaseHealthResponse, HealthResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        app=settings.APP_NAME,
        environment=settings.ENVIRONMENT,
    )


@router.get("/db", response_model=DatabaseHealthResponse)
def health_db(db: Session = Depends(get_db)) -> DatabaseHealthResponse:
    """Run the cheapest possible query that proves the round trip works.

    Returns 200 with status="error" rather than raising, so the frontend can
    render a useful "database unreachable" state instead of a generic failure.
    """
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        return DatabaseHealthResponse(
            status="error",
            database="unreachable",
            detail=type(exc).__name__,
        )
    return DatabaseHealthResponse(status="ok", database="connected")
