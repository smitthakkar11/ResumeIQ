"""FastAPI application entry point.

Built with a factory function (`create_app`) rather than a module-level object
so tests can spin up an isolated app instance with different settings.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        description="Resume ↔ job description compatibility analysis (NLP + ML).",
        version="0.1.0",
        docs_url="/docs",
        openapi_url="/openapi.json",
    )

    # The browser refuses cross-origin requests (localhost:5173 -> localhost:8000)
    # unless the server explicitly opts in with these headers. allow_credentials
    # is on because Phase 2 will send an Authorization header / cookie.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    @app.get("/", tags=["root"])
    def root() -> dict[str, str]:
        return {"app": settings.APP_NAME, "docs": "/docs", "health": f"{settings.API_V1_PREFIX}/health"}

    return app


app = create_app()
