from app.repositories.gmail_token_repository import (
    GmailTokenRepository
)


class GmailTokenService:

    @staticmethod
    def save_token(
        db,
        user_id: str,
        access_token: str,
        refresh_token: str,
        expiry
    ):

        existing = (
            GmailTokenRepository.get_by_user_id(
                db,
                user_id
            )
        )

        if existing:

            return GmailTokenRepository.update(
                db,
                existing,
                access_token=access_token,
                refresh_token=refresh_token,
                expiry=expiry
            )

        return GmailTokenRepository.create(
            db,
            user_id=user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            expiry=expiry
        )