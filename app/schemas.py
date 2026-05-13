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

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and v not in ("draft", "published", "scheduled", "pending_review"):
            raise ValueError("Status must be one of: draft, published, scheduled, pending_review")
        return v

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


class ReviewRejectRequest(BaseModel):
    feedback: str

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
    model_config = {"from_attributes": True}

    id: str
    name: str
    slug: str

    @field_validator("id", mode="before")
    @classmethod
    def uuid_to_str(cls, v):
        return str(v) if v is not None else v

class RevisionListRead(BaseModel):
    model_config = {"from_attributes": True}

    version_number: int
    change_type: str
    title: str
    created_at: datetime
    author_email: Optional[str] = None

class RevisionRead(BaseModel):
    model_config = {"from_attributes": True}

    version_number: int
    change_type: str
    title: str
    content: dict
    description: Optional[str] = None
    tag_names: List[str]
    created_at: datetime
    author_email: Optional[str] = None

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

class UserRead(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    email: str
    role: str
    is_active: bool
    is_verified: bool
    created_at: datetime

    @field_validator("id", mode="before")
    @classmethod
    def uuid_to_str(cls, v):
        return str(v) if v is not None else v

class InviteRequest(BaseModel):
    email: str
    role: str

class RoleUpdateRequest(BaseModel):
    role: str

class ActiveUpdateRequest(BaseModel):
    is_active: bool

class SetupRequest(BaseModel):
    token: str
    password: str

class ArticleReassignRequest(BaseModel):
    author_id: str
