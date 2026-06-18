from datetime import datetime
from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator

from app.models.action import ActionPriority, ActionStatus, ActionType


class ActionBase(BaseModel):
    action_type: ActionType
    title: str
    description: str | None = None
    due_date: datetime | None = None
    status: ActionStatus = ActionStatus.PENDING
    priority: ActionPriority = ActionPriority.MEDIUM
    source_email_subject: str
    extraction_confidence: float = Field(ge=0.0, le=1.0)
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        validation_alias=AliasChoices("metadata_", "metadata")
    )

    @field_validator("title", "source_email_subject")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("value cannot be empty")

        return value


class ActionCreate(ActionBase):
    user_id: str
    email_id: str


class ActionUpdate(BaseModel):
    action_type: ActionType | None = None
    title: str | None = None
    description: str | None = None
    due_date: datetime | None = None
    status: ActionStatus | None = None
    priority: ActionPriority | None = None
    extraction_confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    metadata: dict[str, Any] | None = None


class ActionResponse(ActionBase):
    id: str
    user_id: str
    email_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ExtractedAction(BaseModel):
    action_type: ActionType
    title: str
    description: str | None = None
    due_date: datetime | None = None
    priority: ActionPriority = ActionPriority.MEDIUM
    extraction_confidence: float = Field(ge=0.0, le=1.0)
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        validation_alias=AliasChoices("metadata_", "metadata")
    )

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("title cannot be empty")

        return value


class ActionExtractionResult(BaseModel):
    actions: list[ExtractedAction] = Field(default_factory=list)
    rejected_actions: int = 0
