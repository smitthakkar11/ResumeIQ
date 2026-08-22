"""Integration tests that need a real MySQL server.

These skip (rather than fail) when the database is unreachable, so the suite
still runs on a machine that has not been bootstrapped yet. Unit tests must
never depend on external services; integration tests may, but must say so.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError

from app.db.session import engine


def _database_is_reachable() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError:
        return False


requires_db = pytest.mark.skipif(
    not _database_is_reachable(),
    reason="MySQL unreachable — run backend/scripts/init_db.sql and `alembic upgrade head`",
)


@requires_db
def test_health_db_reports_connected(client: TestClient) -> None:
    response = client.get("/api/health/db")
    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "ok"
    assert body["database"] == "connected"


@requires_db
def test_migration_created_the_users_table() -> None:
    inspector = inspect(engine)
    assert "users" in inspector.get_table_names()

    columns = {c["name"] for c in inspector.get_columns("users")}
    assert columns == {
        "id",
        "name",
        "email",
        "password_hash",
        "is_active",
        "created_at",
        "updated_at",
    }


@requires_db
def test_email_has_a_unique_index() -> None:
    """The uniqueness guarantee must live in the database, not just in Python.

    Application-level "check if the email exists first" loses to a race between
    two concurrent signups; a UNIQUE index cannot.
    """
    inspector = inspect(engine)
    unique_indexed = {
        col
        for index in inspector.get_indexes("users")
        if index["unique"]
        for col in index["column_names"]
    }
    assert "email" in unique_indexed


@requires_db
def test_password_hash_is_nullable_for_google_only_accounts() -> None:
    inspector = inspect(engine)
    password_hash = next(c for c in inspector.get_columns("users") if c["name"] == "password_hash")
    assert password_hash["nullable"] is True
