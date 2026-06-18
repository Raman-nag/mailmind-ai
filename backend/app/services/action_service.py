from sqlalchemy.orm import Session

from app.models.action import Action, ActionStatus
from app.models.email import Email
from app.repositories.action_repository import ActionRepository
from app.services.action_extraction_service import ActionExtractionService
from app.services.action_matcher_service import ActionMatcherService
from app.services.action_update_service import ActionUpdateService


class ActionService:
    @staticmethod
    def process_email_actions(
        db: Session,
        email: Email
    ) -> dict:
        repository = ActionRepository(db)
        update_service = ActionUpdateService(repository)

        active_actions = repository.get_active_by_user_id(
            email.user_id
        )

        completed_actions = ActionMatcherService.detect_completion(
            active_actions,
            email.subject,
            email.body
        )

        for action in completed_actions:
            update_service.transition_status(
                action,
                ActionStatus.COMPLETED
            )

        active_actions = [
            action
            for action in active_actions
            if action not in completed_actions
        ]

        extraction_result = ActionExtractionService.extract_actions(
            email
        )

        created_count = 0
        updated_count = 0

        for extracted_action in extraction_result.actions:
            existing_action = ActionMatcherService.find_best_match(
                active_actions,
                extracted_action.title,
                extracted_action.description
            )

            if existing_action:
                update_service.apply_extracted_action(
                    existing_action,
                    extracted_action
                )
                updated_count += 1
                continue

            action = Action(
                user_id=email.user_id,
                email_id=email.id,
                action_type=extracted_action.action_type,
                title=extracted_action.title,
                description=extracted_action.description,
                due_date=extracted_action.due_date,
                status=ActionStatus.PENDING,
                priority=extracted_action.priority,
                source_email_subject=email.subject,
                extraction_confidence=extracted_action.extraction_confidence,
                metadata_=extracted_action.metadata
            )

            repository.create(action)
            active_actions.append(action)
            created_count += 1

        return {
            "created_actions": created_count,
            "updated_actions": updated_count,
            "completed_actions": len(completed_actions),
            "rejected_actions": extraction_result.rejected_actions
        }
