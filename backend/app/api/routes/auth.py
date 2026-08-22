"""Authentication endpoints.

This layer does one job: translate between HTTP and the service layer. All
security decisions live in app/services/auth/ and app/core/security.py.
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import CurrentUser, DbSession
from app.core.config import settings
from app.core.rate_limit import login_rate_limit, signup_rate_limit
from app.schemas.auth import (
    GoogleAuthRequest,
    LoginRequest,
    SignupRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth.auth_service import (
    AuthService,
    EmailAlreadyRegisteredError,
    InactiveUserError,
    InvalidCredentialsError,
)
from app.services.auth.google_service import (
    GoogleAuthError,
    GoogleNotConfiguredError,
    GoogleService,
)

router = APIRouter(prefix="/auth", tags=["auth"])

INVALID_CREDENTIALS = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Incorrect email or password",
)


def _token_response(service: AuthService, user) -> TokenResponse:
    token, expires_in = service.issue_token(user)
    return TokenResponse(
        access_token=token,
        expires_in=expires_in,
        user=UserResponse.model_validate(user),
    )


@router.post(
    "/signup",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(signup_rate_limit)],
)
def signup(payload: SignupRequest, db: DbSession) -> TokenResponse:
    """Register with email and password, then log straight in."""
    service = AuthService(db)
    try:
        user = service.signup(
            name=payload.name, email=payload.email, password=payload.password
        )
    except EmailAlreadyRegisteredError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        ) from None
    return _token_response(service, user)


@router.post("/login", response_model=TokenResponse, dependencies=[Depends(login_rate_limit)])
def login(payload: LoginRequest, db: DbSession) -> TokenResponse:
    service = AuthService(db)
    try:
        user = service.login(email=payload.email, password=payload.password)
    except InvalidCredentialsError:
        # Same message whether the email is unknown or the password is wrong —
        # see AuthService.login for why.
        raise INVALID_CREDENTIALS from None
    except InactiveUserError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="This account is inactive"
        ) from None
    return _token_response(service, user)


@router.post("/google", response_model=TokenResponse, dependencies=[Depends(login_rate_limit)])
def google_auth(payload: GoogleAuthRequest, db: DbSession) -> TokenResponse:
    """Exchange a Google authorization code for one of OUR access tokens.

    The response is deliberately identical in shape to /login: however a user
    authenticates, the rest of the application deals with one token format.
    """
    try:
        user = GoogleService(db).authenticate(payload.code)
    except GoogleNotConfiguredError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google sign-in is not configured on this server",
        ) from None
    except GoogleAuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)
        ) from None
    return _token_response(AuthService(db), user)


@router.get("/me", response_model=UserResponse)
def read_current_user(user: CurrentUser) -> UserResponse:
    """Who am I? Used by the frontend to restore a session on page load."""
    return UserResponse.model_validate(user)


@router.get("/providers", tags=["auth"])
def available_providers() -> dict:
    """Lets the frontend hide the Google button when it isn't configured.

    Only the CLIENT_ID is exposed — it is public by design. The secret stays
    on the server.
    """
    return {
        "password": True,
        "google": settings.google_oauth_configured,
        "google_client_id": settings.GOOGLE_CLIENT_ID or None,
    }
