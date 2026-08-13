from pydantic import BaseModel, ConfigDict, Field

from aspynotifications.config.destination_config import (
    DestinationConfig,
    DestinationType,
)


class Destination(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    provider: str = Field(..., min_length=1)
    type: DestinationType
    template: str = Field(..., min_length=1)
    routable: bool = False
    config: DestinationConfig
