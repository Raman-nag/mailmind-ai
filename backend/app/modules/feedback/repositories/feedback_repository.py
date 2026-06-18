from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.feedback.models.feedback import Feedback


class FeedbackRepository:
    def __init__(
        self,
        db: Session
    ):
        self.db = db

    def create(
        self,
        feedback: Feedback
    ) -> Feedback:
        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)
        return feedback

    def get_by_user_id(
        self,
        user_id: str
    ) -> Feedback | None:
        stmt = (
            select(Feedback)
            .where(Feedback.user_id == user_id)
            .order_by(Feedback.submitted_at.desc())
        )

        return self.db.scalar(stmt)
