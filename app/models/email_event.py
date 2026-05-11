import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlmodel import SQLModel, Field, Column, JSON

class EmailEvent(SQLModel, table=True):
    __tablename__ = "email_events"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    newsletter_send_id: uuid.UUID = Field(foreign_key="newsletter_sends.id", nullable=False, index=True)
    event_type: str = Field(nullable=False)  # open, click, bounce, delivered, etc.
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
    raw_payload: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
