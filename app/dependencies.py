from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings

security = HTTPBearer()

def require_admin(credentials: HTTPAuthorizationCredentials = Depends(security)) -> None:
    """Verify the request includes the correct admin bearer token."""
    if credentials.credentials != settings.ADMIN_API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing admin token",
        )
