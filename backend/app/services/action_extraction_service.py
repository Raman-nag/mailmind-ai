import json

from pydantic import ValidationError

from app.models.email import Email
from app.schemas.action import ActionExtractionResult, ExtractedAction
from app.services.gemini_service import GeminiService


class ActionExtractionService:
    @staticmethod
    def build_prompt(email: Email) -> str:
        return f"""
        You are extracting actionable items from an email.

        Identify tasks, deadlines, meetings, follow-ups, and commitments.

        Return ONLY valid JSON using this exact shape:

        {{
            "actions": [
                {{
                    "action_type": "TASK",
                    "title": "Short action title",
                    "description": "Specific supporting detail or null",
                    "due_date": "YYYY-MM-DDTHH:MM:SS or null",
                    "priority": "LOW",
                    "extraction_confidence": 0.85,
                    "metadata": {{}}
                }}
            ]
        }}

        Valid action_type values:
        TASK, DEADLINE, MEETING, FOLLOW_UP, COMMITMENT

        Valid priority values:
        LOW, MEDIUM, HIGH, CRITICAL

        Rules:
        - Extract only clear actions that a user may need to track.
        - Do not invent due dates.
        - Use null when no due date is present.
        - Use an empty actions array when no action exists.
        - Confidence must be between 0 and 1.

        Subject:
        {email.subject}

        Sender:
        {email.sender}

        Body:
        {email.body[:5000]}
        """

    @staticmethod
    def extract_actions(email: Email) -> ActionExtractionResult:
        response = GeminiService.generate(
            ActionExtractionService.build_prompt(email)
        )

        cleaned = (
            response
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        try:
            payload = json.loads(cleaned)

        except json.JSONDecodeError:
            return ActionExtractionResult(
                actions=[],
                rejected_actions=1
            )

        raw_actions = payload.get(
            "actions",
            []
        )

        if not isinstance(raw_actions, list):
            return ActionExtractionResult(
                actions=[],
                rejected_actions=1
            )

        actions = []
        rejected_actions = 0

        for raw_action in raw_actions:
            try:
                actions.append(
                    ExtractedAction.model_validate(raw_action)
                )

            except ValidationError:
                rejected_actions += 1

        return ActionExtractionResult(
            actions=actions,
            rejected_actions=rejected_actions
        )
