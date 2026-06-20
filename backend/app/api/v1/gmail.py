from datetime import datetime
from datetime import timedelta
import secrets

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
import requests
from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.core.settings import settings
from app.db.dependencies import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.repositories.gmail_token_repository import GmailTokenRepository
from app.repositories.oauth_state_repository import OAuthStateRepository
from app.services.google_oauth_service import GoogleOAuthService


router = APIRouter()
logger = get_logger("mailmind.gmail")
OAUTH_STATE_TTL_MINUTES = 10


@router.get("/connect")
def connect_gmail(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    now = datetime.utcnow()
    OAuthStateRepository.delete_expired(
        db,
        now
    )

    state = secrets.token_urlsafe(32)
    OAuthStateRepository.create(
        db=db,
        state=state,
        user_id=current_user.id,
        expires_at=now + timedelta(minutes=OAUTH_STATE_TTL_MINUTES)
    )

    flow = GoogleOAuthService.create_flow()

    authorization_url, returned_state = flow.authorization_url(
        access_type="offline",
        prompt="consent",
        state=state
    )

    logger.info(
        "Generated Gmail authorization URL user_id=%s",
        current_user.id
    )

    return {
        "authorization_url": authorization_url,
        "state": returned_state
    }


@router.get("/callback")
def gmail_callback(
    request: Request,
    db: Session = Depends(get_db)
):
    code = request.query_params.get("code")
    state = request.query_params.get("state")

    if not code or not state:
        raise HTTPException(
            status_code=400,
            detail="Missing OAuth code or state"
        )

    oauth_state = OAuthStateRepository.get_by_state(
        db,
        state
    )
    now = datetime.utcnow()

    if (
        oauth_state is None
        or oauth_state.used_at is not None
        or oauth_state.expires_at < now
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid OAuth state"
        )

    try:
        token_response = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            },
            timeout=10
        )
        token_response.raise_for_status()
    except requests.RequestException:
        logger.warning("Gmail token exchange request failed")
        raise HTTPException(
            status_code=400,
            detail="OAuth token exchange failed"
        )

    try:
        data = token_response.json()
    except ValueError:
        logger.warning("Gmail token exchange returned invalid JSON")
        raise HTTPException(
            status_code=400,
            detail="OAuth token exchange failed"
        )

    if "error" in data or not data.get("access_token"):
        logger.warning("Gmail token exchange returned invalid response")
        raise HTTPException(
            status_code=400,
            detail="OAuth token exchange failed"
        )

    existing = GmailTokenRepository.get_by_user_id(
        db,
        oauth_state.user_id
    )

    expiry = datetime.utcnow() + timedelta(
        seconds=data.get("expires_in", 3600)
    )

    if existing:
        GmailTokenRepository.update(
            db,
            existing,
            access_token=data.get("access_token"),
            refresh_token=data.get("refresh_token") or existing.refresh_token,
            expiry=expiry
        )
    else:
        GmailTokenRepository.create(
            db=db,
            user_id=oauth_state.user_id,
            access_token=data.get("access_token"),
            refresh_token=data.get("refresh_token"),
            expiry=expiry
        )

    OAuthStateRepository.mark_used(
        db,
        oauth_state,
        now
    )

    return {
        "message": "Gmail token saved",
        "user_id": oauth_state.user_id
    }