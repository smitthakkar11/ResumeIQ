"""Phase 3: PDF extraction and resume upload."""

import pymupdf
import pytest
from fastapi.testclient import TestClient

from app.services.resume.pdf_extractor import PdfError, extract_text
from tests.conftest import requires_db

RESUME_TEXT = (
    "Smit Thakkar\nsmit@example.com\n\n"
    "SKILLS\nPython, C++, React, MySQL, scikit-learn, Node.js, .NET\n\n"
    "EXPERIENCE\nBuilt a resume analysis platform using FastAPI and TF-IDF. "
    "Improved matching accuracy and reduced manual screening time.\n\n"
    "EDUCATION\nB.Tech Computer Science\n"
)


def make_pdf(text: str = RESUME_TEXT, pages: int = 1) -> bytes:
    doc = pymupdf.open()
    for _ in range(pages):
        page = doc.new_page()
        page.insert_text((72, 72), text, fontsize=11)
    data = doc.tobytes()
    doc.close()
    return data


# ---------------------------------------------------------------- extraction


class TestExtraction:
    def test_extracts_text_from_a_real_pdf(self) -> None:
        text, pages = extract_text(make_pdf(), "resume.pdf")
        assert pages == 1
        assert "Smit Thakkar" in text

    def test_preserves_technical_terms_exactly(self) -> None:
        """C++, .NET and Node.js must survive extraction intact."""
        text, _ = extract_text(make_pdf(), "resume.pdf")
        for term in ("C++", "Node.js", ".NET", "scikit-learn", "MySQL"):
            assert term in text

    def test_counts_pages(self) -> None:
        _, pages = extract_text(make_pdf(pages=3), "resume.pdf")
        assert pages == 3

    def test_rejects_empty_file(self) -> None:
        with pytest.raises(PdfError, match="empty"):
            extract_text(b"", "resume.pdf")

    def test_rejects_non_pdf_bytes_despite_pdf_filename(self) -> None:
        """The extension is client-supplied; only the magic bytes count."""
        with pytest.raises(PdfError, match="doesn't look like a PDF"):
            extract_text(b"just a text file, honestly", "resume.pdf")

    def test_rejects_corrupt_pdf(self) -> None:
        with pytest.raises(PdfError):
            extract_text(b"%PDF-1.7\n<<corrupted garbage>>", "resume.pdf")

    def test_rejects_oversized_file(self) -> None:
        with pytest.raises(PdfError, match="larger than"):
            extract_text(b"%PDF-" + b"x" * (6 * 1024 * 1024), "big.pdf")

    def test_rejects_pdf_with_no_text_layer(self) -> None:
        """A scanned resume is an image — extraction returns nothing."""
        doc = pymupdf.open()
        doc.new_page()  # a blank page: valid PDF, zero text
        data = doc.tobytes()
        doc.close()

        with pytest.raises(PdfError, match="No readable text"):
            extract_text(data, "scan.pdf")

    def test_rejects_too_many_pages(self) -> None:
        with pytest.raises(PdfError, match="longer than"):
            extract_text(make_pdf(pages=25), "long.pdf")

    def test_normalises_whitespace_without_altering_words(self) -> None:
        text, _ = extract_text(make_pdf("Python     and\n\n\n   C++   engineer" * 8), "r.pdf")
        assert "     " not in text
        assert "C++" in text


# ---------------------------------------------------------------------- API

pytestmark_db = requires_db


@requires_db
class TestUploadApi:
    def test_uploads_and_returns_extracted_text(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        response = client.post(
            "/api/resumes/upload",
            headers=auth_headers,
            files={"file": ("my_resume.pdf", make_pdf(), "application/pdf")},
        )
        assert response.status_code == 201
        body = response.json()
        assert body["filename"] == "my_resume.pdf"
        assert body["page_count"] == 1
        assert "Smit Thakkar" in body["extracted_text"]

    def test_upload_requires_authentication(self, client: TestClient) -> None:
        response = client.post(
            "/api/resumes/upload",
            files={"file": ("r.pdf", make_pdf(), "application/pdf")},
        )
        assert response.status_code == 401

    def test_bad_file_returns_400_not_500(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        response = client.post(
            "/api/resumes/upload",
            headers=auth_headers,
            files={"file": ("fake.pdf", b"not a pdf", "application/pdf")},
        )
        assert response.status_code == 400
        assert "PDF" in response.json()["detail"]

    def test_list_returns_only_summaries(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        client.post(
            "/api/resumes/upload",
            headers=auth_headers,
            files={"file": ("a.pdf", make_pdf(), "application/pdf")},
        )
        body = client.get("/api/resumes", headers=auth_headers).json()
        assert len(body) == 1
        assert "extracted_text" not in body[0]

    def test_delete_removes_the_resume(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        created = client.post(
            "/api/resumes/upload",
            headers=auth_headers,
            files={"file": ("a.pdf", make_pdf(), "application/pdf")},
        ).json()

        assert client.delete(f"/api/resumes/{created['id']}", headers=auth_headers).status_code == 204
        assert client.get(f"/api/resumes/{created['id']}", headers=auth_headers).status_code == 404


@requires_db
class TestResumeOwnership:
    """Spec §5: user A must never reach user B's resume."""

    def _register(self, client: TestClient, email: str) -> dict:
        token = client.post(
            "/api/auth/signup",
            json={"name": "User", "email": email, "password": "a-good-password"},
        ).json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def test_another_user_cannot_read_or_delete_it(self, client: TestClient) -> None:
        alice = self._register(client, "alice@example.com")
        bob = self._register(client, "bob@example.com")

        resume_id = client.post(
            "/api/resumes/upload",
            headers=alice,
            files={"file": ("alice.pdf", make_pdf(), "application/pdf")},
        ).json()["id"]

        # 404, not 403 — Bob learns nothing about whether it exists.
        assert client.get(f"/api/resumes/{resume_id}", headers=bob).status_code == 404
        assert client.delete(f"/api/resumes/{resume_id}", headers=bob).status_code == 404

        # And it is genuinely still there for Alice.
        assert client.get(f"/api/resumes/{resume_id}", headers=alice).status_code == 200

    def test_list_is_scoped_to_the_caller(self, client: TestClient) -> None:
        alice = self._register(client, "alice2@example.com")
        bob = self._register(client, "bob2@example.com")

        client.post(
            "/api/resumes/upload",
            headers=alice,
            files={"file": ("alice.pdf", make_pdf(), "application/pdf")},
        )
        assert client.get("/api/resumes", headers=bob).json() == []
        assert len(client.get("/api/resumes", headers=alice).json()) == 1


@requires_db
class TestResumeSkillsEndpoint:
    def test_returns_skills_found_in_the_resume(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        created = client.post(
            "/api/resumes/upload",
            headers=auth_headers,
            files={"file": ("r.pdf", make_pdf(), "application/pdf")},
        ).json()

        body = client.get(f"/api/resumes/{created['id']}/skills", headers=auth_headers).json()
        found = {s["name"] for s in body["skills"]}

        assert {"Python", "C++", "React", "MySQL", "scikit-learn", "Node.js", ".NET"} <= found
        assert body["total"] == len(body["skills"])

    def test_another_user_gets_404(self, client: TestClient, auth_headers: dict) -> None:
        created = client.post(
            "/api/resumes/upload",
            headers=auth_headers,
            files={"file": ("r.pdf", make_pdf(), "application/pdf")},
        ).json()

        other = client.post(
            "/api/auth/signup",
            json={"name": "Other", "email": "other@example.com", "password": "a-good-password"},
        ).json()["access_token"]

        response = client.get(
            f"/api/resumes/{created['id']}/skills",
            headers={"Authorization": f"Bearer {other}"},
        )
        assert response.status_code == 404


@requires_db
class TestResumeQualityEndpoint:
    """Phase B: resume quality, independent of any job description."""

    def _upload(self, client: TestClient, headers: dict) -> int:
        return client.post(
            "/api/resumes/upload",
            headers=headers,
            files={"file": ("r.pdf", make_pdf(), "application/pdf")},
        ).json()["id"]

    def test_returns_an_explainable_breakdown(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        resume_id = self._upload(client, auth_headers)
        body = client.get(f"/api/resumes/{resume_id}/quality", headers=auth_headers).json()

        assert 0 <= body["overall"] <= 100
        assert [c["key"] for c in body["components"]] == [
            "skills", "keywords", "projects", "experience", "education", "formatting"
        ]
        # Every component must justify its score.
        for component in body["components"]:
            assert component["checks"]
            assert all(check["detail"] for check in component["checks"])

    def test_another_user_gets_404(self, client: TestClient, auth_headers: dict) -> None:
        resume_id = self._upload(client, auth_headers)
        other = client.post(
            "/api/auth/signup",
            json={"name": "Other", "email": "otherq@example.com", "password": "a-good-password"},
        ).json()["access_token"]

        response = client.get(
            f"/api/resumes/{resume_id}/quality",
            headers={"Authorization": f"Bearer {other}"},
        )
        assert response.status_code == 404

    def test_requires_authentication(self, client: TestClient, auth_headers: dict) -> None:
        resume_id = self._upload(client, auth_headers)
        assert client.get(f"/api/resumes/{resume_id}/quality").status_code == 401

    def test_analysis_also_carries_the_quality_score(
        self, client: TestClient, auth_headers: dict
    ) -> None:
        resume_id = self._upload(client, auth_headers)
        created = client.post(
            "/api/analyses",
            headers=auth_headers,
            json={
                "resume_id": resume_id,
                "job_title": "Engineer",
                "job_description": "Requirements: Python, React and MySQL for our platform team.",
            },
        ).json()

        assert created["resume_quality_score"] is not None
        assert len(created["quality_breakdown"]) == 6

        # ...and it survives a reload, because it is stored not recomputed.
        fetched = client.get(f"/api/analyses/{created['id']}", headers=auth_headers).json()
        assert fetched["resume_quality_score"] == created["resume_quality_score"]
