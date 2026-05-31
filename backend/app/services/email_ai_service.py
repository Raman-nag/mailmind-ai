import json

from app.services.gemini_service import (
    GeminiService
)


class EmailAIService:

    @staticmethod
    def analyze_email(
        subject: str,
        sender: str,
        body: str
    ):

        prompt = f"""
        Analyze this email.

        Subject:
        {subject}

        Sender:
        {sender}

        Body:
        {body[:3000]}

        Return ONLY valid JSON.

        Example:

        {{
            "priority": "HIGH",
            "category": "SECURITY",
            "deadline": null
        }}

        Priority:
        HIGH, MEDIUM, LOW

        Category:
        SECURITY
        FINANCE
        WORK
        ACADEMIC
        SOCIAL
        PROMOTION

        Deadline:
        YYYY-MM-DD format
        or null
        """

        response = (
            GeminiService
            .generate(prompt)
        )

        try:
            cleaned = (
                response
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )

            return json.loads(cleaned)

        except Exception:

            return {
                "priority": "MEDIUM",
                "category": "WORK",
                "deadline": None
            }