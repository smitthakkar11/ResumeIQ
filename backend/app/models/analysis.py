from typing import Any

from sqlalchemy import JSON, Float, ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base, TimestampMixin


class Analysis(Base, TimestampMixin):
    """An immutable snapshot of one resume-vs-job comparison.

    Scores and skill lists are stored, not recomputed on read: the skill
    dictionary and scoring weights change over time, and a past result must not
    silently change with them.
    """

    __tablename__ = "analyses"
    # Serves "my analyses, newest first" — filter and sort from one index.
    __table_args__ = (Index("ix_analyses_user_created", "user_id", "created_at"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )

    # SET NULL, not CASCADE: deleting a resume should not punch holes in the
    # user's history. The snapshot below stays readable without it.
    resume_id: Mapped[int | None] = mapped_column(
        ForeignKey("resumes.id", ondelete="SET NULL"), nullable=True
    )
    job_description_id: Mapped[int | None] = mapped_column(
        ForeignKey("job_descriptions.id", ondelete="SET NULL"), nullable=True
    )

    # Denormalised so history stays readable after a resume is deleted.
    resume_filename: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    job_title: Mapped[str] = mapped_column(String(200), nullable=False, default="")

    match_score: Mapped[float] = mapped_column(Float, nullable=False)
    text_similarity: Mapped[float] = mapped_column(Float, nullable=False)
    skill_match: Mapped[float | None] = mapped_column(Float, nullable=True)
    keyword_match: Mapped[float] = mapped_column(Float, nullable=False)

    # JSON rather than three more tables: we only ever read these back whole to
    # render one page, never query into them. Normalise what you query,
    # serialise what you only display.
    weights: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    matched_skills: Mapped[list[Any]] = mapped_column(JSON, nullable=False, default=list)
    missing_skills: Mapped[list[Any]] = mapped_column(JSON, nullable=False, default=list)
    extra_skills: Mapped[list[Any]] = mapped_column(JSON, nullable=False, default=list)
    keywords: Mapped[list[Any]] = mapped_column(JSON, nullable=False, default=list)
    sections: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    recommendations: Mapped[list[Any]] = mapped_column(JSON, nullable=False, default=list)
