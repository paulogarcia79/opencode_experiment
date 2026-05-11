import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from app.config import settings

def test_login_success(client: TestClient, session: Session):
    response = client.post(
        "/api/auth/login",
        json={"email": settings.ADMIN_EMAIL, "password": settings.ADMIN_PASSWORD}
    )
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["type"] == "bearer"

def test_login_invalid_email(client: TestClient, session: Session):
    response = client.post(
        "/api/auth/login",
        json={"email": "wrong@example.com", "password": settings.ADMIN_PASSWORD}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"

def test_login_invalid_password(client: TestClient, session: Session):
    response = client.post(
        "/api/auth/login",
        json={"email": settings.ADMIN_EMAIL, "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"

def test_stale_token_version_rejected(client: TestClient, session: Session):
    from app.models.user import User
    from sqlmodel import select
    from app.services.auth_service import create_access_token

    admin = session.exec(select(User)).first()
    # Increment token_version to invalidate existing tokens
    admin.token_version += 1
    session.add(admin)
    session.commit()

    # Create a token with the OLD token_version (0)
    old_token = create_access_token(data={"sub": str(admin.id), "token_version": 0})
    headers = {"Authorization": f"Bearer {old_token}"}

    response = client.get("/api/admin/articles", headers=headers)
    assert response.status_code == 401
