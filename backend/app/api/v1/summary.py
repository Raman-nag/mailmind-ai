from fastapi import APIRouter

from app.schemas.summary import (
    EmailSummaryRequest,
    EmailSummaryResponse
)
from app.services.gemini_service import GeminiService

router = APIRouter()


@router.post(
    "/",
    response_model=EmailSummaryResponse
)
def summarize_email(
    request: EmailSummaryRequest
):

    summary = GeminiService.summarize_email(
        request.email_content
    )

    return EmailSummaryResponse(
        summary=summary
    )