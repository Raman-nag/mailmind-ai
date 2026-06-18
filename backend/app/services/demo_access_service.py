from datetime import datetime
from datetime import timedelta

from sqlalchemy.orm import Session

from app.models.user import User


MAX_ACTIVE_USERS = 20


class DemoAccessService:

    @staticmethod
    def get_active_demo_users_count(
        db: Session
    ) -> int:
        now = datetime.utcnow()

        return (
            db.query(User)
            .filter(User.is_active.is_(True))
            .filter(User.is_demo_expired.is_(False))
            .filter(User.expires_at.isnot(None))
            .filter(User.expires_at > now)
            .count()
        )

    @staticmethod
    def can_register_new_user(
        db: Session
    ) -> bool:
        return (
            DemoAccessService.get_active_demo_users_count(db)
            < MAX_ACTIVE_USERS
        )

    @staticmethod
    def initialize_demo_period(
        user: User
    ) -> User:
        now = datetime.utcnow()
        user.demo_started_at = now
        user.expires_at = now + timedelta(hours=48)
        user.is_demo_expired = False
        return user
