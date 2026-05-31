from app.agents.base.context import AgentContext
from app.agents.base.result import AgentResult

from app.agents.router.router_agent import RouterAgent


class AgentManager:

    @staticmethod
    def execute(
        context: AgentContext
    ) -> AgentResult:

        agent = RouterAgent.get_agent(
            context.agent_type
        )

        return agent.execute(
            context
        )