"""Phase 7: persistence, history and cross-user isolation."""

from fastapi.testclient import TestClient

from tests.conftest import requires_db
from tests.test_resumes import make_pdf

pytestmark = requires_db

JOB = (
    "Software Engineer. Looking for Python, React, MySQL, Docker and AWS. "
    "Kubernetes is a plus. You will build REST APIs in an Agile team."
)
OTHER_JOB = (
    "Data Analyst. We need strong SQL, pandas and Tableau skills to build "
    "dashboards and reports for the commercial team every week."
)


def register(client: TestClient, email: str) -> dict:
    token = client.post(
        "/api/auth/signup",
        json={"name": "User", "email": email, "password": "a-good-password"},
    ).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def upload(client: TestClient, headers: dict, name: str = "r.pdf") -> int:
    return client.post(
        "/api/resumes/upload",
        headers=headers,
        files={"file": (name, make_pdf(), "application/pdf")},
    ).json()["id"]


def run_analysis(client: TestClient, headers: dict, resume_id: int, job: str = JOB, title: str = "SWE") -> dict:
    response = client.post(
        "/api/analyses",
        headers=headers,
        json={"resume_id": resume_id, "job_title": title, "job_description": job},
    )
    assert response.status_code == 201, response.text
    return response.json()


class TestPersistence:
    def test_analysis_is_saved_and_retrievable(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        created = run_analysis(client, auth_headers, upload(client, auth_headers))
        fetched = client.get(f"/api/analyses/{created['id']}", headers=auth_headers).json()

        assert fetched["id"] == created["id"]
        assert fetched["match_score"] == created["match_score"]
        assert fetched["matched_skills"] == created["matched_skills"]
        assert fetched["recommendations"] == created["recommendations"]

    def test_stored_result_is_a_snapshot_not_a_recomputation(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        """Reading it back must not re-run the engine — scores must be stable."""
        created = run_analysis(client, auth_headers, upload(client, auth_headers))
        first = client.get(f"/api/analyses/{created['id']}", headers=auth_headers).json()
        second = client.get(f"/api/analyses/{created['id']}", headers=auth_headers).json()
        assert first == second

    def test_history_is_newest_first(self, client: TestClient, auth_headers: dict) -> None:
        resume_id = upload(client, auth_headers)
        run_analysis(client, auth_headers, resume_id, JOB, "First")
        run_analysis(client, auth_headers, resume_id, OTHER_JOB, "Second")

        history = client.get("/api/analyses", headers=auth_headers).json()
        assert [a["job_title"] for a in history] == ["Second", "First"]

    def test_list_omits_the_heavy_json_blobs(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        run_analysis(client, auth_headers, upload(client, auth_headers))
        row = client.get("/api/analyses", headers=auth_headers).json()[0]
        assert "matched_skills" not in row
        assert "recommendations" not in row

    def test_delete_removes_it(self, client: TestClient, auth_headers: dict) -> None:
        created = run_analysis(client, auth_headers, upload(client, auth_headers))
        assert client.delete(f"/api/analyses/{created['id']}", headers=auth_headers).status_code == 204
        assert client.get(f"/api/analyses/{created['id']}", headers=auth_headers).status_code == 404


class TestJobDescriptionReuse:
    def test_the_same_posting_is_stored_once(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        resume_id = upload(client, auth_headers)
        first = run_analysis(client, auth_headers, resume_id)
        second = run_analysis(client, auth_headers, resume_id)

        assert first["job_description_id"] == second["job_description_id"]
        assert len(client.get("/api/jobs", headers=auth_headers).json()) == 1

    def test_a_different_posting_creates_a_new_row(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        resume_id = upload(client, auth_headers)
        run_analysis(client, auth_headers, resume_id, JOB)
        run_analysis(client, auth_headers, resume_id, OTHER_JOB)
        assert len(client.get("/api/jobs", headers=auth_headers).json()) == 2

    def test_job_detail_returns_the_full_text(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        created = run_analysis(client, auth_headers, upload(client, auth_headers))
        job = client.get(f"/api/jobs/{created['job_description_id']}", headers=auth_headers).json()
        assert job["description"] == JOB


class TestResumeVersioning:
    def test_versions_increment_per_user(self, client: TestClient, auth_headers: dict) -> None:
        upload(client, auth_headers, "v1.pdf")
        upload(client, auth_headers, "v2.pdf")
        upload(client, auth_headers, "v3.pdf")

        versions = {r["filename"]: r["version"] for r in client.get("/api/resumes", headers=auth_headers).json()}
        assert versions == {"v1.pdf": 1, "v2.pdf": 2, "v3.pdf": 3}

    def test_each_users_versions_start_at_one(self, client: TestClient) -> None:
        alice = register(client, "alice7@example.com")
        bob = register(client, "bob7@example.com")

        upload(client, alice, "a1.pdf")
        upload(client, alice, "a2.pdf")
        bob_resume = upload(client, bob, "b1.pdf")

        assert client.get(f"/api/resumes/{bob_resume}", headers=bob).json()["version"] == 1


class TestDeletingAResumeKeepsHistory:
    def test_analysis_survives_with_its_filename(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        """ON DELETE SET NULL, not CASCADE — history must not develop holes."""
        resume_id = upload(client, auth_headers, "my_resume.pdf")
        created = run_analysis(client, auth_headers, resume_id)

        assert client.delete(f"/api/resumes/{resume_id}", headers=auth_headers).status_code == 204

        fetched = client.get(f"/api/analyses/{created['id']}", headers=auth_headers).json()
        assert fetched["resume_id"] is None          # link gone
        assert fetched["resume_filename"] == "my_resume.pdf"  # snapshot kept
        assert fetched["match_score"] == created["match_score"]


class TestOwnership:
    """Spec §5 and §21: a user must never reach another user's data."""

    def test_history_is_scoped_to_the_caller(self, client: TestClient) -> None:
        alice = register(client, "alice8@example.com")
        bob = register(client, "bob8@example.com")

        run_analysis(client, alice, upload(client, alice))
        assert client.get("/api/analyses", headers=bob).json() == []
        assert len(client.get("/api/analyses", headers=alice).json()) == 1

    def test_cannot_read_another_users_analysis(self, client: TestClient) -> None:
        alice = register(client, "alice9@example.com")
        bob = register(client, "bob9@example.com")
        created = run_analysis(client, alice, upload(client, alice))

        assert client.get(f"/api/analyses/{created['id']}", headers=bob).status_code == 404

    def test_cannot_delete_another_users_analysis(self, client: TestClient) -> None:
        alice = register(client, "alice10@example.com")
        bob = register(client, "bob10@example.com")
        created = run_analysis(client, alice, upload(client, alice))

        assert client.delete(f"/api/analyses/{created['id']}", headers=bob).status_code == 404
        # ...and it really is still there for Alice.
        assert client.get(f"/api/analyses/{created['id']}", headers=alice).status_code == 200

    def test_cannot_read_another_users_job_description(self, client: TestClient) -> None:
        alice = register(client, "alice11@example.com")
        bob = register(client, "bob11@example.com")
        created = run_analysis(client, alice, upload(client, alice))

        job_id = created["job_description_id"]
        assert client.get(f"/api/jobs/{job_id}", headers=bob).status_code == 404

    def test_job_list_is_scoped_to_the_caller(self, client: TestClient) -> None:
        alice = register(client, "alice12@example.com")
        bob = register(client, "bob12@example.com")
        run_analysis(client, alice, upload(client, alice))
        assert client.get("/api/jobs", headers=bob).json() == []

    def test_all_history_endpoints_require_authentication(self, client: TestClient) -> None:
        for method, path in [
            ("get", "/api/analyses"),
            ("get", "/api/analyses/1"),
            ("delete", "/api/analyses/1"),
            ("get", "/api/jobs"),
            ("get", "/api/jobs/1"),
        ]:
            assert getattr(client, method)(path).status_code == 401, path


@requires_db
class TestJobDescriptionIntelligence:
    """Phase A: parsed requirements are stored on the job row and returned."""

    STRUCTURED = (
        "Backend Engineer\n"
        "Requirements\n"
        "- 2+ years with Python and MySQL\n"
        "- Bachelor's degree required\n"
        "Preferred qualifications\n"
        "- Docker experience\n"
    )

    def test_analysis_returns_parsed_requirements(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        resume_id = upload(client, auth_headers)
        body = run_analysis(client, auth_headers, resume_id, self.STRUCTURED, "Backend")

        req = body["requirements"]
        assert req["role"] == "Backend Engineer"
        assert req["education"] == "Bachelor's"
        assert req["min_years"] == 2
        assert "Docker" in {s["name"] for s in req["preferred_skills"]}

    def test_requirements_survive_a_reload(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        """Stored on the job row, so reopening the analysis still shows them."""
        resume_id = upload(client, auth_headers)
        created = run_analysis(client, auth_headers, resume_id, self.STRUCTURED, "Backend")

        fetched = client.get(f"/api/analyses/{created['id']}", headers=auth_headers).json()
        assert fetched["requirements"]["role"] == "Backend Engineer"

    def test_company_is_stored_on_the_job(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        resume_id = upload(client, auth_headers)
        response = client.post(
            "/api/analyses",
            headers=auth_headers,
            json={
                "resume_id": resume_id,
                "job_title": "Backend",
                "company": "Acme Corp",
                "job_description": self.STRUCTURED,
            },
        )
        assert response.status_code == 201

        job_id = response.json()["job_description_id"]
        job = client.get(f"/api/jobs/{job_id}", headers=auth_headers).json()
        assert job["company"] == "Acme Corp"
        assert job["role"] == "Backend Engineer"
        assert job["parsed"]["education"] == "Bachelor's"

    def test_partial_skills_are_persisted(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        resume_id = upload(client, auth_headers)
        created = run_analysis(
            client, auth_headers, resume_id,
            "Requirements: Django and Python are essential for this backend role.",
            "Backend",
        )
        # The test resume names FastAPI, which shares the "backend" tag.
        partial = {p["name"] for p in created["partial_skills"]}
        assert "Django" in partial

        fetched = client.get(f"/api/analyses/{created['id']}", headers=auth_headers).json()
        assert {p["name"] for p in fetched["partial_skills"]} == partial
