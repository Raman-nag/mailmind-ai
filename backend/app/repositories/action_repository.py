from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.action import Action, ActionPriority, ActionStatus, ActionType


class ActionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, action: Action) -> Action:
        self.db.add(action)
        self.db.commit()
        self.db.refresh(action)
        return action

    def get_by_id(
        self,
        action_id: str,
        user_id: str
    ) -> Action | None:
        stmt = select(Action).where(
            Action.id == action_id,
            Action.user_id == user_id
        )

        return self.db.scalar(stmt)

    def get_active_by_user_id(
        self,
        user_id: str
    ) -> list[Action]:
        stmt = (
            select(Action)
            .where(
                Action.user_id == user_id,
                Action.status.in_(
                    [
                        ActionStatus.PENDING,
                        ActionStatus.IN_PROGRESS
                    ]
                )
            )
            .order_by(
                Action.due_date.asc().nullslast(),
                Action.created_at.desc()
            )
        )

        return list(self.db.scalars(stmt).all())

    def get_pending_by_user_id(
        self,
        user_id: str
    ) -> list[Action]:
        stmt = (
            select(Action)
            .where(
                Action.user_id == user_id,
                Action.status == ActionStatus.PENDING
            )
            .order_by(
                Action.due_date.asc().nullslast(),
                Action.created_at.desc()
            )
        )

        return list(self.db.scalars(stmt).all())

    def get_today_by_user_id(
        self,
        user_id: str,
        start_at: datetime,
        end_at: datetime
    ) -> list[Action]:
        stmt = (
            select(Action)
            .where(
                Action.user_id == user_id,
                Action.status.in_(
                    [
                        ActionStatus.PENDING,
                        ActionStatus.IN_PROGRESS
                    ]
                ),
                Action.due_date >= start_at,
                Action.due_date < end_at
            )
            .order_by(
                Action.priority.desc(),
                Action.due_date.asc()
            )
        )

        return list(self.db.scalars(stmt).all())

    def get_upcoming_by_user_id(
        self,
        user_id: str,
        start_at: datetime,
        end_at: datetime
    ) -> list[Action]:
        stmt = (
            select(Action)
            .where(
                Action.user_id == user_id,
                Action.status.in_(
                    [
                        ActionStatus.PENDING,
                        ActionStatus.IN_PROGRESS
                    ]
                ),
                Action.due_date >= start_at,
                Action.due_date <= end_at
            )
            .order_by(
                Action.due_date.asc(),
                Action.priority.desc()
            )
        )

        return list(self.db.scalars(stmt).all())

    def get_overdue_by_user_id(
        self,
        user_id: str,
        before_at: datetime
    ) -> list[Action]:
        stmt = (
            select(Action)
            .where(
                Action.user_id == user_id,
                Action.status.in_(
                    [
                        ActionStatus.PENDING,
                        ActionStatus.IN_PROGRESS
                    ]
                ),
                Action.due_date < before_at
            )
            .order_by(
                Action.due_date.asc(),
                Action.priority.desc()
            )
        )

        return list(self.db.scalars(stmt).all())

    def get_due_soon_by_user_id(
        self,
        user_id: str,
        start_at: datetime,
        end_at: datetime
    ) -> list[Action]:
        return self.get_upcoming_by_user_id(
            user_id=user_id,
            start_at=start_at,
            end_at=end_at
        )

    def get_critical_by_user_id(
        self,
        user_id: str
    ) -> list[Action]:
        stmt = (
            select(Action)
            .where(
                Action.user_id == user_id,
                Action.status.in_(
                    [
                        ActionStatus.PENDING,
                        ActionStatus.IN_PROGRESS
                    ]
                ),
                Action.priority.in_(
                    [
                        ActionPriority.HIGH,
                        ActionPriority.CRITICAL
                    ]
                )
            )
            .order_by(
                Action.priority.desc(),
                Action.due_date.asc().nullslast(),
                Action.created_at.desc()
            )
        )

        return list(self.db.scalars(stmt).all())

    def get_pending_replies_by_user_id(
        self,
        user_id: str
    ) -> list[Action]:
        stmt = (
            select(Action)
            .where(
                Action.user_id == user_id,
                Action.status.in_(
                    [
                        ActionStatus.PENDING,
                        ActionStatus.IN_PROGRESS
                    ]
                ),
                Action.action_type == ActionType.FOLLOW_UP
            )
            .order_by(
                Action.due_date.asc().nullslast(),
                Action.created_at.desc()
            )
        )

        return list(self.db.scalars(stmt).all())

    def get_by_email_id(
        self,
        email_id: str
    ) -> list[Action]:
        stmt = (
            select(Action)
            .where(Action.email_id == email_id)
            .order_by(Action.created_at.desc())
        )

        return list(self.db.scalars(stmt).all())

    def update(self, action: Action) -> Action:
        self.db.commit()
        self.db.refresh(action)
        return action
