from sqlalchemy.orm import Session

from app.models.email import Email
from app.repositories.email_repository import EmailRepository

class EmailService:

    @staticmethod
    def create_email(
        db: Session,
        **kwargs
    ):
        email = Email(**kwargs)

        db.add(email)
        db.commit()
        db.refresh(email)

        return email
    
    @staticmethod
    def get_user_emails(
        db,
        user_id: str
    ):
        return EmailRepository.get_by_user_id(
            db,
            user_id
        )
    
    @staticmethod
    def get_email_by_id(
        db,
        email_id: str
    ):
        return EmailRepository.get_by_id(
            db,
            email_id
        )
    
    @staticmethod
    def delete_email(
        db,
        email
    ):
        EmailRepository.delete(
            db,
            email
        )

    @staticmethod
    def update_email_summary(
        db,
        email,
        summary: str
    ):
        email.summary = summary

        return EmailRepository.update(
            db,
            email
        )
    
    @staticmethod
    def update_email_ai_fields(
        db,
        email,
        priority=None,
        category=None,
        deadline=None
    ):

        email.priority = priority
        email.category = category
        email.deadline = deadline

        return EmailRepository.update(
            db,
            email
        )
    
    @staticmethod
    def search_emails(
        db,
        user_id: str,
        query: str
    ):
        return EmailRepository.search(
            db=db,
            user_id=user_id,
            query=query
        )
    
    @staticmethod
    def get_dashboard_stats(
        db,
        user_id: str
    ):
        total = EmailRepository.count_by_user(
            db,
            user_id
        )

        summarized = EmailRepository.count_summarized(
            db,
            user_id
        )

        return {
            "total_emails": total,
            "summarized_emails": summarized,
            "pending_summaries": total - summarized
        }
    
    @staticmethod
    def import_gmail_email(
        db,
        user_id: str,
        gmail_message_id: str,
        sender: str,
        subject: str,
        body: str,
        received_at
    ):

        existing = (
            EmailRepository
            .get_by_gmail_message_id(
                db,
                gmail_message_id
            )
        )

        if existing:
            return existing

        return EmailService.create_email(
            db=db,
            user_id=user_id,
            gmail_message_id=gmail_message_id,
            sender=sender,
            subject=subject,
            body=body,
            received_at=received_at,
            summary=None
        )
    
    