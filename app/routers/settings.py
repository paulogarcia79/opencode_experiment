from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select
from app.database import get_session
from app.dependencies import require_admin
from app.models.user import User
from app.models.user_oauth_provider import UserOAuthProvider
from app.services.oauth_service import OAuthService, SUPPORTED_PROVIDERS
from app.config import settings

router = APIRouter(prefix="/api/admin/settings", tags=["settings"], dependencies=[Depends(require_admin)])


@router.get("/accounts")
def get_connected_accounts(
    session: Session = Depends(get_session),
    user: User = Depends(require_admin),
):
    """Get user's connected OAuth accounts."""
    providers = session.exec(
        select(UserOAuthProvider).where(UserOAuthProvider.user_id == user.id)
    ).all()
    
    return {
        "email": user.email,
        "is_verified": user.is_verified,
        "connected_providers": [
            {"provider": p.provider, "connected_at": p.created_at.isoformat()}
            for p in providers
        ],
    }


@router.post("/accounts/oauth/{provider}")
async def connect_oauth(
    provider: str,
    request: Request,
    session: Session = Depends(get_session),
    user: User = Depends(require_admin),
):
    """Initiate OAuth connection for an existing user."""
    if provider not in SUPPORTED_PROVIDERS:
        raise HTTPException(status_code=404, detail="Provider not found")

    # Check if already connected
    existing = session.exec(
        select(UserOAuthProvider).where(
            UserOAuthProvider.user_id == user.id,
            UserOAuthProvider.provider == provider,
        )
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Already connected to {provider}")

    service = OAuthService()
    # Use the same callback URL as login — only one redirect URI needed per provider
    callback_url = f"{request.url.scheme}://{request.url.netloc}/api/auth/oauth/{provider}/callback"
    url, state = service.get_authorization_url(provider, callback_url)
    
    # Store state with user ID for callback linking
    from app.routers.oauth import _oauth_states
    _oauth_states[state] = f"settings-callback:{user.id}:{provider}"
    
    return {"authorization_url": url}


@router.delete("/accounts/oauth/{provider}")
def disconnect_oauth(
    provider: str,
    session: Session = Depends(get_session),
    user: User = Depends(require_admin),
):
    """Disconnect an OAuth provider from the user's account."""
    if provider not in SUPPORTED_PROVIDERS:
        raise HTTPException(status_code=404, detail="Provider not found")

    oauth_provider = session.exec(
        select(UserOAuthProvider).where(
            UserOAuthProvider.user_id == user.id,
            UserOAuthProvider.provider == provider,
        )
    ).first()
    if not oauth_provider:
        raise HTTPException(status_code=404, detail=f"Not connected to {provider}")

    # Check if this is the only login method
    all_providers = session.exec(
        select(UserOAuthProvider).where(UserOAuthProvider.user_id == user.id)
    ).all()
    has_password = user.hashed_password and not user.hashed_password.startswith("$2b$12$")  # Random unusable password check
    
    # A more reliable check: if the user has only this OAuth provider and no real password
    if len(all_providers) == 1 and not has_real_password(user):
        raise HTTPException(
            status_code=400,
            detail="Cannot disconnect your only login method. Set a password first.",
        )

    session.delete(oauth_provider)
    session.commit()
    return {"message": f"Disconnected from {provider}"}


def has_real_password(user: User) -> bool:
    """Check if user has a real password (not an OAuth-only marker)."""
    return not user.hashed_password.startswith("oauth-only:")
