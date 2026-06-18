from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.modules.feedback.repositories.feedback_repository import FeedbackRepository
from app.modules.feedback.schemas.feedback import FeedbackCreate
from app.modules.feedback.schemas.feedback import FeedbackResponse
from app.modules.feedback.services.feedback_service import FeedbackService

router = APIRouter()


def get_feedback_service(
    db: Session = Depends(get_db)
) -> FeedbackService:
    repository = FeedbackRepository(db)
    return FeedbackService(repository)


@router.post(
    "",
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED
)
def submit_feedback(
    feedback_data: FeedbackCreate,
    current_user: User = Depends(get_current_user),
    service: FeedbackService = Depends(get_feedback_service)
):
    try:
        return service.submit_feedback(
            user=current_user,
            feedback_data=feedback_data
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc)
        )


@router.get(
    "/me",
    response_model=FeedbackResponse
)
def get_my_feedback(
    current_user: User = Depends(get_current_user),
    service: FeedbackService = Depends(get_feedback_service)
):
    feedback = service.get_my_feedback(
        user_id=current_user.id
    )

    if feedback is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Feedback not found"
        )

    return feedback
