import google.generativeai as genai

from app.core.settings import settings


genai.configure(
    api_key=settings.GEMINI_API_KEY
)


class GeminiService:

    @staticmethod
    def summarize_email(
        email_content: str
    ) -> str:

        model = genai.GenerativeModel(
            "gemini-2.5-flash"
        )

        prompt = f"""
        Summarize the following email.

        Email:
        {email_content}

        Return:
        - Main purpose
        - Action items
        - Important dates
        - Important people
        """

        response = model.generate_content(
            prompt
        )

        return response.text