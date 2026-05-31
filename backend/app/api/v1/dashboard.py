from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.dashboard import DashboardStats
from app.services.email_service import EmailService

router = APIRouter()


@router.get(
    "/stats",
    response_model=DashboardStats
)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return EmailService.get_dashboard_stats(
        db=db,
        user_id=current_user.id
    )