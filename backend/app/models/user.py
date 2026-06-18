import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    email: Mapped[str] = mapped_column(
        String,
        unique=True,
        nullable=False
    )

    full_name: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    hashed_password: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )

    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    demo_started_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    is_demo_expired: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    cleanup_after_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    feedback_submitted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    actions = relationship(
        "Action",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    feedback_items = relationship(
        "Feedback",
        back_populates="user",
        cascade="all, delete-orphan"
    )
