"""Aggregates every route module into one router mounted by `main.py`."""

from fastapi import APIRouter

from app.api.routes import analyses, auth, health, resumes

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(resumes.router)
api_router.include_router(analyses.router)

__all__ = ["api_router"]
