import jwt
import secrets
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=8)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm="HS256")
    return encoded_jwt

RESET_TOKEN_EXPIRY_MINUTES = 15

def generate_reset_token(user, session) -> str:
    """Generate a password reset token, store its hash on the user, return plaintext."""
    from sqlmodel import Session
    
    plaintext = secrets.token_urlsafe(32)
    hashed = pwd_context.hash(plaintext)
    user.reset_token_hash = hashed
    user.reset_token_expires_at = datetime.now(timezone.utc) + timedelta(minutes=RESET_TOKEN_EXPIRY_MINUTES)
    session.add(user)
    session.commit()
    return plaintext

def validate_reset_token(token: str, session):
    """Validate a reset token against the stored hash. Returns the user or None."""
    from sqlmodel import Session, select
    from app.models.user import User
    
    users = session.exec(select(User)).all()
    for user in users:
        if user.reset_token_hash is None:
            continue
        if user.reset_token_expires_at is None:
            continue
        # Handle both naive and aware datetimes for SQLite compatibility
        expires_at = user.reset_token_expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < datetime.now(timezone.utc):
            continue
        if pwd_context.verify(token, user.reset_token_hash):
            return user
    return None

def reset_password(user, new_password: str, session):
    """Reset user's password, increment token_version, invalidate all reset tokens."""
    from sqlmodel import Session
    
    user.hashed_password = get_password_hash(new_password)
    user.token_version += 1
    user.reset_token_hash = None
    user.reset_token_expires_at = None
    session.add(user)
    session.commit()
