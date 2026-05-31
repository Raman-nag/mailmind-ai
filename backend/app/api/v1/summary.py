from fastapi import APIRouter

from app.schemas.summary import (
    EmailSummaryRequest,
    EmailSummaryResponse
)
from app.agents.base.context import AgentContext
from app.agents.orchestrator.agent_manager import AgentManager

router = APIRouter()


@router.post(
    "/",
    response_model=EmailSummaryResponse
)
def summarize_email(
    request: EmailSummaryRequest
):

    context = AgentContext(
        agent_type="summary",
        payload={
            "email_content": request.email_content
        }
    )

    result = AgentManager.execute(
        context
    )

    return EmailSummaryResponse(
        summary=result.data["summary"]
    )