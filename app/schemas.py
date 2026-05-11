from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, field_validator

class ArticleCreate(BaseModel):
    title: str
    content: dict
    description: Optional[str] = None
    send_newsletter: bool = True
    scheduled_for: Optional[datetime] = None
    tag_names: List[str] = []

    @field_validator("tag_names")
    @classmethod
    def max_eight_tags(cls, v: List[str]) -> List[str]:
        if len(v) > 8:
            raise ValueError("Maximum 8 tags allowed")
        return v

class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[dict] = None
    description: Optional[str] = None
    status: Optional[str] = None
    send_newsletter: Optional[bool] = None
    scheduled_for: Optional[datetime] = None
    tag_names: Optional[List[str]] = None

    @field_validator("tag_names")
    @classmethod
    def max_eight_tags(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is not None and len(v) > 8:
            raise ValueError("Maximum 8 tags allowed")
        return v

class ArticleAutoSave(BaseModel):
    title: Optional[str] = None
    content: Optional[dict] = None
    description: Optional[str] = None
    tag_names: Optional[List[str]] = None

    @field_validator("tag_names")
    @classmethod
    def max_eight_tags(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is not None and len(v) > 8:
            raise ValueError("Maximum 8 tags allowed")
        return v

class SubscribeRequest(BaseModel):
    email: str

class LoginRequest(BaseModel):
    email: str
    password: str

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class TagRead(BaseModel):
    id: str
    name: str
    slug: str

    @field_validator("id", mode="before")
    @classmethod
    def uuid_to_str(cls, v):
        return str(v) if v is not None else v

    class Config:
        from_attributes = True

class RevisionListRead(BaseModel):
    version_number: int
    change_type: str
    title: str
    created_at: datetime

    class Config:
        from_attributes = True

class RevisionRead(BaseModel):
    version_number: int
    change_type: str
    title: str
    content: dict
    description: Optional[str] = None
    tag_names: List[str]
    created_at: datetime

    class Config:
        from_attributes = True

class ImportSuccessItem(BaseModel):
    id: str
    title: str
    slug: str

class ImportErrorItem(BaseModel):
    filename: str
    error: str

class ImportResult(BaseModel):
    successes: List[ImportSuccessItem]
    errors: List[ImportErrorItem]
    total: int
