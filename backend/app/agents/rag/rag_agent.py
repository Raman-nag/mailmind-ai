from app.agents.base.agent import BaseAgent
from app.agents.base.context import AgentContext
from app.agents.base.result import AgentResult

from app.rag.rag_service import RAGService


class RAGAgent(BaseAgent):

    @staticmethod
    def execute(
        context: AgentContext,
    ) -> AgentResult:

        user_id = context.payload.get(
            "user_id"
        )

        query = context.payload.get(
            "query"
        )

        rag_service = context.payload.get(
            "rag_service"
        )

        if not user_id:

            return AgentResult(
                success=False,
                data={},
                message="User ID is required",
            )

        if not query:

            return AgentResult(
                success=False,
                data={},
                message="Query is required",
            )

        if not rag_service:

            return AgentResult(
                success=False,
                data={},
                message="RAG Service is required",
            )

        response = rag_service.chat(
            user_id=user_id,
            query=query,
        )

        return AgentResult(
            success=True,
            data=response,
            message="Chat response generated successfully",
        )