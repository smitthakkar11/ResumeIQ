"""The `users` table.

Phase 1 defines the schema only. The password hashing, JWT issuing and Google
account linking that use these columns arrive in Phase 2.
"""

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.oauth_account import OAuthAccount


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(120), nullable=False)

    # unique=True creates a UNIQUE index, which does double duty: it enforces
    # "one account per email" at the database level (the only place a race
    # condition cannot slip past) and makes login lookups an index seek.
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)

    # Nullable on purpose. A user who signs up with "Continue with Google" never
    # sets a password, so there is no hash to store. Phase 2 relies on this.
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)

    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    # cascade="all, delete-orphan" mirrors the FK's ON DELETE CASCADE on the
    # Python side, so an in-session delete behaves like the database will.
    oauth_accounts: Mapped[list["OAuthAccount"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    @property
    def has_password(self) -> bool:
        """False for accounts created purely through Google sign-in."""
        return self.password_hash is not None

    def __repr__(self) -> str:  # helpful in the REPL and in test failures
        return f"<User id={self.id} email={self.email!r}>"
