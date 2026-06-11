from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session

from app.agents.base.context import (
    AgentContext,
)

from app.agents.rag.rag_agent import (
    RAGAgent,
)

from app.db.session import get_db

from app.dependencies.auth import (
    get_current_user,
)

from app.models.user import User

from app.repositories.memory_repository import (
    MemoryRepository,
)

from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
)

from app.services.memory_service import (
    MemoryService,
)

from app.rag.retrieval_pipeline import (
    RetrievalPipeline,
)

from app.rag.rag_service import (
    RAGService,
)

router = APIRouter() 


def get_rag_service(
    db: Session = Depends(get_db),
) -> RAGService:

    memory_repository = (
        MemoryRepository(db)
    )

    memory_service = (
        MemoryService(
            memory_repository
        )
    )

    retrieval_pipeline = (
        RetrievalPipeline(
            memory_service
        )
    )

    return RAGService(
        retrieval_pipeline
    )


@router.post(
    "",
    response_model=ChatResponse,
)
def chat(
    request: ChatRequest,
    current_user: User = Depends(
        get_current_user
    ),
    rag_service: RAGService = Depends(
        get_rag_service
    ),
):

    context = AgentContext(
        agent_type="rag",
        payload={
            "user_id": current_user.id,
            "query": request.query,
            "rag_service": rag_service,
        },
    )

    result = RAGAgent.execute(
        context
    )

    if not result.success:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.message,
        )

    return ChatResponse(
        answer=result.data[
            "answer"
        ],
        memories_used=result.data[
            "memories_used"
        ],
        emails_used=result.data[
            "emails_used"
        ],
    )