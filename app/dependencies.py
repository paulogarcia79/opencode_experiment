from fastapi import Request, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from arq.connections import ArqRedis
from app.config import settings
from app.database import get_session
from sqlmodel import Session, select
from app.models.user import User
import jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_arq_pool(request: Request) -> ArqRedis:
    return request.app.state.arq_pool

async def require_admin(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
) -> User:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
        import uuid
        user_id = uuid.UUID(user_id_str)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    
    user = session.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    
    jwt_token_version = payload.get("token_version")
    if jwt_token_version is not None and jwt_token_version != user.token_version:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    
    # In this system, any valid user is an admin for now based on the PRD
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not verified",
        )
    return user
