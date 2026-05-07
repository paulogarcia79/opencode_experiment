import io
from fastapi.testclient import TestClient
from app.config import settings
from app.models.image_asset import ImageAsset

AUTH_HEADER = {"Authorization": f"Bearer {settings.ADMIN_API_TOKEN}"}


class TestImageUpload:
    def test_upload_valid_image(self, client: TestClient, session):
        file_content = b"\x89PNG\r\n\x1a\n" + b"fake png data"
        response = client.post(
            "/api/admin/images",
            files={"file": ("test.png", io.BytesIO(file_content), "image/png")},
            headers=AUTH_HEADER,
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["url"].startswith("/uploads/")
        assert data["original_name"] == "test.png"
        assert data["mime_type"] == "image/png"
        assert data["size_bytes"] == len(file_content)

    def test_upload_unauthorized(self, client: TestClient):
        response = client.post(
            "/api/admin/images",
            files={"file": ("test.png", io.BytesIO(b"fake"), "image/png")},
        )
        assert response.status_code == 401

    def test_upload_invalid_mime_type(self, client: TestClient):
        response = client.post(
            "/api/admin/images",
            files={"file": ("test.txt", io.BytesIO(b"not an image"), "text/plain")},
            headers=AUTH_HEADER,
        )
        assert response.status_code == 400
        assert "Invalid file type" in response.json()["detail"]

    def test_upload_invalid_extension(self, client: TestClient):
        response = client.post(
            "/api/admin/images",
            files={"file": ("test.exe", io.BytesIO(b"fake"), "image/png")},
            headers=AUTH_HEADER,
        )
        assert response.status_code == 400
        assert "Invalid file extension" in response.json()["detail"]

    def test_upload_file_too_large(self, client: TestClient):
        # Create a file larger than MAX_UPLOAD_SIZE_MB
        large_content = b"x" * (settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024 + 1)
        response = client.post(
            "/api/admin/images",
            files={"file": ("large.png", io.BytesIO(large_content), "image/png")},
            headers=AUTH_HEADER,
        )
        assert response.status_code == 400
        assert "too large" in response.json()["detail"].lower()

    def test_upload_creates_db_record(self, client: TestClient, session):
        import uuid
        file_content = b"\x89PNG\r\n\x1a\n" + b"fake png data"
        response = client.post(
            "/api/admin/images",
            files={"file": ("test.png", io.BytesIO(file_content), "image/png")},
            headers=AUTH_HEADER,
        )
        assert response.status_code == 200
        data = response.json()

        # Verify DB record exists
        image = session.get(ImageAsset, uuid.UUID(data["id"]))
        assert image is not None
        assert image.original_name == "test.png"
        assert image.mime_type == "image/png"

    def test_upload_allowed_types(self, client: TestClient):
        """Test that all allowed image types are accepted."""
        allowed_types = [
            ("test.jpg", b"\xff\xd8\xff fake jpg", "image/jpeg"),
            ("test.jpeg", b"\xff\xd8\xff fake jpg", "image/jpeg"),
            ("test.png", b"\x89PNG\r\n\x1a\n fake", "image/png"),
            ("test.gif", b"GIF89a fake", "image/gif"),
            ("test.webp", b"RIFF fake webp", "image/webp"),
        ]

        for filename, content, mime in allowed_types:
            response = client.post(
                "/api/admin/images",
                files={"file": (filename, io.BytesIO(content), mime)},
                headers=AUTH_HEADER,
            )
            assert response.status_code == 200, f"Failed for {filename}: {response.text}"
