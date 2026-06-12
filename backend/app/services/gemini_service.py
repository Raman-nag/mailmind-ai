import google.generativeai as genai

from app.core.settings import settings

from app.core.settings import settings

print("GEMINI KEY:", settings.GEMINI_API_KEY[:10])
genai.configure(
    api_key=settings.GEMINI_API_KEY
)


class GeminiService:

    @staticmethod
    def generate(
        prompt: str
    ) -> str:

        model = genai.GenerativeModel(
            "gemini-2.5-flash"
        )

        response = model.generate_content(
            prompt
        )

        return response.text

    @staticmethod
    def summarize_email(
        email_content: str
    ) -> str:

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

        return GeminiService.generate(
            prompt
        )
    
    @staticmethod
    def generate_reply(
        subject: str,
        sender: str,
        body: str
    ) -> str:

        prompt = f"""
        You are an email assistant.

        Generate a professional reply.

        Subject:
        {subject}

        Sender:
        {sender}

        Original Email:
        {body}

        Return only the reply email.
        """

        return GeminiService.generate(
            prompt
        )