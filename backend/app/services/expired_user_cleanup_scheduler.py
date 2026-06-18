import asyncio
from contextlib import suppress

from app.core.logging import get_logger
from app.db.session import SessionLocal
from app.services.cleanup_service import CleanupService
from app.services.expiry_service import ExpiryService


logger = get_logger("mailmind.scheduler")


class ExpiredUserCleanupScheduler:
    def __init__(
        self,
        interval_seconds: int = 3600
    ):
        self.interval_seconds = interval_seconds
        self._task: asyncio.Task | None = None

    def start(self) -> None:
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._run())
            logger.info(
                "Expired user cleanup scheduler started interval_seconds=%s",
                self.interval_seconds
            )

    async def stop(self) -> None:
        if self._task is None:
            return

        self._task.cancel()

        with suppress(asyncio.CancelledError):
            await self._task

        logger.info("Expired user cleanup scheduler stopped")

    async def _run(self) -> None:
        while True:
            await self.run_once()
            await asyncio.sleep(self.interval_seconds)

    async def run_once(self) -> None:
        db = SessionLocal()

        try:
            expired_users = ExpiryService.get_expired_users(db)

            for user in expired_users:
                user_id = user.id
                ExpiryService.mark_user_expired(user)
                db.commit()
                logger.info(
                    "Marked user expired user_id=%s",
                    user_id
                )

            cleanup_eligible_users = (
                ExpiryService.get_cleanup_eligible_users(db)
            )
            cleanup_eligible_user_ids = [
                user.id
                for user in cleanup_eligible_users
            ]
            db.commit()

            for user_id in cleanup_eligible_user_ids:
                CleanupService.cleanup_user_data(
                    db,
                    user_id
                )

        except Exception:
            db.rollback()
            logger.exception("Expired user cleanup scheduler failed")
        finally:
            db.close()
