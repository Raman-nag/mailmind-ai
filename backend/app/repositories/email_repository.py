from app.models.email import Email
from sqlalchemy import or_

class EmailRepository:

    @staticmethod
    def create(
        db,
        email: Email
    ):
        db.add(email)
        db.commit()
        db.refresh(email)
        return email

    @staticmethod
    def get_by_user_id(
        db,
        user_id: str
    ):
        return (
            db.query(Email)
            .filter(Email.user_id == user_id)
            .order_by(Email.received_at.desc())
            .all()
        )
    
    @staticmethod
    def get_by_id(
        db,
        email_id: str
    ):
        return (
            db.query(Email)
            .filter(Email.id == email_id)
            .first()
        )
    
    @staticmethod
    def delete(
        db,
        email
    ):
        db.delete(email)
        db.commit()

    @staticmethod
    def update(
        db,
        email
    ):
        db.commit()
        db.refresh(email)
        return email
    
    @staticmethod
    def search(
        db,
        user_id: str,
        query: str
    ):
        return (
            db.query(Email)
            .filter(
                Email.user_id == user_id
            )
            .filter(
                or_(
                    Email.subject.ilike(f"%{query}%"),
                    Email.sender.ilike(f"%{query}%"),
                    Email.body.ilike(f"%{query}%")
                )
            )
            .order_by(
                Email.received_at.desc()
            )
            .all()
        )
    
    @staticmethod
    def count_by_user(
        db,
        user_id: str
    ):
        return (
            db.query(Email)
            .filter(Email.user_id == user_id)
            .count()
        )


    @staticmethod
    def count_summarized(
        db,
        user_id: str
    ):
        return (
            db.query(Email)
            .filter(
                Email.user_id == user_id,
                Email.summary.isnot(None)
            )
            .count()
        )
    
    @staticmethod
    def get_by_gmail_message_id(
        db,
        gmail_message_id: str
    ):
        return (
            db.query(Email)
            .filter(
                Email.gmail_message_id ==
                gmail_message_id
            )
            .first()
        )