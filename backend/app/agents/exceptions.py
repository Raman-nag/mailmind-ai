class AgentException(Exception):
    pass


class AgentNotFoundException(
    AgentException
):
    pass


class AgentExecutionException(
    AgentException
):
    pass