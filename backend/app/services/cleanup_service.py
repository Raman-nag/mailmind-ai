from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.models.action import Action
from app.models.email import Email
from app.models.gmail_account import GmailAccount
from app.models.gmail_token import GmailToken
from app.models.memory import Memory
from app.models.user import User
from app.modules.feedback.models.feedback import Feedback
from app.rag.vector_service import VectorService


logger = get_logger("mailmind.cleanup")


class CleanupService:
    chroma_retry_attempts = 3

    @staticmethod
    def cleanup_user_data(
        db: Session,
        user: User | str
    ) -> dict[str, int | bool]:
        user_id = user if isinstance(user, str) else user.id
        deleted_counts: dict[str, int | bool] = {}

        try:
            with db.begin():
                deleted_counts["actions"] = (
                    db.query(Action)
                    .filter(Action.user_id == user_id)
                    .delete(synchronize_session=False)
                )
                deleted_counts["memories"] = (
                    db.query(Memory)
                    .filter(Memory.user_id == user_id)
                    .delete(synchronize_session=False)
                )
                deleted_counts["emails"] = (
                    db.query(Email)
                    .filter(Email.user_id == user_id)
                    .delete(synchronize_session=False)
                )
                deleted_counts["gmail_tokens"] = (
                    db.query(GmailToken)
                    .filter(GmailToken.user_id == user_id)
                    .delete(synchronize_session=False)
                )
                deleted_counts["gmail_accounts"] = (
                    db.query(GmailAccount)
                    .filter(GmailAccount.user_id == user_id)
                    .delete(synchronize_session=False)
                )

                deleted_counts["chroma_cleanup"] = (
                    CleanupService._delete_chroma_vectors(user_id)
                )

                deleted_counts["feedback"] = (
                    db.query(Feedback)
                    .filter(Feedback.user_id == user_id)
                    .delete(synchronize_session=False)
                )
                deleted_counts["users"] = (
                    db.query(User)
                    .filter(User.id == user_id)
                    .delete(synchronize_session=False)
                )

            logger.info(
                "Cleanup completed user_id=%s result=%s",
                user_id,
                deleted_counts
            )
            return deleted_counts

        except Exception:
            db.rollback()
            logger.exception(
                "Cleanup failed and database transaction rolled back user_id=%s",
                user_id
            )
            raise

    @staticmethod
    def _delete_chroma_vectors(
        user_id: str
    ) -> bool:
        for attempt in range(1, CleanupService.chroma_retry_attempts + 1):
            try:
                VectorService.delete_user_vectors(user_id)
                return True
            except Exception:
                logger.exception(
                    "Chroma cleanup failed user_id=%s attempt=%s",
                    user_id,
                    attempt
                )

        logger.error(
            "Chroma cleanup exhausted retries user_id=%s",
            user_id
        )
        return False
