import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ActionType(str, enum.Enum):
    TASK = "TASK"
    DEADLINE = "DEADLINE"
    MEETING = "MEETING"
    FOLLOW_UP = "FOLLOW_UP"
    COMMITMENT = "COMMITMENT"


class ActionStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    DISMISSED = "DISMISSED"


class ActionPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Action(Base):
    __tablename__ = "actions"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    email_id: Mapped[str] = mapped_column(
        ForeignKey("emails.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    action_type: Mapped[ActionType] = mapped_column(
        Enum(ActionType, name="action_type"),
        nullable=False,
        index=True
    )

    title: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    due_date: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
        index=True
    )

    status: Mapped[ActionStatus] = mapped_column(
        Enum(ActionStatus, name="action_status"),
        nullable=False,
        default=ActionStatus.PENDING,
        index=True
    )

    priority: Mapped[ActionPriority] = mapped_column(
        Enum(ActionPriority, name="action_priority"),
        nullable=False,
        default=ActionPriority.MEDIUM,
        index=True
    )

    source_email_subject: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    extraction_confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0
    )

    metadata_: Mapped[dict | None] = mapped_column(
        "metadata",
        JSON,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    user = relationship(
        "User",
        back_populates="actions"
    )

    email = relationship(
        "Email",
        back_populates="actions"
    )
