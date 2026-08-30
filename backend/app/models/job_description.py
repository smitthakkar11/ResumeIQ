from typing import Any

from sqlalchemy import JSON, ForeignKey, Index, String
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base, TimestampMixin


class JobDescription(Base, TimestampMixin):
    __tablename__ = "job_descriptions"
    # Analysing the same posting against three resume versions should reuse one
    # row. We match on a hash because a LONGTEXT column cannot be usefully
    # indexed for equality.
    __table_args__ = (Index("ix_jobs_user_hash", "user_id", "content_hash"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False, default="")
    description: Mapped[str] = mapped_column(LONGTEXT, nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)

    # Supplied by the user; used by application tracking.
    company: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    # Extracted from the text by jd_parser, not typed by the user.
    role: Mapped[str] = mapped_column(String(160), nullable=False, default="")
    # required/preferred skills, soft skills, education, experience. JSON
    # because we only ever read it back whole to render one page.
    parsed: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
