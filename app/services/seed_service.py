import uuid
from sqlmodel import Session, select
from app.config import settings
from app.models.user import User
from app.services.auth_service import get_password_hash

def seed_default_admin(session: Session) -> None:
    """Create a default admin user if no users exist in the database."""
    existing = session.exec(select(User)).first()
    if existing:
        return
    
    admin = User(
        id=uuid.uuid4(),
        email=settings.ADMIN_EMAIL,
        hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
        is_admin=True,
        is_verified=True,
    )
    session.add(admin)
    session.commit()
    print(f"[startup] Seeded default admin user: {settings.ADMIN_EMAIL}")
