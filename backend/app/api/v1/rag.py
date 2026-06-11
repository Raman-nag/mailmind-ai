from fastapi import APIRouter
from fastapi import Depends

from app.dependencies.auth import (
    get_current_user
)
from app.rag.vector_search_service import (
    VectorSearchService
)
from app.schemas.rag import (
    VectorSearchRequest
)

router = APIRouter(
    prefix="/rag",
    tags=["RAG"]
)


@router.post("/search")
def search_emails(
    request: VectorSearchRequest,
    current_user=Depends(
        get_current_user
    )
):

    results = VectorSearchService.search(
        query=request.query,
        user_id=current_user.id,
        top_k=request.top_k
    )

    return results