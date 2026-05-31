from app.agents.base.agent import BaseAgent
from app.agents.base.context import AgentContext
from app.agents.base.result import AgentResult


class MemoryAgent(BaseAgent):

    @staticmethod
    def execute(
        context: AgentContext
    ) -> AgentResult:

        return AgentResult(
            success=False,
            data={},
            message="MemoryAgent not implemented"
        )