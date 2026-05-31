from app.agents.base.agent import BaseAgent
from app.agents.base.context import AgentContext
from app.agents.base.result import AgentResult

from app.services.email_ai_service import (
    EmailAIService
)


class DeadlineAgent(BaseAgent):

    @staticmethod
    def execute(
        context: AgentContext
    ) -> AgentResult:

        subject = context.payload.get(
            "subject"
        )

        sender = context.payload.get(
            "sender"
        )

        body = context.payload.get(
            "body"
        )

        ai_result = (
            EmailAIService
            .analyze_email(
                subject=subject,
                sender=sender,
                body=body
            )
        )

        return AgentResult(
            success=True,
            data=ai_result,
            message="Email analyzed successfully"
        )