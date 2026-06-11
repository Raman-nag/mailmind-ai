from app.services.embedding_service import (
    EmbeddingService,
)


class EmbeddingGenerator:
    """
    Wrapper around EmbeddingService
    for use inside the RAG layer.
    """

    @staticmethod
    def generate(
        text: str
    ) -> list[float]:

        return (
            EmbeddingService.generate_embedding(
                text
            )
        )

    @staticmethod
    def generate_query(
        query: str
    ) -> list[float]:

        return (
            EmbeddingService.generate_query_embedding(
                query
            )
        )