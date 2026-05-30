from sqlalchemy.orm import Session

from app.models.email import Email


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