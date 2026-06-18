from app.core.security import hash_password
from app.core.security import verify_password
from app.core.security import create_access_token
from app.core.logging import get_logger

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.demo_access_service import DemoAccessService


logger = get_logger("mailmind.auth")


class AuthService:

    @staticmethod
    def register_user(
        db,
        email: str,
        full_name: str,
        password: str
    ):

        existing_user = UserRepository.get_by_email(
            db,
            email
        )

        if existing_user:
            logger.info(
                "User registration rejected existing_email=%s",
                email
            )
            raise ValueError(
                "User already exists"
            )

        user = User(
            email=email,
            full_name=full_name,
            hashed_password=hash_password(password)
        )
        DemoAccessService.initialize_demo_period(user)

        created_user = UserRepository.create(
            db,
            user
        )
        logger.info(
            "User registered user_id=%s email=%s",
            created_user.id,
            created_user.email
        )
        return created_user

    @staticmethod
    def login_user(
        db,
        email: str,
        password: str
    ):

        user = UserRepository.get_by_email(
            db,
            email
        )

        if not user:
            logger.info(
                "Login failed unknown_email=%s",
                email
            )
            raise ValueError(
                "Invalid credentials"
            )

        if not verify_password(
            password,
            user.hashed_password
        ):
            logger.info(
                "Login failed invalid_password user_id=%s",
                user.id
            )
            raise ValueError(
                "Invalid credentials"
            )

        token = create_access_token(
            {
                "sub": user.email
            }
        )

        logger.info(
            "Login succeeded user_id=%s",
            user.id
        )

        return {
            "access_token": token,
            "token_type": "bearer"
        }
