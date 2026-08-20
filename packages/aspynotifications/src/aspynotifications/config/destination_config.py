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
    channel_id: str = Field(..., min_length=1)


class TeamsConversationDestinationConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["teams_conversation"] = "teams_conversation"
    service_url: str = Field(..., min_length=1)
    conversation_id: str = Field(..., min_length=1)


DestinationType = Literal[
    "email",
    "slack_channel",
    "teams_conversation",
    "output_hole",
]
DestinationConfig = Annotated[
    EmailDestinationConfig
    | SlackChannelDestinationConfig
    | TeamsConversationDestinationConfig
    | OutputHoleDestinationConfig,
    Field(discriminator="type"),
]
