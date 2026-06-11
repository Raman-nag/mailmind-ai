from pydantic import BaseModel


class VectorSearchRequest(BaseModel):
    query: str
    top_k: int = 5