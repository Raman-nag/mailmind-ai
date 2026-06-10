from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.memory import Memory


class MemoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, memory: Memory) -> Memory:
        self.db.add(memory)
        self.db.commit()
        self.db.refresh(memory)
        return memory

    def get_by_id(
        self,
        memory_id: str,
        user_id: str,
    ) -> Optional[Memory]:
        stmt = select(Memory).where(
            Memory.id == memory_id,
            Memory.user_id == user_id,
        )

        return self.db.scalar(stmt)

    def get_all(
        self,
        user_id: str,
    ) -> list[Memory]:
        stmt = (
            select(Memory)
            .where(Memory.user_id == user_id)
            .order_by(Memory.created_at.desc())
        )

        return list(self.db.scalars(stmt).all())

    def search(
        self,
        user_id: str,
        query: Optional[str] = None,
        memory_type: Optional[str] = None,
    ) -> list[Memory]:
        stmt = select(Memory).where(
            Memory.user_id == user_id
        )

        if query:
            stmt = stmt.where(
                Memory.memory_value.ilike(f"%{query}%")
            )

        if memory_type:
            stmt = stmt.where(
                Memory.memory_type == memory_type
            )

        stmt = stmt.order_by(
            Memory.importance_score.desc(),
            Memory.created_at.desc(),
        )

        return list(self.db.scalars(stmt).all())

    def update(
        self,
        memory: Memory,
    ) -> Memory:
        self.db.commit()
        self.db.refresh(memory)
        return memory

    def delete(
        self,
        memory: Memory,
    ) -> None:
        self.db.delete(memory)
        self.db.commit()