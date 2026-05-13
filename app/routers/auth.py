import time
import secrets
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.database import get_session
from app.models.user import User
from app.schemas import LoginRequest, ForgotPasswordRequest, ResetPasswordRequest, SetupRequest
from app.services.auth_service import verify_password, create_access_token, generate_reset_token, validate_reset_token, reset_password, pwd_context
from app.services.email_service import send_password_reset_email, send_verification_email
from app.dependencies import require_role
from app.services.user_management_service import validate_setup_token, complete_setup

router = APIRouter(prefix="/api/auth", tags=["auth"])

# In-memory cooldown: email -> last_request_timestamp
_forgot_password_cooldown: dict[str, float] = {}
_verification_cooldown: dict[str, float] = {}
COOLDOWN_SECONDS = 60

@router.post("/login")
def login(request: LoginRequest, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == request.email)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated",
        )
    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token = create_access_token(data={"sub": str(user.id), "token_version": user.token_version})
    return {"token": access_token, "type": "bearer"}

@router.get("/me")
def get_me(user: User = Depends(require_role(["admin", "editor", "contributor"]))):
    return {
        "id": str(user.id),
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "created_at": user.created_at,
    }

@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, session: Session = Depends(get_session)):
    email = request.email.lower().strip()
    
    # Check cooldown
    now = time.time()
    last_request = _forgot_password_cooldown.get(email)
    if last_request and (now - last_request) < COOLDOWN_SECONDS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Please wait before requesting another reset link.",
        )
    
    user = session.exec(select(User).where(User.email == email)).first()
    
    if user:
        plaintext_token = generate_reset_token(user, session)
        send_password_reset_email(user.email, plaintext_token)
    
    # Always update cooldown regardless of whether email exists
    _forgot_password_cooldown[email] = now
    
    return {"message": "If an account exists with that email, a reset link has been sent"}

@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest, session: Session = Depends(get_session)):
    user = validate_reset_token(request.token, session)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token.",
        )

    from app.services.auth_service import reset_password as do_reset_password
    do_reset_password(user, request.new_password, session)

    return {"message": "Password reset successfully."}

@router.post("/setup")
def setup_account(request: SetupRequest, session: Session = Depends(get_session)):
    user = validate_setup_token(request.token, session)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired setup token.",
        )

    complete_setup(user, request.password, session)

    return {"message": "Account setup successfully."}


class VerifyEmailRequest:
    token: str

class ResendVerificationRequest:
    email: str


@router.post("/verify-email")
def verify_email(request: dict, session: Session = Depends(get_session)):
    token = request.get("token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token is required.",
        )

    # Find user with matching verification token - query only users with non-null tokens
    users_with_tokens = session.exec(
        select(User).where(User.verification_token_hash.isnot(None))
    ).all()
    matched_user = None
    for user in users_with_tokens:
        if user.verification_token_expires_at is None:
            continue
        if user.is_verified:
            continue
        expires_at = user.verification_token_expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < datetime.now(timezone.utc):
            continue
        if pwd_context.verify(token, user.verification_token_hash):
            matched_user = user
            break

    if matched_user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token.",
        )

    # Mark as verified and clear token
    matched_user.is_verified = True
    matched_user.verification_token_hash = None
    matched_user.verification_token_expires_at = None
    session.add(matched_user)
    session.commit()

    # Generate JWT for immediate login
    access_token = create_access_token(
        data={"sub": str(matched_user.id), "token_version": matched_user.token_version}
    )
    return {"token": access_token, "type": "bearer"}


@router.post("/resend-verification")
def resend_verification(request: dict, session: Session = Depends(get_session)):
    email = request.get("email", "").lower().strip()
    
    # Check cooldown
    now = time.time()
    last_request = _verification_cooldown.get(email)
    if last_request and (now - last_request) < COOLDOWN_SECONDS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Please wait before requesting another verification email.",
        )
    
    user = session.exec(select(User).where(User.email == email)).first()
    
    if user and not user.is_verified:
        # Generate new verification token
        plaintext = secrets.token_urlsafe(32)
        hashed = pwd_context.hash(plaintext)
        user.verification_token_hash = hashed
        user.verification_token_expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
        session.add(user)
        session.commit()
        
        send_verification_email(user.email, plaintext)
    
    # Always update cooldown (no enumeration)
    _verification_cooldown[email] = now
    
    return {"message": "If an unverified account exists with that email, a verification link has been sent"}
