from typing import Literal

from pydantic import BaseModel, ConfigDict


class NotificationProviderServiceConfig(BaseModel):
    """Typed configuration for NotificationProviderService."""

    model_config = ConfigDict(extra="forbid")

    keep: Literal["keep"] = "keep"
