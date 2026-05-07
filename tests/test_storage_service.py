import os
import pytest
from pathlib import Path
from app.services.storage_service import LocalFileSystemStorage
from app.config import settings

class TestLocalFileSystemStorage:
    def test_save_file_creates_directory_structure(self, tmp_path):
        storage = LocalFileSystemStorage(base_dir=str(tmp_path / "uploads"))
        result = storage.save(b"test content", "photo.jpg", "image/jpeg")
        
        assert result["size_bytes"] == 12
        assert result["url"].startswith("/uploads/")
        assert "photo.jpg" in result["storage_path"]
        
        # Verify file exists
        full_path = storage.get_full_path(result["storage_path"])
        assert full_path.exists()
        assert full_path.read_bytes() == b"test content"
    
    def test_save_generates_unique_filenames(self, tmp_path):
        storage = LocalFileSystemStorage(base_dir=str(tmp_path / "uploads"))
        result1 = storage.save(b"content1", "photo.jpg", "image/jpeg")
        result2 = storage.save(b"content2", "photo.jpg", "image/jpeg")
        
        assert result1["storage_path"] != result2["storage_path"]
        assert result1["url"] != result2["url"]
    
    def test_delete_removes_file(self, tmp_path):
        storage = LocalFileSystemStorage(base_dir=str(tmp_path / "uploads"))
        result = storage.save(b"test", "photo.jpg", "image/jpeg")
        
        assert storage.delete(result["storage_path"]) is True
        assert not storage.get_full_path(result["storage_path"]).exists()
    
    def test_delete_nonexistent_returns_false(self, tmp_path):
        storage = LocalFileSystemStorage(base_dir=str(tmp_path / "uploads"))
        assert storage.delete("nonexistent/path.jpg") is False
    
    def test_year_month_directory_layout(self, tmp_path):
        storage = LocalFileSystemStorage(base_dir=str(tmp_path / "uploads"))
        result = storage.save(b"test", "photo.jpg", "image/jpeg")
        
        parts = result["storage_path"].split("/")
        # Should be: YYYY/MM/uuid_photo.jpg
        assert len(parts) == 3
        assert parts[0].isdigit() and len(parts[0]) == 4  # year
        assert parts[1].isdigit() and len(parts[1]) == 2  # month
    
    def test_url_format(self, tmp_path):
        storage = LocalFileSystemStorage(base_dir=str(tmp_path / "uploads"))
        result = storage.save(b"test", "photo.jpg", "image/jpeg")
        
        assert result["url"].startswith("/uploads/")
        assert result["url"].endswith("photo.jpg")
