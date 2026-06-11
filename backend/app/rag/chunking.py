class EmailChunker:
    """
    Responsible for splitting emails into chunks
    suitable for embedding generation.
    """

    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 150

    @classmethod
    def chunk_email(
        cls,
        subject: str,
        body: str
    ) -> list[str]:

        if not body or not body.strip():
            return []

        email_text = (
            f"Subject: {subject}\n\n"
            f"{body.strip()}"
        )

        chunks = []

        start = 0

        while start < len(email_text):
            end = start + cls.CHUNK_SIZE

            chunks.append(
                email_text[start:end]
            )

            start += (
                cls.CHUNK_SIZE -
                cls.CHUNK_OVERLAP
            )

        return chunks