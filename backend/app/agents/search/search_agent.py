from app.agents.base.agent import BaseAgent
from app.agents.base.context import AgentContext
from app.agents.base.result import AgentResult


class SearchAgent(BaseAgent):

    @staticmethod
    def execute(
        context: AgentContext
    ) -> AgentResult:

        return AgentResult(
            success=False,
            data={},
            message="SearchAgent not implemented"
        )