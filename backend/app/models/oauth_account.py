"""Links a local user to an external identity provider (currently Google).

Kept in its own table rather than as a `google_id` column on `users` because:
  * one user may link several providers over time
  * a UNIQUE(provider, provider_account_id) constraint prevents two local
    accounts from claiming the same Google identity
"""

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base, TimestampMixin


class OAuthAccount(Base, TimestampMixin):
    __tablename__ = "oauth_accounts"
    __table_args__ = (
        UniqueConstraint("provider", "provider_account_id", name="uq_oauth_provider_account"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # ondelete="CASCADE": deleting a user removes their linked identities too,
    # enforced by MySQL rather than remembered by application code.
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )

    provider: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g. "google"

    # The provider's own stable id for this user — Google's `sub` claim.
    # Not the email: emails can change, `sub` cannot.
    provider_account_id: Mapped[str] = mapped_column(String(255), nullable=False)

    user: Mapped["User"] = relationship(back_populates="oauth_accounts")  # noqa: F821

    def __repr__(self) -> str:
        return f"<OAuthAccount provider={self.provider!r} user_id={self.user_id}>"
