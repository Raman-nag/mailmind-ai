from app.core.security import hash_password
from app.models.user import User
from app.repositories.user_repository import UserRepository


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
            raise ValueError(
                "User already exists"
            )

        user = User(
            email=email,
            full_name=full_name,
            hashed_password=hash_password(password)
        )

        return UserRepository.create(
            db,
            user
        )