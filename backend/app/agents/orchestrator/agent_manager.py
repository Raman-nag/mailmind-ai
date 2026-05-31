from app.agents.base.context import AgentContext
from app.agents.base.result import AgentResult

from app.agents.router.router_agent import RouterAgent
from app.agents.logger import logger

from app.agents.exceptions import (
    AgentExecutionException
)


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

            raise AgentExecutionException(
                str(e)
            )