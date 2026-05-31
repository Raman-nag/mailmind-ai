from google.oauth2.credentials import Credentials

from app.core.settings import settings


class GoogleCredentialsService:

    @staticmethod
    def create_credentials(token_record):

        return Credentials(
            token=token_record.access_token,
            refresh_token=token_record.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            expiry=token_record.expiry
        )