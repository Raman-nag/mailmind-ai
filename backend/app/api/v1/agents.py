from fastapi import APIRouter

from app.agents.base.context import AgentContext
from app.agents.orchestrator.agent_manager import AgentManager

router = APIRouter()


@router.post("/summary/test")
def test_summary():

    context = AgentContext(
        agent_type="summary",
        payload={
            "email_content": """
            Interview scheduled on 2026-06-10.
            Please bring your resume.
            """
        }
    )

    result = AgentManager.execute(
        context
    )

    return result


@router.post("/deadline/test")
def test_deadline():

    context = AgentContext(
        agent_type="deadline",
        payload={
            "subject": "Assignment Deadline",
            "sender": "professor@college.com",
            "body": "Submit the project before 2026-06-15."
        }
    )

    result = AgentManager.execute(
        context
    )

    return result