from datetime import datetime

from sqlalchemy.orm import Session

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
