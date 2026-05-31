from app.agents.base.agent import BaseAgent
from app.agents.base.context import AgentContext
from app.agents.base.result import AgentResult

from app.services.gemini_service import (
    GeminiService
)


class ReplyAgent(BaseAgent):

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

        reply = (
            GeminiService
            .generate_reply(
                subject=subject,
                sender=sender,
                body=body
            )
        )

        return AgentResult(
            success=True,
            data={
                "reply": reply
            },
            message="Reply generated successfully"
        )