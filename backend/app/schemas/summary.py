from pydantic import BaseModel


class EmailSummaryRequest(BaseModel):
    email_content: str


class EmailSummaryResponse(BaseModel):
    summary: str