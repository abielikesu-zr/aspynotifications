from pydantic import BaseModel, ConfigDict, Field

from aspynotifications.config.destination_config import (
    DestinationConfig,
    DestinationType,
)


class Destination(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(
        ...,
        min_length=1,
        description="Unique textual identifier for the destination",
    )
    name: str = Field(
        ...,
        min_length=1,
        description="Human-readable destination name",
    )
    provider: str = Field(
        ...,
        min_length=1,
        description="Name of the configured provider used for delivery",
    )
    type: DestinationType = Field(
        ...,
        description="Destination endpoint type",
    )
    template: str = Field(
        ...,
        min_length=1,
        description="Logical template name selected by the destination",
    )
    routable: bool = Field(
        default=False,
        description="Whether the destination accepts event-supplied recipients in to",
    )
    config: DestinationConfig = Field(
        ...,
        description="Typed configuration for the destination endpoint",
    )
