import uuid
from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import DateTime

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.db.base import Base


class Email(Base):
    __tablename__ = "emails"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    gmail_message_id: Mapped[str] = mapped_column(
        String,
        nullable=False,
        unique=True
    )

    sender: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    subject: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    body: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    summary: Mapped[str] = mapped_column(
        Text,
        nullable=True
    )

    received_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )