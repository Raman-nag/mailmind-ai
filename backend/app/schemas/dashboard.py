from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_emails: int
    summarized_emails: int
    pending_summaries: int