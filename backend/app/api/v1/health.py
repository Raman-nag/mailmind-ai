from fastapi import APIRouter
from sqlalchemy import text

from app.db.session import engine
from app.schemas.health import HealthResponse
from app.services.health_service import HealthService

router = APIRouter()


@router.get("", response_model=HealthResponse)
def get_health():
    return HealthService.get_health()


@router.get("/db")
def test_database():
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            scalar_result = result.scalar()

        return {
            "database": "connected",
            "result": scalar_result
        }
    except Exception:
        return {
            "database": "failed",
            "result": None
        }
