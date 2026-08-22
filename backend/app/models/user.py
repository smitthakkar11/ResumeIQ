"""The `users` table.

Phase 1 defines the schema only. The password hashing, JWT issuing and Google
account linking that use these columns arrive in Phase 2.
"""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base, TimestampMixin


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

    def __repr__(self) -> str:  # helpful in the REPL and in test failures
        return f"<User id={self.id} email={self.email!r}>"
