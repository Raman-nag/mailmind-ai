import re

from app.agents.action.action_agent import ActionAgent
from app.agents.base.agent import BaseAgent
from app.agents.base.context import AgentContext
from app.agents.base.result import AgentResult
from app.repositories.action_repository import ActionRepository
from app.repositories.email_repository import EmailRepository
from app.repositories.memory_repository import MemoryRepository


class RecommendationAgent(BaseAgent):

    @staticmethod
    def tokens(text: str | None) -> set[str]:
        if not text:
            return set()

        return {
            token
            for token in re.findall(
                r"[a-z0-9]+",
                text.lower()
            )
            if len(token) > 3
        }

    @staticmethod
    def build_memory_recommendations(
        actions: list[dict],
        memories
    ) -> list[dict]:
        recommendations = []

        for memory in memories:
            memory_tokens = RecommendationAgent.tokens(
                memory.memory_value
            )

            if not memory_tokens:
                continue

            matching_actions = [
                action
                for action in actions
                if RecommendationAgent.tokens(
                    " ".join(
                        [
                            action["title"],
                            action["description"] or "",
                            action["source_email_subject"],
                        ]
                    )
                ).intersection(memory_tokens)
            ]

            if not matching_actions:
                continue

            recommendations.append(
                {
                    "title": "Prioritize memory-aligned actions",
                    "description": (
                        f"You have {len(matching_actions)} action(s) related to: "
                        f"{memory.memory_value}"
                    ),
                    "reason": memory.memory_value,
                    "action_ids": [
                        action["id"]
                        for action in matching_actions
                    ],
                    "priority": "HIGH",
                }
            )

        return recommendations

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

        action_repository = ActionRepository(db)
        memory_repository = MemoryRepository(db)

        actions = [
            ActionAgent.serialize_action(action)
            for action in action_repository.get_active_by_user_id(
                user_id
            )
        ]
        memories = memory_repository.get_all(
            user_id
        )
        urgent_emails = EmailRepository.get_urgent_by_user_id(
            db,
            user_id
        )

        recommendations = RecommendationAgent.build_memory_recommendations(
            actions,
            memories
        )

        if urgent_emails:
            recommendations.append(
                {
                    "title": "Review urgent emails",
                    "description": (
                        f"You have {len(urgent_emails)} high-priority email(s) "
                        "that may need attention."
                    ),
                    "reason": "Existing email priority signals",
                    "action_ids": [],
                    "priority": "HIGH",
                }
            )

        if actions and not recommendations:
            recommendations.append(
                {
                    "title": "Work through active actions",
                    "description": (
                        f"You have {len(actions)} active action(s) waiting."
                    ),
                    "reason": "Active action backlog",
                    "action_ids": [
                        action["id"]
                        for action in actions[:3]
                    ],
                    "priority": "MEDIUM",
                }
            )

        return AgentResult(
            success=True,
            data={
                "recommendations": recommendations,
                "memories_used": [
                    {
                        "id": memory.id,
                        "memory_type": memory.memory_type,
                        "memory_value": memory.memory_value,
                        "importance_score": memory.importance_score,
                    }
                    for memory in memories
                ],
                "actions_used": actions,
            },
            message="Recommendations generated successfully"
        )
