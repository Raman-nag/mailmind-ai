from app.models.gmail_token import GmailToken


class GmailTokenRepository:

    @staticmethod
    def get_by_user_id(
        db,
        user_id: str
    ):
        return (
            db.query(GmailToken)
            .filter(
                GmailToken.user_id == user_id
            )
            .first()
        )

    @staticmethod
    def create(
        db,
        **kwargs
    ):
        token = GmailToken(**kwargs)

        db.add(token)
        db.commit()
        db.refresh(token)

        return token

    @staticmethod
    def update(
        db,
        token,
        **kwargs
    ):
        for key, value in kwargs.items():
            setattr(token, key, value)

        db.commit()
        db.refresh(token)

        return token