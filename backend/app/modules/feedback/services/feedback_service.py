from datetime import datetime

from app.models.user import User
from app.modules.feedback.models.feedback import Feedback
from app.modules.feedback.repositories.feedback_repository import FeedbackRepository
from app.modules.feedback.schemas.feedback import FeedbackCreate


class FeedbackService:
    def __init__(
        self,
        repository: FeedbackRepository
    ):
        self.repository = repository

    def submit_feedback(
        self,
        user: User,
        feedback_data: FeedbackCreate
    ) -> Feedback:
        if user.feedback_submitted:
            raise ValueError("Feedback already submitted")

        now = datetime.utcnow()
        feedback_text = feedback_data.feedback_text.strip()

        if not feedback_text:
            raise ValueError("Feedback text is required")

        feedback = Feedback(
            user_id=user.id,
            rating=feedback_data.rating,
            feedback_text=feedback_text,
            submitted_at=now,
            created_at=now,
            updated_at=now
        )

        user.feedback_submitted = True
        return self.repository.create(feedback)

    def get_my_feedback(
        self,
        user_id: str
    ) -> Feedback | None:
        return self.repository.get_by_user_id(user_id)
