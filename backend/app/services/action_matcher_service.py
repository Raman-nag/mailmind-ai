import re

from app.models.action import Action


class ActionMatcherService:
    COMPLETION_PHRASES = [
        "completed",
        "done",
        "finished",
        "submitted",
        "sent",
        "resolved",
        "closed",
        "thanks for submitting",
        "thank you for submitting",
        "received your",
        "we received",
    ]

    @staticmethod
    def normalize_tokens(text: str | None) -> set[str]:
        if not text:
            return set()

        tokens = re.findall(
            r"[a-z0-9]+",
            text.lower()
        )

        return {
            ActionMatcherService.normalize_token(token)
            for token in tokens
            if len(token) > 2
        }

    @staticmethod
    def normalize_token(token: str) -> str:
        for suffix in ("ing", "ed", "es", "s"):
            if token.endswith(suffix) and len(token) > len(suffix) + 3:
                return token[: -len(suffix)]

        return token

    @staticmethod
    def score_match(
        action: Action,
        text: str
    ) -> float:
        action_tokens = ActionMatcherService.normalize_tokens(
            " ".join(
                [
                    action.title,
                    action.description or "",
                    action.source_email_subject
                ]
            )
        )
        text_tokens = ActionMatcherService.normalize_tokens(text)

        if not action_tokens or not text_tokens:
            return 0.0

        overlap = action_tokens.intersection(text_tokens)

        return len(overlap) / len(action_tokens)

    @staticmethod
    def find_best_match(
        actions: list[Action],
        title: str,
        description: str | None = None,
        threshold: float = 0.3
    ) -> Action | None:
        text = " ".join(
            [
                title,
                description or ""
            ]
        )

        scored_actions = [
            (
                ActionMatcherService.score_match(
                    action,
                    text
                ),
                action
            )
            for action in actions
        ]

        if not scored_actions:
            return None

        score, action = max(
            scored_actions,
            key=lambda item: item[0]
        )

        if score < threshold:
            return None

        return action

    @staticmethod
    def detect_completion(
        actions: list[Action],
        subject: str,
        body: str
    ) -> list[Action]:
        text = f"{subject} {body}".lower()

        if not any(phrase in text for phrase in ActionMatcherService.COMPLETION_PHRASES):
            return []

        return [
            action
            for action in actions
            if ActionMatcherService.score_match(action, text) >= 0.2
        ]
