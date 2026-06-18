from typing import Literal

from app.core.config.base import BaseAppSettings


class ProductionSettings(BaseAppSettings):
    ENVIRONMENT: Literal["production"] = "production"
