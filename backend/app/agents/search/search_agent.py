from app.agents.base.agent import BaseAgent
from app.agents.base.context import AgentContext
from app.agents.base.result import AgentResult

from app.services.email_service import (
    EmailService
)


class SearchAgent(BaseAgent):

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

        query = context.payload.get(
            "query"
        )

        emails = (
            EmailService
            .search_emails(
                db=db,
                user_id=user_id,
                query=query
            )
        )

        return AgentResult(
            success=True,
            data={
                "emails": emails
            },
            message="Search completed successfully"
        )