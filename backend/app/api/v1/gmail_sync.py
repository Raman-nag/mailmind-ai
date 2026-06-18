from datetime import datetime
from app.core.logging import get_logger
from app.rag.vector_service import (
    VectorService
)
from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.dependencies.auth import get_current_user
from app.agents.base.context import AgentContext
from app.agents.orchestrator.agent_manager import AgentManager

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

from app.services.action_service import (
    ActionService
)


from app.repositories.email_repository import (
    EmailRepository
)

router = APIRouter()
logger = get_logger("mailmind.gmail_sync")


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
        logger.info(
            "Gmail sync skipped no_account user_id=%s",
            current_user.id
        )
        return {
            "message": "No Gmail account connected"
        }

    credentials = (
        GoogleCredentialsService
        .create_credentials(token)
    )

    logger.info(
        "Gmail sync started user_id=%s token_expiry=%s",
        current_user.id,
        token.expiry
    )

    service = GmailService.create_service(
        credentials
    )

    messages = GmailService.list_messages(
        service
    )

    imported_count = 0
    summarized_count = 0
    created_actions_count = 0
    updated_actions_count = 0
    completed_actions_count = 0
    rejected_actions_count = 0

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

            VectorService.vectorize_email(
                email
            )

            logger.info(
                "Email vectorized user_id=%s email_id=%s",
                current_user.id,
                email.id
            )

            imported_count += 1

            try:

                action_result = (
                    ActionService
                    .process_email_actions(
                        db=db,
                        email=email
                    )
                )

                created_actions_count += action_result.get(
                    "created_actions",
                    0
                )
                updated_actions_count += action_result.get(
                    "updated_actions",
                    0
                )
                completed_actions_count += action_result.get(
                    "completed_actions",
                    0
                )
                rejected_actions_count += action_result.get(
                    "rejected_actions",
                    0
                )

                logger.info(
                    "Actions processed user_id=%s email_id=%s result=%s",
                    current_user.id,
                    email.id,
                    action_result
                )

            except Exception as e:

                logger.exception(
                    "Action extraction failed user_id=%s message_id=%s",
                    current_user.id,
                    message["id"]
                )

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

                logger.info(
                    "Short email summarized user_id=%s email_id=%s",
                    current_user.id,
                    email.id
                )

                continue

            if not email.summary:

                try:

                    context = AgentContext(
                        agent_type="summary",
                        payload={
                            "email_content": f"""
                            Subject:
                            {subject}

                            Sender:
                            {sender}

                            Body:
                            {body[:5000]}
                            """
                        }
                    )

                    result = AgentManager.execute(
                        context
                    )

                    summary = result.data["summary"]

                    EmailService.update_email_summary(
                        db=db,
                        email=email,
                        summary=summary
                    )

                    context = AgentContext(
                        agent_type="deadline",
                        payload={
                            "subject": subject,
                            "sender": sender,
                            "body": body
                        }
                    )

                    result = AgentManager.execute(
                        context
                    )

                    ai_result = result.data

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

                    logger.info(
                        "Email AI analyzed user_id=%s email_id=%s",
                        current_user.id,
                        email.id
                    )

                except Exception as e:

                    logger.exception(
                        "AI analysis failed user_id=%s message_id=%s",
                        current_user.id,
                        message["id"]
                    )

                    summarized_count += 1

                    logger.info(
                        "Email marked summarized after AI failure user_id=%s email_id=%s",
                        current_user.id,
                        email.id
                    )

                except Exception as e:

                    logger.exception(
                        "Summary failed user_id=%s message_id=%s",
                        current_user.id,
                        message["id"]
                    )

        except Exception as e:

            logger.exception(
                "Email import failed user_id=%s message_id=%s",
                current_user.id,
                message["id"]
            )

    logger.info(
        "Gmail sync completed user_id=%s imported=%s summarized=%s "
        "created_actions=%s updated_actions=%s completed_actions=%s "
        "rejected_actions=%s",
        current_user.id,
        imported_count,
        summarized_count,
        created_actions_count,
        updated_actions_count,
        completed_actions_count,
        rejected_actions_count
    )

    return {
        "imported_emails": imported_count,
        "summarized_emails": summarized_count
    }
