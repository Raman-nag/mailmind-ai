from google import genai
from google.genai import types

from app.core.settings import settings


class EmbeddingService:
    """
    Service responsible for generating embeddings
    using Gemini.
    """

    EMBEDDING_MODEL = "gemini-embedding-001"

    _client = genai.Client(
        api_key=settings.GEMINI_API_KEY
    )

    @classmethod
    def generate_embedding(
        cls,
        text: str
    ) -> list[float]:
        """
        Generate embedding for documents/emails.
        """

        if not text or not text.strip():
            raise ValueError(
                "Text cannot be empty."
            )

        response = cls._client.models.embed_content(
            model=cls.EMBEDDING_MODEL,
            contents=text,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT"
            )
        )

        return response.embeddings[0].values

    @classmethod
    def generate_query_embedding(
        cls,
        query: str
    ) -> list[float]:
        """
        Generate embedding for search queries.
        """

        if not query or not query.strip():
            raise ValueError(
                "Query cannot be empty."
            )

        response = cls._client.models.embed_content(
            model=cls.EMBEDDING_MODEL,
            contents=query,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_QUERY"
            )
        )

        return response.embeddings[0].values