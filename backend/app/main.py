from fastapi import FastAPI

from app.api.v1.health import router as health_router
from app.core.settings import settings

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0"
)

app.include_router(
    health_router,
    prefix="/api/v1/health",
    tags=["Health"]
)


@app.get("/")
def root():
    return {
        "message": "MailMind AI Backend Running",
        "app_name": settings.APP_NAME
    }