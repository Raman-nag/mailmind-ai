import chromadb
from chromadb.api.models.Collection import Collection

from app.core.settings import settings


class ChromaVectorStore:
    """
    Responsible for managing ChromaDB collections.
    """

    def __init__(self):
        self.client = chromadb.PersistentClient(
            path=settings.CHROMA_DB_PATH
        )

    def get_email_collection(self) -> Collection:
        """
        Create or retrieve the email collection.
        """

        return self.client.get_or_create_collection(
            name=settings.CHROMA_EMAIL_COLLECTION,
            metadata={
                "description": "MailMind email embeddings"
            }
        )


vector_store = ChromaVectorStore()