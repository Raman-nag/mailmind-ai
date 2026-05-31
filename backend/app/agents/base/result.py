from dataclasses import dataclass
from typing import Any


@dataclass
class AgentResult:

    success: bool
    data: dict[str, Any]
    message: str = ""