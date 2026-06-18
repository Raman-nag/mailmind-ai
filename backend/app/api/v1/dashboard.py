from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app.agents.base.context import AgentContext
from app.agents.orchestrator.agent_manager import AgentManager
from app.db.dependencies import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.dashboard import (
    DashboardActionsResponse,
    DashboardEmailsResponse,
    DashboardRecommendationsResponse,
    DashboardStats,
)
from app.services.email_service import EmailService

router = APIRouter()


@router.get(
    "/stats",
    response_model=DashboardStats
)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return EmailService.get_dashboard_stats(
        db=db,
        user_id=current_user.id
    )


@router.get(
    "/today-tasks",
    response_model=DashboardActionsResponse
)
def get_today_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    context = AgentContext(
        agent_type="action",
        payload={
            "db": db,
            "user_id": current_user.id,
            "mode": "today"
        }
    )

    result = AgentManager.execute(
        context
    )

    actions = result.data.get(
        "actions",
        []
    )

    return {
        "count": len(actions),
        "actions": actions
    }


@router.get(
    "/upcoming-deadlines",
    response_model=DashboardActionsResponse
)
def get_upcoming_deadlines(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    context = AgentContext(
        agent_type="reminder",
        payload={
            "db": db,
            "user_id": current_user.id,
            "mode": "upcoming",
            "days": 7
        }
    )

    result = AgentManager.execute(
        context
    )

    actions = result.data.get(
        "actions",
        []
    )

    return {
        "count": len(actions),
        "actions": actions
    }


@router.get(
    "/urgent-emails",
    response_model=DashboardEmailsResponse
)
def get_urgent_emails(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    context = AgentContext(
        agent_type="priority",
        payload={
            "db": db,
            "user_id": current_user.id
        }
    )

    result = AgentManager.execute(
        context
    )

    emails = result.data.get(
        "urgent_emails",
        []
    )

    return {
        "count": len(emails),
        "emails": emails
    }


@router.get(
    "/pending-replies",
    response_model=DashboardActionsResponse
)
def get_pending_replies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    context = AgentContext(
        agent_type="action",
        payload={
            "db": db,
            "user_id": current_user.id,
            "mode": "pending_replies"
        }
    )

    result = AgentManager.execute(
        context
    )

    actions = result.data.get(
        "actions",
        []
    )

    return {
        "count": len(actions),
        "actions": actions
    }


@router.get(
    "/recommended-actions",
    response_model=DashboardRecommendationsResponse
)
def get_recommended_actions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    contexts = [
        AgentContext(
            agent_type="action",
            payload={
                "db": db,
                "user_id": current_user.id,
                "mode": "active"
            }
        ),
        AgentContext(
            agent_type="reminder",
            payload={
                "db": db,
                "user_id": current_user.id,
                "mode": "due_soon",
                "days": 3
            }
        ),
        AgentContext(
            agent_type="recommendation",
            payload={
                "db": db,
                "user_id": current_user.id
            }
        ),
    ]

    result = AgentManager.execute_orchestrated(
        query="What should I do today?",
        contexts=contexts
    )

    recommendation_result = result.data[
        "agent_results"
    ][2]
    recommendations = recommendation_result[
        "data"
    ].get(
        "recommendations",
        []
    )

    return {
        "count": len(recommendations),
        "recommendations": recommendations,
        "answer": result.data.get(
            "answer"
        )
    }
