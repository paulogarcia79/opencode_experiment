import os
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from app.config import settings

class LocalFileSystemStorage:
    """File storage service using local filesystem with year/month directory layout."""

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = Path(base_dir or settings.UPLOAD_DIR)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _generate_path(self, filename: str) -> Path:
        """Generate a storage path with year/month directory layout."""
        now = datetime.now(timezone.utc)
        dir_path = self.base_dir / str(now.year) / f"{now.month:02d}"
        dir_path.mkdir(parents=True, exist_ok=True)
        # Use UUID prefix to avoid collisions
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        return dir_path / unique_name

    def _relative_path(self, full_path: Path) -> str:
        """Get the relative path from the base directory."""
        return str(full_path.relative_to(self.base_dir))

    def save(self, file_bytes: bytes, filename: str, mime_type: str) -> dict:
        """Save a file to storage and return metadata.
        
        Returns dict with:
            - storage_path: relative path from uploads dir
            - url: public URL path
            - size_bytes: file size
        """
        file_path = self._generate_path(filename)
        file_path.write_bytes(file_bytes)
        
        relative = self._relative_path(file_path)
        return {
            "storage_path": relative,
            "url": f"/uploads/{relative}",
            "size_bytes": len(file_bytes),
        }

    def delete(self, storage_path: str) -> bool:
        """Delete a file from storage. Returns True if deleted, False if not found."""
        file_path = self.base_dir / storage_path
        if file_path.exists():
            file_path.unlink()
            # Clean up empty parent directories
            self._cleanup_empty_dirs(file_path.parent)
            return True
        return False

    def _cleanup_empty_dirs(self, dir_path: Path) -> None:
        """Remove empty parent directories up to base_dir."""
        try:
            for parent in dir_path.parents:
                if parent == self.base_dir:
                    break
                if parent.exists() and not any(parent.iterdir()):
                    parent.rmdir()
        except OSError:
            pass  # Directory not empty or permission issue

    def get_full_path(self, storage_path: str) -> Path:
        """Get the full filesystem path for a stored file."""
        return self.base_dir / storage_path

# Global storage instance
storage = LocalFileSystemStorage()
