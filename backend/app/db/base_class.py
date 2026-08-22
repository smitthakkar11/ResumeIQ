"""The SQLAlchemy declarative base every ORM model inherits from.

`Base.metadata` is the in-memory catalogue of all tables. Alembic reads exactly
this object to work out what the schema *should* look like, then diffs it
against what the live database actually has.
"""

from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    """Adds created_at / updated_at, maintained by the database itself.

    `server_default=func.now()` means MySQL fills the value, not Python, so rows
    inserted by a migration or a raw SQL script still get correct timestamps.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
