import logging

import google.generativeai as genai
from sqlalchemy import text

from app.core.settings import settings
from app.db.session import engine
from app.schemas.health import HealthResponse
from app.schemas.health import HealthServices
from app.schemas.health import ServiceStatus


logger = logging.getLogger(__name__)


class HealthService:
    @staticmethod
    def check_database() -> ServiceStatus:
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1")).scalar()
            return "ok"
        except Exception:
            logger.exception("Database health check failed")
            return "failed"

    @staticmethod
    def check_chromadb() -> ServiceStatus:
        try:
            from app.rag.vector_store import vector_store

            vector_store.client.heartbeat()
            return "ok"
        except Exception:
            logger.exception("ChromaDB health check failed")
            return "failed"

    @staticmethod
    def check_gemini() -> ServiceStatus:
        try:
            if not settings.GEMINI_API_KEY:
                return "failed"

            genai.configure(api_key=settings.GEMINI_API_KEY)
            genai.GenerativeModel("gemini-2.5-flash")
            return "ok"
        except Exception:
            logger.exception("Gemini health check failed")
            return "failed"

    @classmethod
    def get_health(cls) -> HealthResponse:
        services = HealthServices(
            database=cls.check_database(),
            chromadb=cls.check_chromadb(),
            gemini=cls.check_gemini()
        )
        status = (
            "healthy"
            if all(service == "ok" for service in services.model_dump().values())
            else "unhealthy"
        )

        return HealthResponse(
            status=status,
            services=services
        )
