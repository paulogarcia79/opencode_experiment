from typing import Optional
from pydantic import BaseModel

class ArticleCreate(BaseModel):
    title: str
    content: dict
    description: Optional[str] = None
    send_newsletter: bool = True

class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[dict] = None
    description: Optional[str] = None
    status: Optional[str] = None
    send_newsletter: Optional[bool] = None

class SubscribeRequest(BaseModel):
    email: str
