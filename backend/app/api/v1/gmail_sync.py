from datetime import datetime

from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.dependencies.auth import get_current_user

from app.models.user import User

from app.repositories.gmail_token_repository import (
    GmailTokenRepository
)

from app.services.google_credentials_service import (
    GoogleCredentialsService
)

from app.services.gmail_service import (
    GmailService
)

from app.services.gmail_parser_service import (
    GmailParserService
)

from app.services.email_service import (
    EmailService
)

from app.services.gemini_service import (
    GeminiService
)

from app.services.email_ai_service import (
    EmailAIService
)

from app.repositories.email_repository import (
    EmailRepository
)

router = APIRouter()


@router.get("/sync")
def sync_gmail(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    token = GmailTokenRepository.get_by_user_id(
        db,
        current_user.id
    )

    if token is None:
        return {
            "message": "No Gmail account connected"
        }

    credentials = (
        GoogleCredentialsService
        .create_credentials(token)
    )

    print("=" * 80)
    print("GMAIL SYNC STARTED")
    print("USER:", current_user.email)
    print("ACCESS TOKEN:", bool(token.access_token))
    print("REFRESH TOKEN:", bool(token.refresh_token))
    print("EXPIRY:", token.expiry)
    print("=" * 80)

    service = GmailService.create_service(
        credentials
    )

    messages = GmailService.list_messages(
        service
    )

    imported_count = 0
    summarized_count = 0

    for message in messages:

        try:

            full_message = GmailService.get_message(
                service,
                message["id"]
            )

            payload = full_message.get(
                "payload",
                {}
            )

            headers = payload.get(
                "headers",
                []
            )

            sender = GmailService.extract_header(
                headers,
                "From"
            )

            subject = GmailService.extract_header(
                headers,
                "Subject"
            )

            body = GmailParserService.get_body(
                payload
            )

            existing = (
                EmailRepository
                .get_by_gmail_message_id(
                    db,
                    message["id"]
                )
            )

            if existing:
                continue

            email = EmailService.import_gmail_email(
                db=db,
                user_id=current_user.id,
                gmail_message_id=message["id"],
                sender=sender,
                subject=subject,
                body=body,
                received_at=datetime.utcnow()
            )

            imported_count += 1

            # Skip Gemini for very short emails
            if len(body.strip()) < 150:

                summary = (
                    "Short notification email. "
                    + body[:300]
                )

                EmailService.update_email_summary(
                    db=db,
                    email=email,
                    summary=summary
                )

                summarized_count += 1

                print(
                    f"SHORT EMAIL SUMMARY: {subject}"
                )

                continue

            if not email.summary:

                try:

                    summary = (
                        GeminiService
                        .summarize_email(
                            f"""
                            Subject:
                            {subject}

                            Sender:
                            {sender}

                            Body:
                            {body[:5000]}
                            """
                        )
                    )

                    EmailService.update_email_summary(
                        db=db,
                        email=email,
                        summary=summary
                    )

                    ai_result = (
                        EmailAIService
                        .analyze_email(
                            subject=subject,
                            sender=sender,
                            body=body
                        )
                    )

                    EmailService.update_email_ai_fields(
                        db=db,
                        email=email,
                        priority=ai_result.get(
                            "priority"
                        ),
                        category=ai_result.get(
                            "category"
                        ),
                        deadline=ai_result.get(
                            "deadline"
                        )
                    )

                    summarized_count += 1

                    print(
                        f"AI ANALYZED: {subject}"
                    )

                except Exception as e:

                    print("=" * 80)
                    print("AI ANALYSIS FAILED")
                    print("SUBJECT:", subject)
                    print("ERROR:", str(e))
                    print("=" * 80)

                    summarized_count += 1

                    print(
                        f"SUMMARIZED: {subject}"
                    )

                except Exception as e:

                    print("=" * 80)
                    print("SUMMARY FAILED")
                    print("SUBJECT:", subject)
                    print("ERROR:", str(e))
                    print("=" * 80)

        except Exception as e:

            print("=" * 80)
            print("EMAIL IMPORT FAILED")
            print("MESSAGE ID:", message["id"])
            print("ERROR:", str(e))
            print("=" * 80)

    print("=" * 80)
    print("SYNC COMPLETE")
    print("IMPORTED:", imported_count)
    print("SUMMARIZED:", summarized_count)
    print("=" * 80)

    return {
        "imported_emails": imported_count,
        "summarized_emails": summarized_count
    }