from typing import Literal

from pydantic import BaseModel


ServiceStatus = Literal["ok", "failed"]
HealthStatus = Literal["healthy", "unhealthy"]


class HealthServices(BaseModel):
    database: ServiceStatus
    chromadb: ServiceStatus
    gemini: ServiceStatus


class HealthResponse(BaseModel):
    status: HealthStatus
    services: HealthServices
