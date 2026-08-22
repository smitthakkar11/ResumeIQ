"""Database engine and per-request session management."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

# The Engine owns a *pool* of TCP connections to MySQL. Creating it is expensive,
# so we do it once at import time and reuse it for the life of the process.
#
#   pool_pre_ping: MySQL drops idle connections after `wait_timeout` (8h default).
#                  Without this you get "MySQL server has gone away" in production.
#   pool_recycle:  proactively retire connections older than 1h.
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False,
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency: one Session per HTTP request, always closed.

    Used as `db: Session = Depends(get_db)`. The `yield` hands the session to the
    endpoint; the `finally` runs after the response is produced, so the
    connection returns to the pool even if the endpoint raised.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
