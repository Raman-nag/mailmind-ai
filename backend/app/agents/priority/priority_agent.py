from app.agents.action.action_agent import ActionAgent
from app.agents.base.agent import BaseAgent
from app.agents.base.context import AgentContext
from app.agents.base.result import AgentResult
from app.repositories.action_repository import ActionRepository
from app.repositories.email_repository import EmailRepository


class PriorityAgent(BaseAgent):
    PRIORITY_SCORES = {
        "CRITICAL": 100,
        "HIGH": 75,
        "MEDIUM": 50,
        "LOW": 25,
    }

    @staticmethod
    def serialize_email(email) -> dict:
        return {
            "id": email.id,
            "sender": email.sender,
            "subject": email.subject,
            "summary": email.summary,
            "priority": email.priority,
            "category": email.category,
            "deadline": email.deadline,
            "received_at": email.received_at,
        }

    @staticmethod
    def rank_actions(actions: list[dict]) -> list[dict]:
        return sorted(
            [
                {
                    **action,
                    "urgency_score": PriorityAgent.PRIORITY_SCORES.get(
                        action["priority"],
                        0
                    )
                }
                for action in actions
            ],
            key=lambda action: (
                action["urgency_score"],
                action["due_date"] is not None
            ),
            reverse=True
        )

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
        critical_actions = [
            ActionAgent.serialize_action(action)
            for action in repository.get_critical_by_user_id(
                user_id
            )
        ]
        ranked_actions = PriorityAgent.rank_actions(
            critical_actions
        )
        urgent_emails = [
            PriorityAgent.serialize_email(email)
            for email in EmailRepository.get_urgent_by_user_id(
                db,
                user_id
            )
        ]

        return AgentResult(
            success=True,
            data={
                "critical_actions": ranked_actions,
                "urgent_emails": urgent_emails,
                "count": len(ranked_actions) + len(urgent_emails),
            },
            message="Priority items retrieved successfully"
        )
