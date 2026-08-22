"""Single import surface for Alembic.

Alembic's autogenerate compares `Base.metadata` against the live database. A
model class only registers itself in that metadata when its module is imported,
so every model must be imported here — otherwise Alembic will happily generate a
migration that DROPs a table it simply never learned about.
"""

from app.db.base_class import Base  # noqa: F401
from app.models.oauth_account import OAuthAccount  # noqa: F401
from app.models.user import User  # noqa: F401

__all__ = ["Base", "OAuthAccount", "User"]
