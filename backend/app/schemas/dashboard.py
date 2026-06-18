from datetime import datetime

from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_emails: int
    summarized_emails: int
    pending_summaries: int


class DashboardActionItem(BaseModel):
    id: str
    email_id: str
    action_type: str
    title: str
    description: str | None
    due_date: datetime | None = None
    status: str
    priority: str
    source_email_subject: str
    extraction_confidence: float
    metadata: dict


class DashboardEmailItem(BaseModel):
    id: str
    sender: str
    subject: str
    summary: str | None
    priority: str | None
    category: str | None
    deadline: datetime | None = None
    received_at: datetime


class DashboardRecommendation(BaseModel):
    title: str
    description: str
    reason: str
    action_ids: list[str]
    priority: str


class DashboardActionsResponse(BaseModel):
    count: int
    actions: list[DashboardActionItem]


class DashboardEmailsResponse(BaseModel):
    count: int
    emails: list[DashboardEmailItem]


class DashboardRecommendationsResponse(BaseModel):
    count: int
    recommendations: list[DashboardRecommendation]
    answer: str | None = None
