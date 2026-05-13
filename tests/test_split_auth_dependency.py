import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from app.models.user import User
from app.services.auth_service import create_access_token, get_password_hash


def create_user(session: Session, email: str, role: str = "contributor", is_verified: bool = True, is_active: bool = True) -> User:
    user = User(
        email=email,
        hashed_password=get_password_hash("testpassword"),
        role=role,
        is_verified=is_verified,
        is_active=is_active,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def get_token_headers(user: User) -> dict:
    token = create_access_token(data={"sub": str(user.id), "token_version": user.token_version})
    return {"Authorization": f"Bearer {token}"}


def test_allow_unverified_accesses_me(client: TestClient, session: Session):
    """require_role_allow_unverified on /api/auth/me works for unverified users."""
    user = create_user(session, "unverified@example.com", is_verified=False)
    headers = get_token_headers(user)

    response = client.get("/api/auth/me", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "unverified@example.com"
    assert data["is_verified"] is False


def test_require_role_blocks_unverified_with_403(client: TestClient, session: Session):
    """require_role on a protected endpoint returns 403 for unverified users."""
    user = create_user(session, "unver@example.com", is_verified=False)
    headers = get_token_headers(user)

    response = client.get("/api/admin/images", headers=headers)

    assert response.status_code == 403
    assert "verified" in response.json()["detail"].lower()


def test_allow_unverified_accesses_settings(client: TestClient, session: Session):
    """require_role_allow_unverified on /api/admin/settings/accounts works for unverified."""
    user = create_user(session, "settings-unver@example.com", is_verified=False)
    headers = get_token_headers(user)

    response = client.get("/api/admin/settings/accounts", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "settings-unver@example.com"
    assert data["is_verified"] is False


def test_verified_user_me_still_works(client: TestClient, session: Session):
    """Verified users still access /api/auth/me normally."""
    user = create_user(session, "verified-me@example.com", is_verified=True)
    headers = get_token_headers(user)

    response = client.get("/api/auth/me", headers=headers)

    assert response.status_code == 200
    assert response.json()["is_verified"] is True


def test_verified_user_protected_still_works(client: TestClient, session: Session):
    """Verified users still access protected endpoints normally."""
    user = create_user(session, "verified-prot@example.com", is_verified=True, role="admin")
    headers = get_token_headers(user)

    response = client.get("/api/admin/images", headers=headers)

    assert response.status_code == 200


def test_unauthenticated_still_gets_401(client: TestClient):
    """Unauthenticated requests still get 401 (not 403)."""
    response = client.get("/api/auth/me")
    assert response.status_code == 401

    response = client.get("/api/admin/images")
    assert response.status_code == 401
