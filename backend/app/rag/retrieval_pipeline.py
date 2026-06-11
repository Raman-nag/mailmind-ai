from app.services.memory_service import MemoryService
from app.rag.vector_search_service import VectorSearchService


class RetrievalPipeline:

    def __init__(
        self,
        memory_service: MemoryService,
    ):
        self.memory_service = memory_service

    def retrieve(
        self,
        user_id: str,
        query: str,
        top_k: int = 5,
    ) -> dict:

        memories = (
            self.memory_service.get_memories(
                user_id=user_id,
            )
        )

        email_results = (
            VectorSearchService.search(
                query=query,
                user_id=user_id,
                top_k=top_k,
            )
        )

        return {
            "memories": memories,
            "emails": email_results,
        }