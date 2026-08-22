"""Unit tests for hashing and JWTs. No database, no HTTP."""

import time

import jwt
import pytest

from app.core.config import settings
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


class TestPasswordHashing:
    def test_hash_is_not_the_plaintext(self) -> None:
        assert hash_password("hunter2") != "hunter2"

    def test_hash_uses_bcrypt_with_the_configured_cost(self) -> None:
        assert hash_password("hunter2").startswith(f"$2b${settings.BCRYPT_COST:02d}$")

    def test_same_password_hashes_differently_each_time(self) -> None:
        """Proves a fresh random salt is used — defeats rainbow tables."""
        assert hash_password("hunter2") != hash_password("hunter2")

    def test_correct_password_verifies(self) -> None:
        assert verify_password("hunter2", hash_password("hunter2")) is True

    def test_wrong_password_is_rejected(self) -> None:
        assert verify_password("hunter3", hash_password("hunter2")) is False

    def test_malformed_hash_fails_closed(self) -> None:
        """A corrupt hash must deny access, never grant it or 500."""
        assert verify_password("hunter2", "not-a-bcrypt-hash") is False


class TestAccessTokens:
    def test_round_trip_returns_the_subject(self) -> None:
        assert decode_access_token(create_access_token(42)) == 42

    def test_payload_is_readable_and_holds_no_secrets(self) -> None:
        """A JWT is signed, not encrypted — assert we rely on that knowingly."""
        claims = jwt.decode(create_access_token(42), options={"verify_signature": False})
        assert claims["sub"] == "42"
        assert set(claims) == {"sub", "iat", "exp"}

    def test_tampered_token_is_rejected(self) -> None:
        token = create_access_token(42)
        forged = token[:-6] + ("AAAAAA" if not token.endswith("AAAAAA") else "BBBBBB")
        assert decode_access_token(forged) is None

    def test_token_signed_with_another_key_is_rejected(self) -> None:
        foreign = jwt.encode(
            {"sub": "42"}, "a-completely-different-secret-key-of-sufficient-length", algorithm="HS256"
        )
        assert decode_access_token(foreign) is None

    def test_alg_none_token_is_rejected(self) -> None:
        """The classic JWT attack: strip the signature by declaring alg=none."""
        forged = jwt.encode({"sub": "42"}, key="", algorithm="none")
        assert decode_access_token(forged) is None

    def test_expired_token_is_rejected(self) -> None:
        token = create_access_token(42, expires_minutes=-1)
        assert decode_access_token(token) is None

    def test_garbage_is_rejected(self) -> None:
        assert decode_access_token("not.a.jwt") is None

    @pytest.mark.parametrize("expires", [1, 5])
    def test_valid_token_survives_a_moment(self, expires: int) -> None:
        token = create_access_token(42, expires_minutes=expires)
        time.sleep(0.05)
        assert decode_access_token(token) == 42


class TestRateLimiting:
    """Without this, bcrypt's cost is the only thing slowing a brute-force."""

    def test_repeated_failed_logins_are_eventually_blocked(self, client) -> None:
        body = {"email": "nobody@example.com", "password": "wrong"}
        codes = [client.post("/api/auth/login", json=body).status_code for _ in range(12)]

        assert 429 in codes, "login is brute-forceable"
        assert codes.index(429) >= 10, "limiter fired too early for an honest typo"

    def test_blocked_response_says_when_to_retry(self, client) -> None:
        body = {"email": "nobody@example.com", "password": "wrong"}
        response = None
        for _ in range(12):
            response = client.post("/api/auth/login", json=body)
            if response.status_code == 429:
                break

        assert response.status_code == 429
        assert int(response.headers["Retry-After"]) > 0

    def test_signup_is_limited_more_tightly_than_login(self) -> None:
        from app.core.rate_limit import login_rate_limit, signup_rate_limit

        signup_per_hour = signup_rate_limit.limit / signup_rate_limit.window
        login_per_hour = login_rate_limit.limit / login_rate_limit.window
        assert signup_per_hour < login_per_hour


class TestSecurityHeaders:
    def test_responses_carry_defence_in_depth_headers(self, client) -> None:
        headers = client.get("/api/health").headers
        assert headers["X-Content-Type-Options"] == "nosniff"
        assert headers["X-Frame-Options"] == "DENY"
        assert headers["Referrer-Policy"] == "no-referrer"


class TestSecretKeyValidation:
    def test_a_short_secret_key_is_rejected_at_startup(self) -> None:
        """A forgeable signing key must fail loudly, not silently work."""
        import pydantic
        import pytest as _pytest

        from app.core.config import Settings

        with _pytest.raises(pydantic.ValidationError, match="at least 32 characters"):
            Settings(SECRET_KEY="tooshort", DATABASE_URL="mysql+pymysql://u:p@localhost/db")

    def test_the_placeholder_secret_is_rejected(self) -> None:
        import pydantic
        import pytest as _pytest

        from app.core.config import Settings

        with _pytest.raises(pydantic.ValidationError, match="placeholder"):
            Settings(
                SECRET_KEY="replace_me_with_a_long_random_string",
                DATABASE_URL="mysql+pymysql://u:p@localhost/db",
            )
