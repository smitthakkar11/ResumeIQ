"""Google Sign-In via the OAuth 2.0 authorization code flow.

    browser ──code──► us ──code + client_id + client_secret──► Google
                                                                  │
    our JWT ◄── find-or-create user ◄── verified id_token ◄────────┘

The code exchange happens here, on the server, because it needs
GOOGLE_CLIENT_SECRET — a value that must never reach the browser.
"""

import httpx
import jwt
from jwt import PyJWKClient
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.auth.auth_service import AuthError

GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_JWKS_URL = "https://www.googleapis.com/oauth2/v3/certs"
GOOGLE_ISSUERS = ("https://accounts.google.com", "accounts.google.com")
PROVIDER = "google"


class GoogleAuthError(AuthError):
    pass


class GoogleNotConfiguredError(AuthError):
    pass


class GoogleService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.users = UserRepository(db)
        # Cached so we don't refetch Google's public keys on every login.
        self._jwk_client = PyJWKClient(GOOGLE_JWKS_URL, cache_keys=True)

    # ---------------------------------------------------------------

    def authenticate(self, code: str) -> User:
        if not settings.google_oauth_configured:
            raise GoogleNotConfiguredError

        id_token = self._exchange_code_for_id_token(code)
        claims = self._verify_id_token(id_token)
        return self._find_or_create_user(claims)

    # ---------------------------------------------------------------

    def _exchange_code_for_id_token(self, code: str) -> str:
        """Redeem the one-time code. This is the step that needs the secret."""
        try:
            response = httpx.post(
                GOOGLE_TOKEN_URL,
                data={
                    "code": code,
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                    "grant_type": "authorization_code",
                },
                timeout=10.0,
            )
        except httpx.HTTPError as exc:
            raise GoogleAuthError("Could not reach Google's token endpoint") from exc

        if response.status_code != 200:
            raise GoogleAuthError("Google rejected the authorization code")

        id_token = response.json().get("id_token")
        if not id_token:
            raise GoogleAuthError("Google's response contained no id_token")
        return id_token

    def _verify_id_token(self, id_token: str) -> dict:
        """Verify Google's signature and the claims that matter.

        `audience` is not optional paranoia: without it, an id_token minted for
        a DIFFERENT application would verify fine (Google signed it, after
        all) and let its holder log in here as that user.
        """
        try:
            signing_key = self._jwk_client.get_signing_key_from_jwt(id_token)
            claims = jwt.decode(
                id_token,
                signing_key.key,
                algorithms=["RS256"],
                audience=settings.GOOGLE_CLIENT_ID,
                issuer=GOOGLE_ISSUERS,
            )
        except (InvalidTokenError, Exception) as exc:  # noqa: BLE001
            raise GoogleAuthError("Could not verify Google's id_token") from exc

        if not claims.get("email_verified", False):
            # An unverified email would let someone claim an address they do
            # not control, and thereby link to an existing local account.
            raise GoogleAuthError("Google account email is not verified")
        if not claims.get("sub") or not claims.get("email"):
            raise GoogleAuthError("Google's id_token is missing required claims")

        return claims

    def _find_or_create_user(self, claims: dict) -> User:
        """Resolve the Google identity to a local user, in priority order."""
        google_sub = claims["sub"]
        email = claims["email"].strip().lower()

        # 1. Already linked — the normal returning-user path. Matched on
        #    Google's stable `sub`, never on email, which can change.
        user = self.users.get_by_oauth_account(PROVIDER, google_sub)
        if user is not None:
            return user

        # 2. A local account already owns this email. Link it. This is safe
        #    only because we checked email_verified above; otherwise it would
        #    be an account-takeover vector.
        user = self.users.get_by_email(email)
        if user is not None:
            self.users.link_oauth_account(
                user=user, provider=PROVIDER, provider_account_id=google_sub
            )
            return user

        # 3. Brand-new user. password_hash stays NULL — there is no password
        #    to set, which is exactly why that column is nullable.
        user = self.users.create(
            name=claims.get("name") or email.split("@")[0],
            email=email,
            password_hash=None,
        )
        self.users.link_oauth_account(
            user=user, provider=PROVIDER, provider_account_id=google_sub
        )
        return user
