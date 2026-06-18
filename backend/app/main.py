import os
from contextlib import asynccontextmanager

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.memory import router as memory_router
from app.api.v1.auth import router as auth_router
from app.api.v1.health import router as health_router
from app.core.settings import settings
from app.api.v1.summary import router as summary_router
from app.api.v1.emails import router as email_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.gmail import router as gmail_router
from app.api.v1.gmail_sync import router as gmail_sync_router
from app.api.v1 import agents
from app.api.v1.rag import (
    router as rag_router
)
from app.api.v1.chat import (
    router as chat_router,
)
from app.core.logging import configure_logging
from app.middleware.demo_access_validator import DemoAccessValidator
from app.middleware.error_logging import ErrorLoggingMiddleware
from app.modules.feedback.routers.feedback import router as feedback_router
from app.services.expired_user_cleanup_scheduler import (
    ExpiredUserCleanupScheduler
)

configure_logging()

cleanup_scheduler = ExpiredUserCleanupScheduler(
    interval_seconds=settings.EXPIRED_USER_CLEANUP_INTERVAL_SECONDS
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    cleanup_scheduler.start()
    try:
        yield
    finally:
        await cleanup_scheduler.stop()

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    lifespan=lifespan
)
app.add_middleware(ErrorLoggingMiddleware)
app.add_middleware(DemoAccessValidator)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"http://localhost:\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(
    rag_router
)
app.include_router(
    chat_router,
    prefix="/api/v1/chat",
    tags=["Chat"],
)
app.include_router(
    health_router,
    prefix="/api/v1/health",
    tags=["Health"]
)

app.include_router(
    memory_router,
    prefix="/api/v1/memories",
    tags=["Memory"]
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
app.include_router(
    email_router,
    prefix="/api/v1/emails",
    tags=["Emails"]
)

app.include_router(
    dashboard_router,
    prefix="/api/v1/dashboard",
    tags=["Dashboard"]
)

app.include_router(
    gmail_router,
    prefix="/api/v1/gmail",
    tags=["gmail"]
)

app.include_router(
    gmail_sync_router,
    prefix="/api/v1/gmail",
    tags=["gmail"]
)

app.include_router(
    agents.router,
    prefix="/api/v1/agents",
    tags=["Agents"]
)
app.include_router(
    feedback_router,
    prefix="/api/v1/feedback",
    tags=["Feedback"]
)
@app.get("/")
def root():
    return {
        "message": "MailMind AI Backend Running",
        "app_name": settings.APP_NAME
    }
