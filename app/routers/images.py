import uuid
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlmodel import Session
from app.database import get_session
from app.dependencies import require_admin
from app.models.image_asset import ImageAsset
from app.services.storage_service import storage
from app.config import settings

router = APIRouter()

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_SIZE_BYTES = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024

def validate_image_file(file: UploadFile) -> None:
    """Validate uploaded image file type and size."""
    # Check mime type
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed: {', '.join(settings.ALLOWED_IMAGE_TYPES)}"
        )
    
    # Check file extension
    filename = file.filename or ""
    ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file extension. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

@router.post("/api/admin/images", response_model=dict, dependencies=[Depends(require_admin)])
async def upload_image_endpoint(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
):
    """Upload an image file."""
    validate_image_file(file)
    
    # Read file content
    content = await file.read()
    
    # Check file size
    if len(content) > MAX_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE_MB}MB"
        )
    
    # Save to storage
    result = storage.save(content, file.filename or "unnamed", file.content_type or "application/octet-stream")
    
    # Create database record
    image_asset = ImageAsset(
        filename=result["storage_path"].split("/")[-1],
        original_name=file.filename or "unnamed",
        mime_type=file.content_type or "application/octet-stream",
        size_bytes=result["size_bytes"],
        storage_path=result["storage_path"],
        url=result["url"],
    )
    session.add(image_asset)
    session.commit()
    session.refresh(image_asset)
    
    return {
        "id": str(image_asset.id),
        "url": image_asset.url,
        "original_name": image_asset.original_name,
        "size_bytes": image_asset.size_bytes,
        "mime_type": image_asset.mime_type,
    }
