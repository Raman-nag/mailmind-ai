from app.rag.embeddings import EmbeddingGenerator
from app.rag.vector_store import vector_store


class VectorSearchService:

    @staticmethod
    def search(
        query: str,
        user_id: str,
        top_k: int = 5
    ):
        """
        Search for semantically similar emails.
        """

        collection = (
            vector_store.get_email_collection()
        )

        query_embedding = (
            EmbeddingGenerator.generate_query(
                query
            )
        )

        results = collection.query(
            query_embeddings=[
                query_embedding
            ],
            n_results=top_k,
            where={
                "user_id": user_id
            }
        )

        return results