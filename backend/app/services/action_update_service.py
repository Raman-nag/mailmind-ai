from app.models.action import Action, ActionStatus
from app.repositories.action_repository import ActionRepository
from app.schemas.action import ExtractedAction


class ActionUpdateService:
    VALID_TRANSITIONS = {
        ActionStatus.PENDING: {
            ActionStatus.IN_PROGRESS,
            ActionStatus.COMPLETED,
            ActionStatus.DISMISSED,
        },
        ActionStatus.IN_PROGRESS: {
            ActionStatus.PENDING,
            ActionStatus.COMPLETED,
            ActionStatus.DISMISSED,
        },
        ActionStatus.COMPLETED: set(),
        ActionStatus.DISMISSED: set(),
    }

    def __init__(self, repository: ActionRepository):
        self.repository = repository

    def transition_status(
        self,
        action: Action,
        status: ActionStatus
    ) -> Action:
        if action.status == status:
            return action

        allowed_statuses = self.VALID_TRANSITIONS.get(
            action.status,
            set()
        )

        if status not in allowed_statuses:
            return action

        action.status = status

        return self.repository.update(action)

    def apply_extracted_action(
        self,
        action: Action,
        extracted_action: ExtractedAction
    ) -> Action:
        action.action_type = extracted_action.action_type
        action.title = extracted_action.title
        action.description = extracted_action.description
        action.due_date = extracted_action.due_date
        action.priority = extracted_action.priority
        action.extraction_confidence = max(
            action.extraction_confidence,
            extracted_action.extraction_confidence
        )
        action.metadata_ = {
            **(action.metadata_ or {}),
            **extracted_action.metadata,
            "updated_from_email": True,
        }

        if action.status == ActionStatus.PENDING:
            action.status = ActionStatus.IN_PROGRESS

        return self.repository.update(action)
