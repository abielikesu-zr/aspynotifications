from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

from aspynotifications.entities.noop import OutputHoleDestinationConfig


class EmailDestinationConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["email"] = "email"
    to: list[str] = Field(default_factory=list)
    cc: list[str] = Field(default_factory=list)
    bcc: list[str] = Field(default_factory=list)


class SlackChannelDestinationConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["slack_channel"] = "slack_channel"


DestinationType = Literal[
    "email",
    "slack_channel",
    "output_hole",
]
DestinationConfig = Annotated[
    EmailDestinationConfig
    | SlackChannelDestinationConfig
    | OutputHoleDestinationConfig,
    Field(discriminator="type"),
]
