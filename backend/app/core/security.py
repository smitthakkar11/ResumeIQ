"""Password hashing and JWT creation/verification.

Deliberately dependency-light: `bcrypt` and `PyJWT` directly, no wrapper
library. There is no magic here — read it and you can explain every line.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt
from jwt.exceptions import InvalidTokenError

from app.core.config import settings

# bcrypt operates on bytes and truncates input at 72 bytes. Passwords longer
# than that would silently share a hash with their 72-byte prefix, so we reject
# them at the schema layer rather than let the truncation happen unnoticed.
BCRYPT_MAX_BYTES = 72


# --------------------------------------------------------------------------
# Passwords
# --------------------------------------------------------------------------

def hash_password(password: str) -> str:
    """Hash a plaintext password with a fresh random salt.

    `gensalt(rounds=c)` runs 2^c iterations of bcrypt's key schedule. The salt,
    cost factor and algorithm are all encoded into the returned string, so
    verification needs nothing else stored alongside it:

        $2b$12$<22-char salt><31-char hash>
    """
    salt = bcrypt.gensalt(rounds=settings.BCRYPT_COST)
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    """Check a password against a stored hash.

    `checkpw` re-hashes the candidate using the salt and cost read out of the
    stored hash, then compares in constant time — a naive `==` would leak
    information through how long the comparison takes.
    """
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        # Malformed or truncated hash in the database — treat as a failed login
        # rather than a 500, but never as a success.
        return False


# --------------------------------------------------------------------------
# JSON Web Tokens
# --------------------------------------------------------------------------

def create_access_token(subject: int | str, expires_minutes: int | None = None) -> str:
    """Issue a signed access token identifying one user.

    The payload holds only non-secret claims — a JWT is signed, NOT encrypted,
    so anyone holding it can read the payload:

        sub  subject: the user id this token authenticates
        iat  issued-at
        exp  expiry — the only thing limiting a stolen token's usefulness,
             since a JWT cannot be revoked once issued
    """
    now = datetime.now(timezone.utc)
    expires = now + timedelta(minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload: dict[str, Any] = {
        "sub": str(subject),  # the JWT spec requires `sub` to be a string
        "iat": now,
        "exp": expires,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> int | None:
    """Verify a token's signature and expiry, returning the user id or None.

    `algorithms=[...]` is a whitelist, and it matters: without it a forged
    token could declare `"alg": "none"` and be accepted with no signature at
    all — a real historical CVE class in JWT libraries.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except InvalidTokenError:
        # Covers expired, tampered, malformed and wrong-algorithm tokens.
        return None

    subject = payload.get("sub")
    if subject is None:
        return None
    try:
        return int(subject)
    except (TypeError, ValueError):
        return None
