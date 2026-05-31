from app.agents.base.agent import BaseAgent
from app.agents.base.context import AgentContext
from app.agents.base.result import AgentResult

from app.services.gemini_service import GeminiService


class SummaryAgent(BaseAgent):

    @staticmethod
    def execute(
        context: AgentContext
    ) -> AgentResult:

        email_content = context.payload.get(
            "email_content"
        )

        if not email_content:

            return AgentResult(
                success=False,
                data={},
                message="Email content is required"
            )

        summary = (
            GeminiService
            .summarize_email(
                email_content
            )
        )

        return AgentResult(
            success=True,
            data={
                "summary": summary
            },
            message="Summary generated successfully"
        )