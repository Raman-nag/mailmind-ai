from functools import lru_cache
from typing import Literal

from pydantic import AliasChoices
from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


class BaseAppSettings(BaseSettings):
    ENVIRONMENT: Literal["development", "production"] = "development"
    APP_NAME: str

    DATABASE_URL: str
    SECRET_KEY: str = Field(
        validation_alias=AliasChoices(
            "SECRET_KEY",
            "JWT_SECRET"
        )
    )
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    GEMINI_API_KEY: str

    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str

    CORS_ALLOWED_ORIGINS: str = (
        "http://localhost:3000,"
        "http://localhost:5173,"
        "http://localhost:8080"
        "http://localhost:52087"
    )

    CHROMA_DB_PATH: str = Field(
        validation_alias=AliasChoices(
            "CHROMA_DB_PATH",
            "CHROMA_PATH"
        )
    )
    CHROMA_EMAIL_COLLECTION: str = "emails_collection"

    SUPABASE_URL: str | None = None
    SUPABASE_KEY: str | None = None

    DEMO_CLEANUP_GRACE_HOURS: int = 24
    EXPIRED_USER_CLEANUP_INTERVAL_SECONDS: int = 3600


    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )

    @property
    def CORS_ORIGINS(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.CORS_ALLOWED_ORIGINS.split(",")
            if origin.strip()
        ]

    @property
    def JWT_SECRET(self) -> str:
        return self.SECRET_KEY

    @property
    def CHROMA_PATH(self) -> str:
        return self.CHROMA_DB_PATH


@lru_cache
def get_settings() -> BaseAppSettings:
    from app.core.config.development import DevelopmentSettings
    from app.core.config.production import ProductionSettings

    environment_settings = BaseAppSettings()

    if environment_settings.ENVIRONMENT == "production":
        return ProductionSettings()

    return DevelopmentSettings()
