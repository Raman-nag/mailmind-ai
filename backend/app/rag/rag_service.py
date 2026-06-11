from app.rag.context_builder import (
    ContextBuilder,
)

from app.rag.prompt_templates import (
    PromptTemplates,
)

from app.rag.retrieval_pipeline import (
    RetrievalPipeline,
)

from app.services.gemini_service import (
    GeminiService,
)


class RAGService:

    def __init__(
        self,
        retrieval_pipeline: RetrievalPipeline,
    ):
        self.retrieval_pipeline = (
            retrieval_pipeline
        )

    def chat(
        self,
        user_id: str,
        query: str,
    ) -> dict:

        retrieved = (
            self.retrieval_pipeline.retrieve(
                user_id=user_id,
                query=query,
            )
        )

        memories = retrieved["memories"]

        emails = retrieved["emails"]

        context = (
            ContextBuilder.build(
                query=query,
                memories=memories,
                email_results=emails,
            )
        )

        prompt = (
            PromptTemplates
            .inbox_chat_prompt(
                query=context["query"],
                memory_context=context[
                    "memory_context"
                ],
                email_context=context[
                    "email_context"
                ],
            )
        )

        answer = (
            GeminiService.generate(
                prompt
            )
        )

        return {
            "answer": answer,
            "memories_used": [
                memory.memory_value
                for memory in memories
            ],
            "emails_used": (
                emails.get(
                    "ids",
                    [[]],
                )[0]
            ),
        }