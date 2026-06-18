from typing import Literal

from app.core.config.base import BaseAppSettings


class DevelopmentSettings(BaseAppSettings):
    ENVIRONMENT: Literal["development"] = "development"
