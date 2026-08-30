"""Phase 5: the POST /api/analyses endpoint."""

from fastapi.testclient import TestClient

from tests.conftest import requires_db
from tests.test_resumes import make_pdf

pytestmark = requires_db

JOB = (
    "Software Engineer. Looking for an engineer with Python, React, MySQL, "
    "Docker and AWS. Kubernetes is a plus. You will build REST APIs."
)


def upload(client: TestClient, headers: dict) -> int:
    return client.post(
        "/api/resumes/upload",
        headers=headers,
        files={"file": ("r.pdf", make_pdf(), "application/pdf")},
    ).json()["id"]


class TestAnalyseEndpoint:
    def test_returns_a_full_breakdown(self, client: TestClient, auth_headers: dict) -> None:
        resume_id = upload(client, auth_headers)
        response = client.post(
            "/api/analyses",
            headers=auth_headers,
            json={"resume_id": resume_id, "job_title": "SWE Intern", "job_description": JOB},
        )
        assert response.status_code == 201

        body = response.json()
        assert body["job_title"] == "SWE Intern"
        assert 0 <= body["match_score"] <= 100
        assert {s["name"] for s in body["matched_skills"]} >= {"Python", "React", "MySQL"}
        assert "Docker" in {s["name"] for s in body["missing_skills"]}
        assert any(k["term"] == "docker" and not k["found"] for k in body["keywords"])

        # "Kubernetes is a plus" makes it preferred, so it must NOT be counted
        # as a missing requirement — a nice-to-have cannot drag the score down.
        assert "Kubernetes" not in {s["name"] for s in body["missing_skills"]}
        assert "Kubernetes" in {s["name"] for s in body["requirements"]["preferred_skills"]}

    def test_requires_authentication(self, client: TestClient) -> None:
        response = client.post(
            "/api/analyses", json={"resume_id": 1, "job_description": JOB}
        )
        assert response.status_code == 401

    def test_rejects_a_very_short_job_description(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        resume_id = upload(client, auth_headers)
        response = client.post(
            "/api/analyses",
            headers=auth_headers,
            json={"resume_id": resume_id, "job_description": "Need a dev"},
        )
        assert response.status_code == 422

    def test_cannot_analyse_another_users_resume(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        resume_id = upload(client, auth_headers)
        other = client.post(
            "/api/auth/signup",
            json={"name": "Other", "email": "other5@example.com", "password": "a-good-password"},
        ).json()["access_token"]

        response = client.post(
            "/api/analyses",
            headers={"Authorization": f"Bearer {other}"},
            json={"resume_id": resume_id, "job_description": JOB},
        )
        assert response.status_code == 404

    def test_unknown_resume_returns_404(self, client: TestClient, auth_headers: dict) -> None:
        response = client.post(
            "/api/analyses",
            headers=auth_headers,
            json={"resume_id": 999_999, "job_description": JOB},
        )
        assert response.status_code == 404
