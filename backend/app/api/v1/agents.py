from fastapi import APIRouter

from app.agents.base.context import AgentContext
from app.agents.orchestrator.agent_manager import AgentManager
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
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

@router.post("/reply/test")
def test_reply():

    context = AgentContext(
        agent_type="reply",
        payload={
            "subject": "Interview Invitation",
            "sender": "hr@company.com",
            "body": """
            We would like to invite you
            for an interview on Monday
            at 10 AM.
            """
        }
    )

    result = AgentManager.execute(
        context
    )

    return result

@router.get("/search/test")
def test_search(
    q: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    )
):

    context = AgentContext(
        agent_type="search",
        payload={
            "db": db,
            "user_id": current_user.id,
            "query": q
        }
    )

    result = AgentManager.execute(
        context
    )

    return {
        "success": result.success,
        "count": len(
            result.data["emails"]
        ),
        "emails": result.data["emails"]
    }