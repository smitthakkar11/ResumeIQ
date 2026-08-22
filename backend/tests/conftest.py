"""Pytest fixtures shared across the backend test suite."""

import os

import pytest

# Settings validation runs at import time, so a DATABASE_URL must exist before
# `app` is imported. Tests that do not touch MySQL can run with this placeholder.
os.environ.setdefault(
    "DATABASE_URL", "mysql+pymysql://resumeiq:resumeiq_dev_pw@localhost:3306/resume_analyzer"
)

from fastapi.testclient import TestClient  # noqa: E402

from app.main import create_app  # noqa: E402


@pytest.fixture(scope="session")
def client() -> TestClient:
    return TestClient(create_app())
