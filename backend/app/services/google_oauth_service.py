from google_auth_oauthlib.flow import Flow

from app.core.settings import settings


class GoogleOAuthService:

    @staticmethod
    def create_flow():

        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token"
                }
            },
            scopes=[
                "openid",
                "https://www.googleapis.com/auth/userinfo.email",
                "https://www.googleapis.com/auth/gmail.readonly"
            ],
            redirect_uri=settings.GOOGLE_REDIRECT_URI
        )

        # Disable PKCE
        flow.autogenerate_code_verifier = False

        return flow