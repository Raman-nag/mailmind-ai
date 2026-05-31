from pydantic import BaseModel
from datetime import datetime


class GmailTokenResponse(BaseModel):
    access_token: str
    refresh_token: str | None = None
    expiry: datetime | None = None