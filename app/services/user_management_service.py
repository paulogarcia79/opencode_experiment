import secrets
from datetime import datetime, timedelta, timezone
from sqlmodel import Session, select
from app.models.user import User
from app.services.auth_service import pwd_context, get_password_hash

SETUP_TOKEN_EXPIRY_HOURS = 24
VALID_ROLES = {"admin", "editor", "contributor"}


def generate_setup_token(user: User, session: Session) -> str:
    plaintext = secrets.token_urlsafe(32)
    hashed = pwd_context.hash(plaintext)
    user.setup_token_hash = hashed
    user.setup_token_expires_at = datetime.now(timezone.utc) + timedelta(hours=SETUP_TOKEN_EXPIRY_HOURS)
    session.add(user)
    session.commit()
    return plaintext


def validate_setup_token(token: str, session: Session) -> User | None:
    users_with_tokens = session.exec(
        select(User).where(User.setup_token_hash.isnot(None))
    ).all()

    for user in users_with_tokens:
        if user.setup_token_expires_at is None:
            continue
        expires_at = user.setup_token_expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < datetime.now(timezone.utc):
            continue
        if pwd_context.verify(token, user.setup_token_hash):
            return user
    return None


def complete_setup(user: User, password: str, session: Session) -> None:
    user.hashed_password = get_password_hash(password)
    user.is_verified = True
    user.setup_token_hash = None
    user.setup_token_expires_at = None
    session.add(user)
    session.commit()


def create_invited_user(email: str, role: str, session: Session) -> User:
    unusable_password = pwd_context.hash(secrets.token_urlsafe(32))
    user = User(
        email=email.lower().strip(),
        hashed_password=unusable_password,
        role=role,
        is_active=True,
        is_verified=False,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def update_user_role(user: User, role: str, session: Session) -> None:
    user.role = role
    session.add(user)
    session.commit()


def toggle_user_active(user: User, is_active: bool, session: Session) -> None:
    user.is_active = is_active
    session.add(user)
    session.commit()
