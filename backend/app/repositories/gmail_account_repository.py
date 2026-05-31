from app.models.gmail_account import GmailAccount


class GmailAccountRepository:

    @staticmethod
    def get_by_user_id(
        db,
        user_id: str
    ):
        return (
            db.query(GmailAccount)
            .filter(
                GmailAccount.user_id == user_id
            )
            .first()
        )

    @staticmethod
    def create(
        db,
        **kwargs
    ):
        account = GmailAccount(**kwargs)

        db.add(account)
        db.commit()
        db.refresh(account)

        return account