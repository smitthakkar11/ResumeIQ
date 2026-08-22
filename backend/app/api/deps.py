"""Shared FastAPI dependencies.

Right now this only re-exports the database session. In Phase 2 it grows a
`get_current_user` dependency, which is what every protected endpoint will
depend on to enforce authentication and ownership.
"""

from app.db.session import get_db

__all__ = ["get_db"]
