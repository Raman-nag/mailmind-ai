from fastapi import FastAPI
from app.api.v1.auth import router as auth_router
from app.api.v1.health import router as health_router
from app.core.settings import settings
from app.api.v1.summary import router as summary_router
app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0"
)

app.include_router(
    health_router,
    prefix="/api/v1/health",
    tags=["Health"]
)
app.include_router(
    auth_router,
    prefix="/api/v1/auth",
    tags=["Auth"]
)
app.include_router(
    summary_router,
    prefix="/api/v1/summary",
    tags=["Summary"]
)

@app.get("/")
def root():
    return {
        "message": "MailMind AI Backend Running",
        "app_name": settings.APP_NAME
    }