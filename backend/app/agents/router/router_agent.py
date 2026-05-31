from app.agents.summary.summary_agent import SummaryAgent
from app.agents.deadline.deadline_agent import DeadlineAgent
from app.agents.reply.reply_agent import ReplyAgent
from app.agents.search.search_agent import SearchAgent
from app.agents.memory.memory_agent import MemoryAgent
from app.agents.exceptions import (
    AgentNotFoundException
)
class RouterAgent:

    AGENTS = {
        "summary": SummaryAgent,
        "deadline": DeadlineAgent,
        "reply": ReplyAgent,
        "search": SearchAgent,
        "memory": MemoryAgent,
    }

    @staticmethod
    def get_agent(
        agent_type: str
    ):

        agent = RouterAgent.AGENTS.get(
            agent_type
        )

        if not agent:
            

            raise AgentNotFoundException(
                f"Unsupported agent type: {agent_type}"
            )

        return agent