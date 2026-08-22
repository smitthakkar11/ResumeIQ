"""Pytest fixtures shared across the backend test suite.

Test isolation strategy: every test runs inside a transaction that is rolled
back afterwards, so tests share one real MySQL database without leaking rows
into each other. We test against MySQL rather than swapping in SQLite because
a test suite that exercises a different database than production is testing
the wrong thing — collations, constraint behaviour and type coercion all differ.
"""

import os
from collections.abc import Generator

import pytest

# Settings validation runs at import time, so these must exist before `app` is
# imported. Real values come from backend/.env when it is present.
os.environ.setdefault(
    "DATABASE_URL", "mysql+pymysql://resumeiq:resumeiq_dev_pw@localhost:3306/resume_analyzer"
)
os.environ.setdefault("SECRET_KEY", "test-only-secret-key-not-used-in-any-real-environment")

from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy import text  # noqa: E402
from sqlalchemy.exc import SQLAlchemyError  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.api.deps import get_db  # noqa: E402
from app.core.rate_limit import login_rate_limit, signup_rate_limit  # noqa: E402
from app.db.session import engine  # noqa: E402
from app.main import create_app  # noqa: E402


def database_is_reachable() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError:
        return False


requires_db = pytest.mark.skipif(
    not database_is_reachable(),
    reason="MySQL unreachable — run backend/scripts/init_db.sql and `alembic upgrade head`",
)


@pytest.fixture(autouse=True)
def reset_rate_limits() -> None:
    """Clear the auth rate limiters before every test.

    They are real production behaviour and are tested explicitly in
    test_security.py, but leaving their counters shared across tests would
    couple unrelated tests together — the 6th test that signs up would fail
    because of the 5 before it.
    """
    login_rate_limit._hits.clear()
    signup_rate_limit._hits.clear()


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """A Session whose writes are discarded when the test finishes.

    The session is bound to an explicit connection holding an open transaction.
    `join_transaction_mode="create_savepoint"` makes the application's own
    `session.commit()` calls commit to a SAVEPOINT instead of the real
    transaction — so production code commits normally, and we still roll the
    whole thing back at the end.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """A TestClient whose requests use the rolled-back session above.

    Dependency overrides are how FastAPI supports this without the application
    code knowing it is under test.
    """
    app = create_app()
    app.dependency_overrides[get_db] = lambda: db_session

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def signup_payload() -> dict[str, str]:
    return {"name": "Smit Thakkar", "email": "smit@example.com", "password": "correct-horse-1"}


@pytest.fixture
def registered(client: TestClient, signup_payload: dict[str, str]) -> dict:
    """Creates a user and returns the signup response body (token + user)."""
    response = client.post("/api/auth/signup", json=signup_payload)
    assert response.status_code == 201, response.text
    return response.json()


@pytest.fixture
def auth_headers(registered: dict) -> dict[str, str]:
    return {"Authorization": f"Bearer {registered['access_token']}"}
