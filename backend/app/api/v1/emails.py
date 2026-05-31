from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.email import EmailCreate
from app.schemas.email import EmailResponse
from app.services.email_service import EmailService
from app.services.gemini_service import GeminiService
from app.dependencies.auth import get_current_user
from app.models.user import User
from fastapi import HTTPException
from fastapi import Response
from fastapi import Query

router = APIRouter()
@router.get(
    "/search",
    response_model=list[EmailResponse]
)
def search_emails(
    q: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return EmailService.search_emails(
        db=db,
        user_id=current_user.id,
        query=q
    )
@router.get("/{email_id}")

@router.post(
    "/",
    response_model=EmailResponse
)
def create_email(
    email_data: EmailCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    summary = GeminiService.summarize_email(
        email_data.body
    )

    email = EmailService.create_email(
        db=db,
        user_id=current_user.id,
        sender=email_data.sender,
        subject=email_data.subject,
        body=email_data.body,
        gmail_message_id=email_data.gmail_message_id,
        received_at=email_data.received_at,
        summary=summary
    )

    return email


@router.get(
    "/",
    response_model=list[EmailResponse]
)
def get_my_emails(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return EmailService.get_user_emails(
        db=db,
        user_id=current_user.id
    )

@router.get(
    "/{email_id}",
    response_model=EmailResponse
)
def get_email(
    email_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    email = EmailService.get_email_by_id(
        db=db,
        email_id=email_id
    )

    if email is None:
        raise HTTPException(
            status_code=404,
            detail="Email not found"
        )

    if email.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    return email

@router.delete(
    "/{email_id}",
    status_code=204
)
def delete_email(
    email_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    email = EmailService.get_email_by_id(
        db=db,
        email_id=email_id
    )

    if email is None:
        raise HTTPException(
            status_code=404,
            detail="Email not found"
        )

    if email.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    EmailService.delete_email(
        db=db,
        email=email
    )

    return Response(
        status_code=204
    )

@router.post(
    "/{email_id}/summarize",
    response_model=EmailResponse
)
def summarize_email(
    email_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    email = EmailService.get_email_by_id(
        db=db,
        email_id=email_id
    )

    if email is None:
        raise HTTPException(
            status_code=404,
            detail="Email not found"
        )

    if email.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Access denied"
        )

    summary = GeminiService.summarize_email(
        email.body
    )

    return EmailService.update_email_summary(
        db=db,
        email=email,
        summary=summary
    )