from app.agents.summary.summary_agent import SummaryAgent


class RouterAgent:

    AGENTS = {
        "summary": SummaryAgent,
    }

    @staticmethod
    def get_agent(
        agent_type: str
    ):

        agent = RouterAgent.AGENTS.get(
            agent_type
        )

        if not agent:
            raise ValueError(
                f"Unsupported agent type: {agent_type}"
            )

        return agent