from datetime import datetime
from pydantic import BaseModel


class EmailCreate(BaseModel):
    sender: str
    subject: str
    body: str
    gmail_message_id: str
    received_at: datetime


class EmailResponse(BaseModel):
    id: str
    sender: str
    subject: str
    body: str
    summary: str | None
    received_at: datetime

    class Config:
        from_attributes = True