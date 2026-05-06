from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.database import get_session
from app.schemas import SubscribeRequest
from app.services.subscriber_service import (
    create_subscriber,
    confirm_subscriber,
    unsubscribe_subscriber,
)

router = APIRouter()

@router.post("/api/subscribers")
def subscribe_endpoint(data: SubscribeRequest, session: Session = Depends(get_session)):
    subscriber = create_subscriber(session, data.email)
    return {"message": "Check your email to confirm your subscription."}

@router.get("/api/subscribers/confirm")
def confirm_endpoint(token: str, session: Session = Depends(get_session)):
    subscriber = confirm_subscriber(session, token)
    if not subscriber:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired confirmation link.")
    return {"message": "Your subscription has been confirmed!"}

@router.get("/api/subscribers/unsubscribe")
def unsubscribe_endpoint(token: str, session: Session = Depends(get_session)):
    subscriber = unsubscribe_subscriber(session, token)
    if not subscriber:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid unsubscribe link.")
    return {"message": "You have been unsubscribed."}
