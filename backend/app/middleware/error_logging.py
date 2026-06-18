from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.core.logging import get_logger


logger = get_logger("mailmind.errors")


class ErrorLoggingMiddleware(BaseHTTPMiddleware):

    async def dispatch(
        self,
        request: Request,
        call_next
    ):
        try:
            return await call_next(request)
        except Exception:
            logger.exception(
                "Unhandled application error path=%s method=%s",
                request.url.path,
                request.method
            )
            raise
