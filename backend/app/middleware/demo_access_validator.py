from fastapi import status
from jose import JWTError
from jose import jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.logging import get_logger
from app.core.settings import settings
from app.db.session import SessionLocal
from app.repositories.user_repository import UserRepository
from app.services.expiry_service import ExpiryService


logger = get_logger("mailmind.access")


class DemoAccessValidator(BaseHTTPMiddleware):
    allowed_paths = (
        "/",
        "/docs",
        "/openapi.json",
        "/redoc",
        "/api/v1/health",
        "/api/v1/auth/login",
        "/api/v1/auth/register",
        "/api/v1/feedback",
    )

    async def dispatch(
        self,
        request: Request,
        call_next
    ):
        if self._is_allowed_path(request.url.path):
            return await call_next(request)

        authorization = request.headers.get("authorization")

        if not authorization:
            return await call_next(request)

        scheme, _, token = authorization.partition(" ")

        if scheme.lower() != "bearer" or not token:
            return await call_next(request)

        db = SessionLocal()

        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            email = payload.get("sub")

            if email is None:
                return await call_next(request)

            user = UserRepository.get_by_email(
                db,
                email
            )

            if user is None:
                return await call_next(request)

            if (
                user.is_demo_expired
                or ExpiryService.is_user_expired(user)
            ):
                if not user.is_demo_expired:
                    ExpiryService.mark_user_expired(user)
                    db.commit()

                logger.info(
                    "Blocked expired demo access for user_id=%s path=%s",
                    user.id,
                    request.url.path
                )

                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={
                        "detail": "Demo access has expired."
                    }
                )

        except JWTError:
            return await call_next(request)
        finally:
            db.close()

        return await call_next(request)

    def _is_allowed_path(
        self,
        path: str
    ) -> bool:
        return any(
            path == allowed_path
            or path.startswith(f"{allowed_path}/")
            for allowed_path in self.allowed_paths
        )
