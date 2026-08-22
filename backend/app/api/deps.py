"""Shared FastAPI dependencies.

`get_current_user` is the single gate every protected endpoint passes through.
Because it is a dependency, adding it to a route's signature is the entire
opt-in — there is no middleware doing path-prefix matching that someone can
forget to update when adding a route.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User
from app.repositories.user_repository import UserRepository

# auto_error=False so we can raise our own 401 with a WWW-Authenticate header
# rather than FastAPI's default 403 for a missing credential.
bearer_scheme = HTTPBearer(auto_error=False)

CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Resolve `Authorization: Bearer <token>` to a live User row.

    The database lookup is deliberate. The token alone proves the id was valid
    *when the token was issued*; the user may since have been deleted or
    deactivated. Trusting the JWT payload without this check is how deactivated
    accounts keep working for another hour.
    """
    if credentials is None or not credentials.credentials:
        raise CREDENTIALS_EXCEPTION

    user_id = decode_access_token(credentials.credentials)
    if user_id is None:
        raise CREDENTIALS_EXCEPTION

    user = UserRepository(db).get_by_id(user_id)
    if user is None:
        raise CREDENTIALS_EXCEPTION
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account is inactive",
        )

    return user


# Convenience aliases so routes read as `user: CurrentUser` instead of a
# three-line Annotated[...] signature.
CurrentUser = Annotated[User, Depends(get_current_user)]
DbSession = Annotated[Session, Depends(get_db)]

__all__ = ["CurrentUser", "DbSession", "get_current_user", "get_db"]
