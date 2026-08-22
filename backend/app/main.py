"""FastAPI application entry point.

Built with a factory function (`create_app`) rather than a module-level object
so tests can spin up an isolated app instance with different settings.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        description="Resume ↔ job description compatibility analysis (NLP + ML).",
        version="0.1.0",
        # Interactive docs are a development convenience. In production they
        # publish the full API surface, so they are switched off there.
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
        openapi_url="/openapi.json" if settings.is_development else None,
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

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        """Defence-in-depth headers on every response.

        nosniff  stops a browser from guessing a response is HTML/JS
        DENY     blocks this API being framed for clickjacking
        no-referrer  keeps URLs (which can carry ids) out of Referer headers
        """
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response

    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    @app.get("/", tags=["root"])
    def root() -> dict[str, str]:
        return {"app": settings.APP_NAME, "docs": "/docs", "health": f"{settings.API_V1_PREFIX}/health"}

    return app


app = create_app()
