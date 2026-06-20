import google.generativeai as genai
from google.api_core.exceptions import (
    ResourceExhausted,
    GoogleAPICallError,
)

from app.core.settings import settings


genai.configure(
    api_key=settings.GEMINI_API_KEY
)


class GeminiService:

    @staticmethod
    def generate(
        prompt: str
    ) -> str:

        try:
            model = genai.GenerativeModel(
                "gemini-2.5-flash"
            )

            response = model.generate_content(
                prompt
            )

            if not response:
                return (
                    "AI service returned an empty response."
                )

            if not getattr(response, "text", None):
                return (
                    "AI service could not generate a response."
                )

            return response.text

        except ResourceExhausted:
            return (
                "Gemini API quota exceeded. "
                "Please wait a minute and try again."
            )

        except GoogleAPICallError as e:
            return (
                f"Gemini API error: {str(e)}"
            )

        except Exception as e:
            return (
                f"AI service temporarily unavailable: {str(e)}"
            )

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