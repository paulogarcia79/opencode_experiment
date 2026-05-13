import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from app.models.user import User
from app.services.auth_service import verify_password


@pytest.fixture(autouse=True)
def _clear_cooldowns():
    """Reset registration cooldown between tests."""
    from app.routers.auth import _registration_cooldown
    _registration_cooldown.clear()


def test_register_success_creates_contributor(client: TestClient, session: Session):
    """Successful registration creates a user with contributor role, returns token."""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "SecurePass1",
            "confirm_password": "SecurePass1",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert data["type"] == "bearer"

    # Verify user was created with correct attributes
    user = session.exec(select(User).where(User.email == "newuser@example.com")).first()
    assert user is not None
    assert user.role == "contributor"
    assert user.is_verified is False
    assert user.is_active is True
    assert verify_password("SecurePass1", user.hashed_password)


def test_register_returns_registration_new_header(client: TestClient, session: Session):
    """Fresh registration returns X-Registration-New: true header."""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "fresh@example.com",
            "password": "SecurePass1",
            "confirm_password": "SecurePass1",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("X-Registration-New") == "true"


def test_register_password_mismatch(client: TestClient, session: Session):
    """Registration with mismatched confirm_password returns 422."""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "mismatch@example.com",
            "password": "SecurePass1",
            "confirm_password": "DifferentPass1",
        },
    )
    assert response.status_code == 422


def test_register_weak_password_too_short(client: TestClient, session: Session):
    """Password shorter than 8 characters returns 422."""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "short@example.com",
            "password": "Ab1",
            "confirm_password": "Ab1",
        },
    )
    assert response.status_code == 422


def test_register_weak_password_no_uppercase(client: TestClient, session: Session):
    """Password without uppercase returns 422."""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "noupper@example.com",
            "password": "alllowercase1",
            "confirm_password": "alllowercase1",
        },
    )
    assert response.status_code == 422


def test_register_weak_password_no_lowercase(client: TestClient, session: Session):
    """Password without lowercase returns 422."""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "nolower@example.com",
            "password": "ALLUPPERCASE1",
            "confirm_password": "ALLUPPERCASE1",
        },
    )
    assert response.status_code == 422


def test_register_weak_password_no_digit(client: TestClient, session: Session):
    """Password without digit returns 422."""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "nodigit@example.com",
            "password": "NoDigitHere",
            "confirm_password": "NoDigitHere",
        },
    )
    assert response.status_code == 422


def test_register_duplicate_email_silent(client: TestClient, session: Session):
    """Registering an already-registered email returns 200 with no token."""
    # First registration
    client.post(
        "/api/auth/register",
        json={
            "email": "dupe@example.com",
            "password": "SecurePass1",
            "confirm_password": "SecurePass1",
        },
    )

    # Second registration — same email
    response = client.post(
        "/api/auth/register",
        json={
            "email": "dupe@example.com",
            "password": "SecurePass1",
            "confirm_password": "SecurePass1",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "token" not in data
    assert "detail" in data


def test_register_ip_cooldown(client: TestClient, session: Session):
    """Two rapid registrations from the same client trigger a 429 cooldown."""
    # First registration
    response1 = client.post(
        "/api/auth/register",
        json={
            "email": "first@example.com",
            "password": "SecurePass1",
            "confirm_password": "SecurePass1",
        },
    )
    assert response1.status_code == 200

    # Second registration — same IP, too soon
    response2 = client.post(
        "/api/auth/register",
        json={
            "email": "second@example.com",
            "password": "SecurePass1",
            "confirm_password": "SecurePass1",
        },
    )
    assert response2.status_code == 429


def test_register_authenticated_rejected(client: TestClient, session: Session):
    """An already-authenticated user cannot register — returns 400."""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "authed@example.com",
            "password": "SecurePass1",
            "confirm_password": "SecurePass1",
        },
    )
    assert response.status_code == 200
    token = response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Try to register while logged in
    response = client.post(
        "/api/auth/register",
        headers=headers,
        json={
            "email": "another@example.com",
            "password": "SecurePass1",
            "confirm_password": "SecurePass1",
        },
    )
    assert response.status_code == 400


def test_register_generates_verification_token(client: TestClient, session: Session):
    """Registration generates a verification token hash on the user."""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "verify@example.com",
            "password": "SecurePass1",
            "confirm_password": "SecurePass1",
        },
    )
    assert response.status_code == 200

    user = session.exec(select(User).where(User.email == "verify@example.com")).first()
    assert user is not None
    assert user.verification_token_hash is not None
    assert user.verification_token_expires_at is not None
    assert user.is_verified is False
