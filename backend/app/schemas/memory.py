from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class MemoryBase(BaseModel):
    memory_type: str
    memory_value: str
    importance_score: int = 5
    source: str = "USER"


class MemoryCreate(MemoryBase):
    pass


class MemoryUpdate(BaseModel):
    memory_type: Optional[str] = None
    memory_value: Optional[str] = None
    importance_score: Optional[int] = None
    source: Optional[str] = None


class MemoryResponse(MemoryBase):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MemorySearch(BaseModel):
    query: Optional[str] = None
    memory_type: Optional[str] = None