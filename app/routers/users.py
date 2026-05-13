import time
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.database import get_session
from app.models.user import User
from app.schemas import UserRead, InviteRequest, RoleUpdateRequest, ActiveUpdateRequest
from app.dependencies import require_role
from app.services.user_management_service import (
    generate_setup_token,
    create_invited_user,
    update_user_role,
    toggle_user_active,
    VALID_ROLES,
)
from app.services.email_service import send_invite_email

router = APIRouter(prefix="/api/admin/users", tags=["users"])

_invite_cooldown: dict[str, float] = {}
INVITE_COOLDOWN_SECONDS = 60


@router.get("/", response_model=list[UserRead])
def list_users(
    session: Session = Depends(get_session),
    _admin: User = Depends(require_role(["admin"])),
):
    users = session.exec(select(User).order_by(User.created_at.desc())).all()
    return [
        UserRead(
            id=str(u.id),
            email=u.email,
            role=u.role,
            is_active=u.is_active,
            is_verified=u.is_verified,
            created_at=u.created_at,
        )
        for u in users
    ]


@router.post("/invite")
def invite_user(
    request: InviteRequest,
    session: Session = Depends(get_session),
    _admin: User = Depends(require_role(["admin"])),
):
    email = request.email.lower().strip()

    now = time.time()
    last_request = _invite_cooldown.get(email)
    if last_request and (now - last_request) < INVITE_COOLDOWN_SECONDS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Please wait before sending another invite.",
        )

    if request.role not in VALID_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(VALID_ROLES)}",
        )

    existing = session.exec(select(User).where(User.email == email)).first()
    if existing:
        existing.role = request.role
        existing.is_verified = False
        session.add(existing)
        session.commit()
        plaintext_token = generate_setup_token(existing, session)
        send_invite_email(email, plaintext_token, request.role)
        _invite_cooldown[email] = now
        return {"message": f"Invite sent to existing user: {email}"}

    user = create_invited_user(email, request.role, session)
    plaintext_token = generate_setup_token(user, session)
    send_invite_email(email, plaintext_token, request.role)

    _invite_cooldown[email] = now

    return {"message": f"Invite sent to {email}"}


@router.put("/{user_id}/role")
def update_role(
    user_id: uuid.UUID,
    request: RoleUpdateRequest,
    session: Session = Depends(get_session),
    _admin: User = Depends(require_role(["admin"])),
):
    if request.role not in VALID_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(VALID_ROLES)}",
        )

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    update_user_role(user, request.role, session)
    return {"message": f"Role updated to {request.role}"}


@router.put("/{user_id}/active")
def toggle_active(
    user_id: uuid.UUID,
    request: ActiveUpdateRequest,
    session: Session = Depends(get_session),
    _admin: User = Depends(require_role(["admin"])),
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    toggle_user_active(user, request.is_active, session)
    status_msg = "activated" if request.is_active else "deactivated"
    return {"message": f"User {status_msg}"}
