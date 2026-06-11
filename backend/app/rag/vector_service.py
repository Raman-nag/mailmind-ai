from app.rag.chunking import EmailChunker
from app.rag.embeddings import EmbeddingGenerator
from app.rag.vector_store import vector_store


class VectorService:

    @staticmethod
    def vectorize_email(email):
        """
        Vectorize and store an email in ChromaDB.
        """

        collection = (
            vector_store.get_email_collection()
        )

        chunks = EmailChunker.chunk_email(
            subject=email.subject,
            body=email.body
        )

        for index, chunk in enumerate(chunks):

            embedding = (
                EmbeddingGenerator.generate(
                    chunk
                )
            )

            collection.upsert(
                ids=[
                    f"{email.id}_{index}"
                ],
                documents=[
                    chunk
                ],
                embeddings=[
                    embedding
                ],
                metadatas=[
                    {
                        "email_id": email.id,
                        "user_id": email.user_id,
                        "subject": email.subject,
                        "sender": email.sender,
                        "priority": (
                            email.priority or ""
                        ),
                        "category": (
                            email.category or ""
                        ),
                        "received_at": str(
                            email.received_at
                        ),
                        "chunk_index": index
                    }
                ]
            )

        return len(chunks)