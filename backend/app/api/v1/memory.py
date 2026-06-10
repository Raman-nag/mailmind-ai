from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.dependencies.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.memory_repository import MemoryRepository
from app.schemas.memory import (
    MemoryCreate,
    MemoryResponse,
    MemoryUpdate,
)
from app.services.memory_service import MemoryService

router = APIRouter()


from fastapi import Depends

def get_memory_service(
    db: Session = Depends(get_db),
) -> MemoryService:
    repository = MemoryRepository(db)
    return MemoryService(repository)


@router.post(
    "",
    response_model=MemoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_memory(
    memory_data: MemoryCreate,
    current_user: User = Depends(get_current_user),
    service: MemoryService = Depends(get_memory_service),
):
    return service.create_memory(
        user_id=current_user.id,
        memory_data=memory_data,
    )


@router.get(
    "",
    response_model=list[MemoryResponse],
)
def get_memories(
    current_user: User = Depends(get_current_user),
    service: MemoryService = Depends(get_memory_service),
):
    return service.get_memories(
        user_id=current_user.id,
    )


@router.get(
    "/search",
    response_model=list[MemoryResponse],
)
def search_memories(
    query: Optional[str] = Query(default=None),
    memory_type: Optional[str] = Query(default=None),
    current_user: User = Depends(get_current_user),
    service: MemoryService = Depends(get_memory_service),
):
    return service.search_memories(
        user_id=current_user.id,
        query=query,
        memory_type=memory_type,
    )


@router.put(
    "/{memory_id}",
    response_model=MemoryResponse,
)
def update_memory(
    memory_id: str,
    memory_data: MemoryUpdate,
    current_user: User = Depends(get_current_user),
    service: MemoryService = Depends(get_memory_service),
):
    try:
        return service.update_memory(
            memory_id=memory_id,
            user_id=current_user.id,
            memory_data=memory_data,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.delete(
    "/{memory_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_memory(
    memory_id: str,
    current_user: User = Depends(get_current_user),
    service: MemoryService = Depends(get_memory_service),
):
    try:
        service.delete_memory(
            memory_id=memory_id,
            user_id=current_user.id,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )