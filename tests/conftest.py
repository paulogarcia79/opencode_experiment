import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool
from unittest.mock import AsyncMock
from app.main import app
from app.database import get_session
from app.services.seed_service import seed_default_admin

from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

@pytest.fixture(autouse=True)
def setup_cache():
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")
    yield
    # No clear method on InMemoryBackend or no await needed

@pytest.fixture(name="arq_pool")
def arq_pool_fixture():
    mock = AsyncMock()
    app.state.arq_pool = mock
    return mock

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        seed_default_admin(session)
        yield session

@pytest.fixture(name="client")
def client_fixture(session: Session, arq_pool):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    # Reset rate limiter state between tests
    from app.limiter import limiter
    limiter.reset()

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

@pytest.fixture(name="admin_token")
def admin_token_fixture(session: Session) -> dict:
    from app.models.user import User
    from sqlmodel import select
    from app.services.auth_service import create_access_token
    admin = session.exec(select(User)).first()
    token = create_access_token(data={"sub": str(admin.id), "token_version": admin.token_version})
    return {"Authorization": f"Bearer {token}"}


def create_user(session: Session, email: str, role: str = "contributor", is_active: bool = True, is_verified: bool = True) -> "User":
    """Create a test user and return it."""
    from app.models.user import User
    from app.services.auth_service import get_password_hash
    user = User(
        email=email,
        hashed_password=get_password_hash("test-password"),
        role=role,
        is_active=is_active,
        is_verified=is_verified,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def create_user_token(session: Session, email: str, role: str = "contributor") -> dict:
    """Create a test user and return auth headers."""
    from app.services.auth_service import create_access_token
    user = create_user(session, email, role)
    token = create_access_token(data={"sub": str(user.id), "token_version": user.token_version})
    return {"Authorization": f"Bearer {token}"}


def get_token_for_user(user: "User") -> dict:
    """Return auth headers for an existing user."""
    from app.services.auth_service import create_access_token
    token = create_access_token(data={"sub": str(user.id), "token_version": user.token_version})
    return {"Authorization": f"Bearer {token}"}
