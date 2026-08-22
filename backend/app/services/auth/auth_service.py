"""Signup and login logic.

Raises domain-specific exceptions rather than HTTPException so this module
stays testable without FastAPI; the route layer translates them into
status codes.
"""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository


class AuthError(Exception):
    """Base class for authentication failures."""


class EmailAlreadyRegisteredError(AuthError):
    pass


class InvalidCredentialsError(AuthError):
    pass


class InactiveUserError(AuthError):
    pass


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.users = UserRepository(db)

    def signup(self, *, name: str, email: str, password: str) -> User:
        if self.users.get_by_email(email):
            raise EmailAlreadyRegisteredError

        try:
            return self.users.create(
                name=name,
                email=email,
                password_hash=hash_password(password),
            )
        except IntegrityError:
            # The check above loses a race between two simultaneous signups.
            # The UNIQUE index on users.email is the real guarantee; this
            # converts the resulting database error into a clean 409.
            self.db.rollback()
            raise EmailAlreadyRegisteredError from None

    def login(self, *, email: str, password: str) -> User:
        user = self.users.get_by_email(email)

        # Deliberately identical failure for "no such user" and "wrong
        # password". Distinguishing them turns the login form into an account
        # enumeration oracle: an attacker could discover which emails are
        # registered without ever guessing a password.
        if user is None or not user.has_password:
            raise InvalidCredentialsError
        if not verify_password(password, user.password_hash or ""):
            raise InvalidCredentialsError
        if not user.is_active:
            raise InactiveUserError

        return user

    @staticmethod
    def issue_token(user: User) -> tuple[str, int]:
        """Return (access_token, seconds_until_expiry)."""
        token = create_access_token(user.id)
        return token, settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
