from abc import ABC
from abc import abstractmethod

from app.agents.base.context import AgentContext
from app.agents.base.result import AgentResult


class BaseAgent(ABC):

    @staticmethod
    @abstractmethod
    def execute(
        context: AgentContext
    ) -> AgentResult:
        pass