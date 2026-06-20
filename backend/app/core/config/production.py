from typing import Literal

from pydantic import model_validator

from app.core.config.base import BaseAppSettings


class ProductionSettings(BaseAppSettings):
    ENVIRONMENT: Literal["production"] = "production"

    @model_validator(mode="after")
    def validate_production_secrets(self):
        if len(self.SECRET_KEY) < 32:
            raise ValueError(
                "SECRET_KEY must be at least 32 characters in production"
            )

        return self