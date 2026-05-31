from fastapi import APIRouter
from fastapi import Request
import requests

from app.core.settings import settings
from app.services.google_oauth_service import (
    GoogleOAuthService
)

router = APIRouter()


@router.get("/connect")
def connect_gmail():

    flow = GoogleOAuthService.create_flow()

    authorization_url, state = flow.authorization_url(
        access_type="offline",
        prompt="consent"
    )

    print("AUTH URL:")
    print(authorization_url)

    return {
        "authorization_url": authorization_url,
        "state": state
    }


from fastapi import Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.db.dependencies import get_db
from app.repositories.user_repository import UserRepository
from app.repositories.gmail_token_repository import GmailTokenRepository


@router.get("/callback")
def gmail_callback(
    request: Request,
    db: Session = Depends(get_db)
):

    code = request.query_params.get("code")

    token_response = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        }
    )

    data = token_response.json()

    user = UserRepository.get_by_email(
        db,
        "test@mailmind.ai"
    )

    if user is None:
        return {
            "error": "User not found"
        }

    existing = GmailTokenRepository.get_by_user_id(
        db,
        user.id
    )

    expiry = datetime.utcnow() + timedelta(
        seconds=data.get("expires_in", 3600)
    )

    if existing:

        GmailTokenRepository.update(
            db,
            existing,
            access_token=data.get("access_token"),
            refresh_token=data.get("refresh_token"),
            expiry=expiry
        )

    else:

        GmailTokenRepository.create(
            db=db,
            user_id=user.id,
            access_token=data.get("access_token"),
            refresh_token=data.get("refresh_token"),
            expiry=expiry
        )

    return {
        "message": "Gmail token saved",
        "user_id": user.id
    }