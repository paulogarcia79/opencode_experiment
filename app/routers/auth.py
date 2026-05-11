import time
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.database import get_session
from app.models.user import User
from app.schemas import LoginRequest, ForgotPasswordRequest
from app.services.auth_service import verify_password, create_access_token, generate_reset_token, validate_reset_token, reset_password
from app.services.email_service import send_password_reset_email

router = APIRouter(prefix="/api/auth", tags=["auth"])

# In-memory cooldown: email -> last_request_timestamp
_forgot_password_cooldown: dict[str, float] = {}
COOLDOWN_SECONDS = 60

@router.post("/login")
def login(request: LoginRequest, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == request.email)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    
    access_token = create_access_token(data={"sub": str(user.id), "token_version": user.token_version})
    return {"token": access_token, "type": "bearer"}

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
