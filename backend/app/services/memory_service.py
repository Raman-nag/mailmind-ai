import uuid

from app.models.memory import Memory
from app.repositories.memory_repository import MemoryRepository
from app.schemas.memory import MemoryCreate, MemoryUpdate


class MemoryService:
    def __init__(self, repository: MemoryRepository):
        self.repository = repository

    def create_memory(
        self,
        user_id: str,
        memory_data: MemoryCreate,
    ) -> Memory:
        memory = Memory(
            id=str(uuid.uuid4()),
            user_id=user_id,
            memory_type=memory_data.memory_type.upper(),
            memory_value=memory_data.memory_value.strip(),
            importance_score=memory_data.importance_score,
            source=memory_data.source.upper(),
        )

        return self.repository.create(memory)

    def get_memories(
        self,
        user_id: str,
    ) -> list[Memory]:
        return self.repository.get_all(user_id)

    def get_memory(
        self,
        memory_id: str,
        user_id: str,
    ) -> Memory:
        memory = self.repository.get_by_id(
            memory_id=memory_id,
            user_id=user_id,
        )

        if not memory:
            raise ValueError("Memory not found")

        return memory

    def search_memories(
        self,
        user_id: str,
        query: str | None = None,
        memory_type: str | None = None,
    ) -> list[Memory]:
        if memory_type:
            memory_type = memory_type.upper()

        return self.repository.search(
            user_id=user_id,
            query=query,
            memory_type=memory_type,
        )

    def update_memory(
        self,
        memory_id: str,
        user_id: str,
        memory_data: MemoryUpdate,
    ) -> Memory:
        memory = self.get_memory(
            memory_id=memory_id,
            user_id=user_id,
        )

        updates = memory_data.model_dump(exclude_unset=True)

        if "memory_type" in updates:
            updates["memory_type"] = updates["memory_type"].upper()

        if "memory_value" in updates:
            updates["memory_value"] = updates["memory_value"].strip()

        if "source" in updates:
            updates["source"] = updates["source"].upper()

        for field, value in updates.items():
            setattr(memory, field, value)

        return self.repository.update(memory)

    def delete_memory(
        self,
        memory_id: str,
        user_id: str,
    ) -> None:
        memory = self.get_memory(
            memory_id=memory_id,
            user_id=user_id,
        )

        self.repository.delete(memory)