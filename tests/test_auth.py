from fastapi.testclient import TestClient
from app.config import settings

def test_require_admin_missing_token(client: TestClient):
    response = client.post("/api/admin/articles", json={"title": "Test", "content": {}})
    assert response.status_code == 401

def test_require_admin_invalid_token(client: TestClient):
    response = client.post(
        "/api/admin/articles",
        json={"title": "Test", "content": {}},
        headers={"Authorization": "Bearer wrong-token"},
    )
    assert response.status_code == 403

def test_require_admin_valid_token(client: TestClient):
    response = client.post(
        "/api/admin/articles",
        json={"title": "Test", "content": {}, "status": "draft"},
        headers={"Authorization": f"Bearer {settings.ADMIN_API_TOKEN}"},
    )
    # 200 because body is complete now
    assert response.status_code == 200
