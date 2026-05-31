from dataclasses import dataclass
from typing import Any


@dataclass
class AgentContext:

    agent_type: str
    payload: dict[str, Any]