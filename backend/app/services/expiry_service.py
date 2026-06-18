from datetime import datetime
from datetime import timedelta

from sqlalchemy.orm import Session

from app.core.settings import settings
from app.models.user import User


class ExpiryService:

    @staticmethod
    def is_user_expired(
        user: User
    ) -> bool:
        if user.expires_at is None:
            return False

        return user.expires_at < datetime.utcnow()

    @staticmethod
    def mark_user_expired(
        user: User
    ) -> User:
        user.is_demo_expired = True

        if user.cleanup_after_at is None:
            user.cleanup_after_at = (
                datetime.utcnow()
                + timedelta(hours=settings.DEMO_CLEANUP_GRACE_HOURS)
            )

        return user

    @staticmethod
    def get_expired_users(
        db: Session
    ) -> list[User]:
        now = datetime.utcnow()

        return (
            db.query(User)
            .filter(User.expires_at.isnot(None))
            .filter(User.expires_at < now)
            .filter(User.is_demo_expired.is_(False))
            .all()
        )

    @staticmethod
    def get_cleanup_eligible_users(
        db: Session
    ) -> list[User]:
        now = datetime.utcnow()

        return (
            db.query(User)
            .filter(User.is_demo_expired.is_(True))
            .filter(
                (User.feedback_submitted.is_(True))
                | (
                    User.cleanup_after_at.isnot(None)
                    & (User.cleanup_after_at <= now)
                )
            )
            .all()
        )
