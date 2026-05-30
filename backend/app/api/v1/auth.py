from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.user import UserRegister
from app.schemas.user import UserResponse
from app.schemas.user import UserLogin
from app.schemas.user import TokenResponse
from app.services.auth_service import AuthService
from app.dependencies.auth import get_current_user
from app.models.user import User

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse
)
def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    try:

        user = AuthService.register_user(
            db=db,
            email=user_data.email,
            full_name=user_data.full_name,
            password=user_data.password
        )

        return user

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


# ADD THIS BELOW REGISTER
@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    user_data: UserLogin,
    db: Session = Depends(get_db)
):
    try:

        return AuthService.login_user(
            db=db,
            email=user_data.email,
            password=user_data.password
        )

    except ValueError as e:
        raise HTTPException(
            status_code=401,
            detail=str(e)
        )

@router.get(
    "/me",
    response_model=UserResponse
)
def me(
    current_user: User = Depends(
        get_current_user
    )
):
    return current_user