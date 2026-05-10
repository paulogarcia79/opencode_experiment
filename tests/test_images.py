import io
import uuid
from fastapi.testclient import TestClient
from app.config import settings
from app.models.image_asset import ImageAsset



class TestImageUpload:
    def test_upload_valid_image(self, client: TestClient, session, admin_token):
        file_content = b"\x89PNG\r\n\x1a\n" + b"fake png data"
        response = client.post(
            "/api/admin/images",
            files={"file": ("test.png", io.BytesIO(file_content), "image/png")},
            headers=admin_token,
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["url"].startswith("/uploads/")
        assert data["original_name"] == "test.png"
        assert data["mime_type"] == "image/png"
        assert data["size_bytes"] == len(file_content)

    def test_upload_unauthorized(self, client: TestClient, admin_token):
        response = client.post(
            "/api/admin/images",
            files={"file": ("test.png", io.BytesIO(b"fake"), "image/png")},
        )
        assert response.status_code == 401

    def test_upload_invalid_mime_type(self, client: TestClient, admin_token):
        response = client.post(
            "/api/admin/images",
            files={"file": ("test.txt", io.BytesIO(b"not an image"), "text/plain")},
            headers=admin_token,
        )
        assert response.status_code == 400
        assert "Invalid file type" in response.json()["detail"]

    def test_upload_invalid_extension(self, client: TestClient, admin_token):
        response = client.post(
            "/api/admin/images",
            files={"file": ("test.exe", io.BytesIO(b"fake"), "image/png")},
            headers=admin_token,
        )
        assert response.status_code == 400
        assert "Invalid file extension" in response.json()["detail"]

    def test_upload_file_too_large(self, client: TestClient, admin_token):
        # Create a file larger than MAX_UPLOAD_SIZE_MB
        large_content = b"x" * (settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024 + 1)
        response = client.post(
            "/api/admin/images",
            files={"file": ("large.png", io.BytesIO(large_content), "image/png")},
            headers=admin_token,
        )
        assert response.status_code == 400
        assert "too large" in response.json()["detail"].lower()

    def test_upload_creates_db_record(self, client: TestClient, session, admin_token):
        import uuid
        file_content = b"\x89PNG\r\n\x1a\n" + b"fake png data"
        response = client.post(
            "/api/admin/images",
            files={"file": ("test.png", io.BytesIO(file_content), "image/png")},
            headers=admin_token,
        )
        assert response.status_code == 200
        data = response.json()

        # Verify DB record exists
        image = session.get(ImageAsset, uuid.UUID(data["id"]))
        assert image is not None
        assert image.original_name == "test.png"
        assert image.mime_type == "image/png"

    def test_upload_allowed_types(self, client: TestClient, admin_token):
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
                headers=admin_token,
            )
            assert response.status_code == 200, f"Failed for {filename}: {response.text}"


class TestImageList:
    def test_list_images(self, client: TestClient, admin_token):
        # Upload a couple of images first
        for i in range(3):
            client.post(
                "/api/admin/images",
                files={"file": (f"test{i}.png", io.BytesIO(b"\x89PNG\r\n\x1a\n fake"), "image/png")},
                headers=admin_token,
            )
        
        response = client.get("/api/admin/images", headers=admin_token)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert data[0]["original_name"].startswith("test")
        assert "id" in data[0]
        assert "url" in data[0]
        assert "created_at" in data[0]

    def test_list_images_pagination(self, client: TestClient, admin_token):
        # Upload 5 images
        for i in range(5):
            client.post(
                "/api/admin/images",
                files={"file": (f"test{i}.png", io.BytesIO(b"\x89PNG\r\n\x1a\n fake"), "image/png")},
                headers=admin_token,
            )
        
        response = client.get("/api/admin/images?limit=2", headers=admin_token)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2

    def test_list_images_unauthorized(self, client: TestClient, admin_token):
        response = client.get("/api/admin/images")
        assert response.status_code == 401


class TestImageDelete:
    def test_delete_image(self, client: TestClient, session, admin_token):
        # Upload an image
        upload_response = client.post(
            "/api/admin/images",
            files={"file": ("test.png", io.BytesIO(b"\x89PNG\r\n\x1a\n fake"), "image/png")},
            headers=admin_token,
        )
        assert upload_response.status_code == 200
        image_id = upload_response.json()["id"]

        # Delete it
        response = client.delete(f"/api/admin/images/{image_id}", headers=admin_token)
        assert response.status_code == 204

        # Verify it's gone
        image = session.get(ImageAsset, uuid.UUID(image_id))
        assert image is None

    def test_delete_image_not_found(self, client: TestClient, admin_token):
        response = client.delete(
            f"/api/admin/images/{uuid.uuid4()}",
            headers=admin_token,
        )
        assert response.status_code == 404

    def test_delete_image_unauthorized(self, client: TestClient, admin_token):
        response = client.delete(f"/api/admin/images/{uuid.uuid4()}")
        assert response.status_code == 401
