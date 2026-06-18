from app.agents.base.context import AgentContext
from app.agents.base.result import AgentResult

from app.agents.router.router_agent import RouterAgent
from app.agents.logger import logger

from app.agents.exceptions import (
    AgentExecutionException
)
from app.services.gemini_service import GeminiService


class AgentManager:

    @staticmethod
    def execute(
        context: AgentContext
    ) -> AgentResult:

        agent = RouterAgent.get_agent(
            context.agent_type
        )

        try:

            logger.info(
                f"Executing agent: {context.agent_type}"
            )

            result = agent.execute(
                context
            )

            logger.info(
                f"Completed agent: {context.agent_type}"
            )

            return result

        except Exception as e:

            logger.exception(
                f"Agent execution failed: {context.agent_type}"
            )

            raise AgentExecutionException(
                str(e)
            )

    @staticmethod
    def execute_many(
        contexts: list[AgentContext]
    ) -> list[AgentResult]:

        results = []

        for context in contexts:
            results.append(
                AgentManager.execute(
                    context
                )
            )

        return results

    @staticmethod
    def synthesize(
        query: str,
        results: list[AgentResult]
    ) -> str:

        agent_outputs = [
            {
                "success": result.success,
                "data": result.data,
                "message": result.message,
            }
            for result in results
        ]

        prompt = f"""
        You are MailMind AI, a proactive email assistant.

        Use these agent outputs to answer the user clearly and concisely.
        Focus on what the user should do next.

        User question:
        {query}

        Agent outputs:
        {agent_outputs}

        Return a concise final response.
        """

        try:
            return GeminiService.generate(prompt)

        except Exception:
            return (
                "You have pending email actions that may require attention. "
                "Review urgent emails and upcoming deadlines first."
            )

    @staticmethod
    def execute_orchestrated(
        query: str,
        contexts: list[AgentContext]
    ) -> AgentResult:

        results = AgentManager.execute_many(
            contexts
        )

        
        try:
            synthesis = AgentManager.synthesize(
                query=query,
                results=results
            )
        except Exception:
            synthesis = (
                "AI recommendation temporarily unavailable. "
                "Review urgent emails and pending actions."
            )

        return AgentResult(
            success=True,
            data={
                "answer": synthesis,
                "agent_results": [
                    {
                        "success": result.success,
                        "data": result.data,
                        "message": result.message,
                    }
                    for result in results
                ],
            },
            message="Orchestrated response generated successfully"
        )
