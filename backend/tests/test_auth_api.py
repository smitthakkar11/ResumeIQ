"""End-to-end tests for the authentication endpoints."""

from fastapi.testclient import TestClient

from tests.conftest import requires_db

pytestmark = requires_db


class TestSignup:
    def test_creates_an_account_and_returns_a_token(
        self, client: TestClient, signup_payload: dict
    ) -> None:
        response = client.post("/api/auth/signup", json=signup_payload)
        assert response.status_code == 201

        body = response.json()
        assert body["token_type"] == "bearer"
        assert body["access_token"]
        assert body["user"]["email"] == signup_payload["email"]
        assert body["user"]["has_password"] is True

    def test_response_never_leaks_the_password_or_its_hash(
        self, client: TestClient, signup_payload: dict
    ) -> None:
        raw = client.post("/api/auth/signup", json=signup_payload).text
        assert signup_payload["password"] not in raw
        assert "password_hash" not in raw
        assert "$2b$" not in raw

    def test_duplicate_email_is_rejected_with_409(
        self, client: TestClient, signup_payload: dict
    ) -> None:
        client.post("/api/auth/signup", json=signup_payload)
        second = client.post("/api/auth/signup", json=signup_payload)
        assert second.status_code == 409

    def test_email_is_stored_lowercased(self, client: TestClient, signup_payload: dict) -> None:
        payload = {**signup_payload, "email": "SMIT@Example.COM"}
        response = client.post("/api/auth/signup", json=payload)
        assert response.json()["user"]["email"] == "smit@example.com"

    def test_rejects_invalid_email(self, client: TestClient, signup_payload: dict) -> None:
        response = client.post("/api/auth/signup", json={**signup_payload, "email": "nope"})
        assert response.status_code == 422

    def test_rejects_short_password(self, client: TestClient, signup_payload: dict) -> None:
        response = client.post("/api/auth/signup", json={**signup_payload, "password": "abc"})
        assert response.status_code == 422

    def test_rejects_password_longer_than_bcrypts_72_byte_limit(
        self, client: TestClient, signup_payload: dict
    ) -> None:
        """Truncating silently would make two different passwords equivalent."""
        response = client.post("/api/auth/signup", json={**signup_payload, "password": "a" * 100})
        assert response.status_code == 422


class TestLogin:
    def test_correct_credentials_return_a_token(
        self, client: TestClient, registered: dict, signup_payload: dict
    ) -> None:
        response = client.post(
            "/api/auth/login",
            json={"email": signup_payload["email"], "password": signup_payload["password"]},
        )
        assert response.status_code == 200
        assert response.json()["user"]["id"] == registered["user"]["id"]

    def test_wrong_password_is_rejected(
        self, client: TestClient, registered: dict, signup_payload: dict
    ) -> None:
        response = client.post(
            "/api/auth/login",
            json={"email": signup_payload["email"], "password": "wrong-password"},
        )
        assert response.status_code == 401

    def test_unknown_email_gives_the_same_error_as_a_wrong_password(
        self, client: TestClient, registered: dict, signup_payload: dict
    ) -> None:
        """Different messages would let an attacker enumerate registered emails."""
        wrong_password = client.post(
            "/api/auth/login",
            json={"email": signup_payload["email"], "password": "wrong-password"},
        )
        unknown_email = client.post(
            "/api/auth/login",
            json={"email": "nobody@example.com", "password": "wrong-password"},
        )
        assert wrong_password.status_code == unknown_email.status_code == 401
        assert wrong_password.json()["detail"] == unknown_email.json()["detail"]

    def test_login_is_case_insensitive_on_email(
        self, client: TestClient, registered: dict, signup_payload: dict
    ) -> None:
        response = client.post(
            "/api/auth/login",
            json={"email": "SMIT@EXAMPLE.COM", "password": signup_payload["password"]},
        )
        assert response.status_code == 200


class TestCurrentUser:
    def test_returns_the_authenticated_user(
        self, client: TestClient, auth_headers: dict, registered: dict
    ) -> None:
        response = client.get("/api/auth/me", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["id"] == registered["user"]["id"]

    def test_requires_a_token(self, client: TestClient) -> None:
        assert client.get("/api/auth/me").status_code == 401

    def test_rejects_a_garbage_token(self, client: TestClient) -> None:
        response = client.get("/api/auth/me", headers={"Authorization": "Bearer not.a.jwt"})
        assert response.status_code == 401

    def test_rejects_a_token_for_a_user_that_no_longer_exists(self, client: TestClient) -> None:
        """A signature check alone is not enough — the row must still be there."""
        from app.core.security import create_access_token

        orphan = create_access_token(999_999)
        response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {orphan}"})
        assert response.status_code == 401

    def test_rejects_an_expired_token(self, client: TestClient, registered: dict) -> None:
        from app.core.security import create_access_token

        expired = create_access_token(registered["user"]["id"], expires_minutes=-1)
        response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {expired}"})
        assert response.status_code == 401

    def test_rejects_a_missing_bearer_prefix(self, client: TestClient, registered: dict) -> None:
        response = client.get(
            "/api/auth/me", headers={"Authorization": registered["access_token"]}
        )
        assert response.status_code == 401


class TestAuthorizationBetweenUsers:
    """Spec §28: user A must not be able to act as user B."""

    def test_a_token_only_ever_identifies_its_own_user(
        self, client: TestClient, signup_payload: dict
    ) -> None:
        alice = client.post("/api/auth/signup", json=signup_payload).json()
        bob = client.post(
            "/api/auth/signup",
            json={"name": "Bob", "email": "bob@example.com", "password": "bobs-password-1"},
        ).json()

        assert alice["user"]["id"] != bob["user"]["id"]

        alice_me = client.get(
            "/api/auth/me", headers={"Authorization": f"Bearer {alice['access_token']}"}
        ).json()
        bob_me = client.get(
            "/api/auth/me", headers={"Authorization": f"Bearer {bob['access_token']}"}
        ).json()

        assert alice_me["id"] == alice["user"]["id"]
        assert bob_me["id"] == bob["user"]["id"]
        assert alice_me["email"] != bob_me["email"]


class TestGoogleProvider:
    def test_providers_endpoint_never_exposes_the_client_secret(
        self, client: TestClient
    ) -> None:
        body = client.get("/api/auth/providers").json()
        assert set(body) == {"password", "google", "google_client_id"}
        assert "secret" not in client.get("/api/auth/providers").text.lower()

    def test_google_endpoint_reports_503_when_not_configured(self, client: TestClient) -> None:
        from app.core.config import settings

        if settings.google_oauth_configured:
            import pytest

            pytest.skip("Google OAuth is configured in this environment")

        response = client.post("/api/auth/google", json={"code": "irrelevant"})
        assert response.status_code == 503
