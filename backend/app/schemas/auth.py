"""Request/response contracts for authentication.

Note what is NOT here: there is no schema that ever contains `password_hash`.
Keeping API shapes separate from ORM models is what makes that guarantee
structural rather than a thing you have to remember.
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.core.security import BCRYPT_MAX_BYTES


class SignupRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def password_must_fit_bcrypt(cls, value: str) -> str:
        """bcrypt silently truncates past 72 BYTES (not characters).

        Without this check, 'a'*80 and 'a'*100 would produce the same hash and
        both would unlock the account. Rejecting is safer than truncating.
        """
        if len(value.encode("utf-8")) > BCRYPT_MAX_BYTES:
            raise ValueError(f"password must be at most {BCRYPT_MAX_BYTES} bytes")
        return value

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("name must not be blank")
        return cleaned


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class GoogleAuthRequest(BaseModel):
    """The one-time authorization code returned by Google to the browser.

    The code alone is useless to an attacker: redeeming it requires
    GOOGLE_CLIENT_SECRET, which never leaves the backend.
    """

    code: str = Field(min_length=1)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    is_active: bool
    has_password: bool
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="Seconds until the token expires")
    user: UserResponse
