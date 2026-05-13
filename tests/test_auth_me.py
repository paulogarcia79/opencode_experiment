import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from app.config import settings
from app.models.user import User
from app.services.auth_service import create_access_token, get_password_hash


def create_user(session: Session, email: str, role: str = "admin", is_verified: bool = True, is_active: bool = True) -> User:
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


def test_me_returns_user_profile(client: TestClient, session: Session):
    user = create_user(session, "editor@example.com", role="editor")
    headers = get_token_headers(user)

    response = client.get("/api/auth/me", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(user.id)
    assert data["email"] == "editor@example.com"
    assert data["role"] == "editor"
    assert data["is_active"] is True
    assert data["is_verified"] is True
    assert "created_at" in data


def test_me_unauthenticated_returns_401(client: TestClient):
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_me_invalid_token_returns_401(client: TestClient):
    headers = {"Authorization": "Bearer invalidtoken"}
    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == 401


def test_me_inactive_user_returns_401(client: TestClient, session: Session):
    user = create_user(session, "inactive@example.com", is_active=False)
    headers = get_token_headers(user)

    response = client.get("/api/auth/me", headers=headers)

    assert response.status_code == 401
    assert "deactivated" in response.json()["detail"].lower()


def test_me_unverified_user_returns_200(client: TestClient, session: Session):
    user = create_user(session, "unverified@example.com", is_verified=False)
    headers = get_token_headers(user)

    response = client.get("/api/auth/me", headers=headers)

    assert response.status_code == 200
    assert response.json()["is_verified"] is False


def test_me_admin_role(client: TestClient, session: Session):
    user = create_user(session, "admin2@example.com", role="admin")
    headers = get_token_headers(user)

    response = client.get("/api/auth/me", headers=headers)

    assert response.status_code == 200
    assert response.json()["role"] == "admin"


def test_me_contributor_role(client: TestClient, session: Session):
    user = create_user(session, "contributor@example.com", role="contributor")
    headers = get_token_headers(user)

    response = client.get("/api/auth/me", headers=headers)

    assert response.status_code == 200
    assert response.json()["role"] == "contributor"
