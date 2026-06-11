class ContextBuilder:

    @staticmethod
    def build(
        query: str,
        memories: list,
        email_results: dict,
    ) -> dict:

        memory_context = []

        for memory in memories:

            memory_context.append(
                f"- {memory.memory_value}"
            )

        email_context = []

        documents = (
            email_results.get("documents", [])
        )

        metadatas = (
            email_results.get("metadatas", [])
        )

        if documents:

            docs = documents[0]

            metadata_list = (
                metadatas[0]
                if metadatas
                else []
            )

            for i, doc in enumerate(docs):

                metadata = (
                    metadata_list[i]
                    if i < len(metadata_list)
                    else {}
                )

                subject = metadata.get(
                    "subject",
                    "Unknown Subject",
                )

                email_context.append(
                    f"Subject: {subject}\n"
                    f"Content: {doc}"
                )

        return {
            "query": query,
            "memory_context": "\n".join(
                memory_context
            ),
            "email_context": "\n\n".join(
                email_context
            ),
        }