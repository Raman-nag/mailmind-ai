from datetime import datetime, time, timedelta

from app.agents.base.agent import BaseAgent
from app.agents.base.context import AgentContext
from app.agents.base.result import AgentResult
from app.models.action import Action
from app.repositories.action_repository import ActionRepository


class ActionAgent(BaseAgent):

    @staticmethod
    def serialize_action(action: Action) -> dict:
        return {
            "id": action.id,
            "email_id": action.email_id,
            "action_type": action.action_type.value,
            "title": action.title,
            "description": action.description,
            "due_date": action.due_date,
            "status": action.status.value,
            "priority": action.priority.value,
            "source_email_subject": action.source_email_subject,
            "extraction_confidence": action.extraction_confidence,
            "metadata": action.metadata_ or {},
        }

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
            "active"
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

        if mode == "today":
            today = datetime.utcnow().date()
            start_at = datetime.combine(
                today,
                time.min
            )
            end_at = start_at + timedelta(days=1)
            actions = repository.get_today_by_user_id(
                user_id=user_id,
                start_at=start_at,
                end_at=end_at
            )

        elif mode == "pending":
            actions = repository.get_pending_by_user_id(
                user_id
            )

        elif mode == "pending_replies":
            actions = repository.get_pending_replies_by_user_id(
                user_id
            )

        else:
            actions = repository.get_active_by_user_id(
                user_id
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
                "summary": {
                    "total": len(serialized_actions),
                    "high_priority": len(
                        [
                            action
                            for action in serialized_actions
                            if action["priority"] in [
                                "HIGH",
                                "CRITICAL"
                            ]
                        ]
                    ),
                }
            },
            message="Actions retrieved successfully"
        )
