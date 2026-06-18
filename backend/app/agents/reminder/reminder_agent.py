from datetime import datetime, timedelta

from app.agents.action.action_agent import ActionAgent
from app.agents.base.agent import BaseAgent
from app.agents.base.context import AgentContext
from app.agents.base.result import AgentResult
from app.repositories.action_repository import ActionRepository


class ReminderAgent(BaseAgent):

    @staticmethod
    def execute(
        context: AgentContext
    ) -> AgentResult:

        db = context.payload.get(
            "db"
        )
        user_id = context.payload.get(
            "user_id"
        )
        mode = context.payload.get(
            "mode",
            "upcoming"
        )
        days = context.payload.get(
            "days",
            7
        )

        if not db:

            return AgentResult(
                success=False,
                data={},
                message="Database session is required"
            )

        if not user_id:

            return AgentResult(
                success=False,
                data={},
                message="User ID is required"
            )

        repository = ActionRepository(db)
        now = datetime.utcnow()
        end_at = now + timedelta(days=days)

        if mode == "overdue":
            actions = repository.get_overdue_by_user_id(
                user_id=user_id,
                before_at=now
            )

        elif mode == "due_soon":
            actions = repository.get_due_soon_by_user_id(
                user_id=user_id,
                start_at=now,
                end_at=now + timedelta(days=3)
            )

        else:
            actions = repository.get_upcoming_by_user_id(
                user_id=user_id,
                start_at=now,
                end_at=end_at
            )

        serialized_actions = [
            ActionAgent.serialize_action(action)
            for action in actions
        ]

        return AgentResult(
            success=True,
            data={
                "mode": mode,
                "count": len(serialized_actions),
                "actions": serialized_actions,
            },
            message="Reminders retrieved successfully"
        )
