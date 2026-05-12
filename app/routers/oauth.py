import uuid
from urllib.parse import urlencode
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlmodel import Session, select
from starlette.datastructures import URL
from app.database import get_session
from app.config import settings
from app.models.user import User
from app.models.user_oauth_provider import UserOAuthProvider
from app.services.oauth_service import OAuthService, SUPPORTED_PROVIDERS
from app.services.auth_service import create_access_token, get_password_hash
from app.services.email_service import send_verification_email
import secrets
import redis.asyncio as aioredis

router = APIRouter(prefix="/api/auth/oauth", tags=["auth"])

# In-memory state store for CSRF protection: state -> redirect_uri
_oauth_states: dict[str, str] = {}

OAUTH_CODE_TTL_SECONDS = 300  # 5 minutes


def _get_redis() -> aioredis.Redis:
    return aioredis.from_url(settings.REDIS_URL)


class OAuthExchangeRequest(BaseModel):
    code: str


class OAuthHandler:
    def __init__(self, session: Session):
        self.session = session
        self.service = OAuthService()

    async def _authorize_redirect(self, request: Request, redirect_uri: str) -> RedirectResponse:
        provider = request.path_params["provider"]
        if provider not in SUPPORTED_PROVIDERS:
            raise HTTPException(status_code=404, detail="Provider not found")

        url, state = self.service.get_authorization_url(provider, redirect_uri)
        _oauth_states[state] = redirect_uri
        return RedirectResponse(url=url, status_code=307)

    async def _exchange_code(self, request: Request, provider: str, redirect_uri: str) -> dict:
        """Exchange authorization code for access token using authlib."""
        client = self.service.oauth.create_client(provider)
        if client is None:
            raise HTTPException(status_code=500, detail=f"Provider {provider} not configured")

        code = request.query_params.get("code")
        token = await client.fetch_access_token(code=code, redirect_uri=redirect_uri)
        return token

    async def _fetch_userinfo(self, token: dict, provider: str) -> dict:
        """Fetch user info from the OAuth provider."""
        import httpx
        if "userinfo" in token:
            return token["userinfo"]
        # For Google, fetch from userinfo endpoint using access token
        if provider == "google" and "access_token" in token:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://openidconnect.googleapis.com/v1/userinfo",
                    headers={"Authorization": f"Bearer {token['access_token']}"}
                )
                if resp.status_code == 200:
                    return resp.json()
        # For GitHub, fetch from API
        if provider == "github" and "access_token" in token:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://api.github.com/user",
                    headers={"Authorization": f"Bearer {token['access_token']}", "Accept": "application/vnd.github.v3+json"}
                )
                if resp.status_code == 200:
                    user_data = resp.json()
                    # Fetch primary email
                    email_resp = await client.get(
                        "https://api.github.com/user/emails",
                        headers={"Authorization": f"Bearer {token['access_token']}", "Accept": "application/vnd.github.v3+json"}
                    )
                    if email_resp.status_code == 200:
                        emails = email_resp.json()
                        primary = next((e for e in emails if e.get("primary")), emails[0] if emails else {})
                        user_data["email"] = primary.get("email")
                        user_data["email_verified"] = primary.get("verified", False)
                    return user_data
        # Fallback: decode ID token for Google with signature verification
        if provider == "google" and "id_token" in token:
            import jwt
            from jwt import PyJWKClient
            id_token = token["id_token"]
            # Fetch Google's public keys to verify the signature
            jwks_client = PyJWKClient("https://www.googleapis.com/oauth2/v3/certs")
            signing_key = jwks_client.get_signing_key_from_jwt(id_token)
            return jwt.decode(
                id_token,
                signing_key.key,
                algorithms=["RS256"],
                audience=settings.GOOGLE_CLIENT_ID,
            )
        return token


@router.get("/{provider}")
async def oauth_initiate(request: Request, session: Session = Depends(get_session)):
    provider = request.path_params["provider"]
    if provider not in SUPPORTED_PROVIDERS:
        raise HTTPException(status_code=404, detail="Provider not found")

    handler = OAuthHandler(session)
    try:
        callback_url = f"{request.url.scheme}://{request.url.netloc}/api/auth/oauth/{provider}/callback"
        return await handler._authorize_redirect(request, callback_url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{provider}/callback")
async def oauth_callback(request: Request, session: Session = Depends(get_session)):
    provider = request.path_params["provider"]
    if provider not in SUPPORTED_PROVIDERS:
        raise HTTPException(status_code=404, detail="Provider not found")

    code = request.query_params.get("code")
    state = request.query_params.get("state")
    if not code or not state:
        raise HTTPException(status_code=400, detail="Missing code or state parameter")

    redirect_uri = _oauth_states.pop(state, None)
    if not redirect_uri:
        raise HTTPException(status_code=400, detail="Invalid state parameter")

    handler = OAuthHandler(session)

    # Check if this is a settings connect callback
    if redirect_uri.startswith("settings-callback:"):
        _, user_id_str, expected_provider = redirect_uri.split(":")
        user_id = uuid.UUID(user_id_str)

        if provider != expected_provider:
            raise HTTPException(status_code=400, detail="Provider mismatch")

        token = await handler._exchange_code(request, provider, f"{request.url.scheme}://{request.url.netloc}/api/auth/oauth/{provider}/callback")
        user_info = await handler._fetch_userinfo(token, provider)
        extracted = handler.service.extract_user_info(provider, user_info)

        oauth_provider = UserOAuthProvider(
            user_id=user_id,
            provider=provider,
            provider_user_id=extracted["provider_user_id"],
        )
        session.add(oauth_provider)
        session.commit()

        return RedirectResponse(url=f"{settings.APP_BASE_URL}/admin/settings?connected={provider}", status_code=302)

    token = await handler._exchange_code(request, provider, f"{request.url.scheme}://{request.url.netloc}/api/auth/oauth/{provider}/callback")
    user_info = await handler._fetch_userinfo(token, provider)

    extracted = handler.service.extract_user_info(provider, user_info)
    email = extracted.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="Email not provided by OAuth provider")

    # Look up existing user by email
    existing_user = session.exec(select(User).where(User.email == email.lower())).first()

    if existing_user:
        # Auto-link: create OAuth provider record if not exists
        existing_provider = session.exec(
            select(UserOAuthProvider).where(
                UserOAuthProvider.user_id == existing_user.id,
                UserOAuthProvider.provider == provider,
            )
        ).first()
        if not existing_provider:
            oauth_provider = UserOAuthProvider(
                user_id=existing_user.id,
                provider=provider,
                provider_user_id=extracted["provider_user_id"],
            )
            session.add(oauth_provider)
            session.commit()

        # Generate JWT and store in Redis as one-time code
        jwt_token = create_access_token(
            data={"sub": str(existing_user.id), "token_version": existing_user.token_version}
        )
        oauth_code = secrets.token_urlsafe(32)
        redis_conn = _get_redis()
        await redis_conn.setex(f"oauth_code:{oauth_code}", OAUTH_CODE_TTL_SECONDS, jwt_token)
        await redis_conn.aclose()

        frontend_url = f"{settings.APP_BASE_URL}/admin/login?oauth_code={oauth_code}"
        return RedirectResponse(url=frontend_url, status_code=302)
    else:
        # Create new user
        new_user = User(
            id=uuid.uuid4(),
            email=email.lower(),
            hashed_password="oauth-only:" + get_password_hash(secrets.token_urlsafe(32)),
            is_verified=False,
        )
        session.add(new_user)
        session.flush()

        # Create OAuth provider record
        oauth_provider = UserOAuthProvider(
            user_id=new_user.id,
            provider=provider,
            provider_user_id=extracted["provider_user_id"],
        )
        session.add(oauth_provider)

        # Send verification email
        _send_verification(new_user, session)
        session.commit()

        # Redirect to verify-email page
        verify_url = f"{settings.APP_BASE_URL}/admin/verify-email?email={email}"
        return RedirectResponse(url=verify_url, status_code=302)


def _send_verification(user: User, session: Session) -> None:
    """Generate verification token and send email."""
    from datetime import datetime, timedelta, timezone
    from app.services.auth_service import pwd_context

    plaintext = secrets.token_urlsafe(32)
    hashed = pwd_context.hash(plaintext)
    user.verification_token_hash = hashed
    user.verification_token_expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
    session.add(user)

    send_verification_email(user.email, plaintext)


@router.post("/exchange")
async def oauth_exchange(request: OAuthExchangeRequest):
    """Exchange a one-time OAuth code for a JWT token.

    The code is single-use and expires after 5 minutes.
    """
    redis_conn = _get_redis()
    key = f"oauth_code:{request.code}"
    jwt_token = await redis_conn.get(key)
    if not jwt_token:
        await redis_conn.aclose()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OAuth code",
        )

    # Delete the code immediately (single-use)
    await redis_conn.delete(key)
    await redis_conn.aclose()

    return {"token": jwt_token.decode() if isinstance(jwt_token, bytes) else jwt_token, "type": "bearer"}
