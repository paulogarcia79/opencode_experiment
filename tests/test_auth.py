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
