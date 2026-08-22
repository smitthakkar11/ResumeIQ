"""All database access for users and their linked OAuth accounts.

Why a repository layer at all: it keeps `session.query(...)` out of the
service and route layers, so business logic can be read (and tested) without
SQLAlchemy noise, and every query touching users lives in one auditable file.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.oauth_account import OAuthAccount
from app.models.user import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    # ---- reads ----

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        """Emails are matched case-insensitively by storing them lowercased.

        MySQL's default collation is already case-insensitive, but relying on
        that would make the behaviour depend on database configuration rather
        than on our code.
        """
        stmt = select(User).where(User.email == email.strip().lower())
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_oauth_account(self, provider: str, provider_account_id: str) -> User | None:
        stmt = (
            select(User)
            .join(OAuthAccount)
            .where(
                OAuthAccount.provider == provider,
                OAuthAccount.provider_account_id == provider_account_id,
            )
        )
        return self.db.execute(stmt).scalar_one_or_none()

    # ---- writes ----

    def create(self, *, name: str, email: str, password_hash: str | None) -> User:
        user = User(name=name.strip(), email=email.strip().lower(), password_hash=password_hash)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def link_oauth_account(
        self, *, user: User, provider: str, provider_account_id: str
    ) -> OAuthAccount:
        account = OAuthAccount(
            user_id=user.id,
            provider=provider,
            provider_account_id=provider_account_id,
        )
        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)
        return account
