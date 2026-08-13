from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class EmailDestinationConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    to: list[str] = Field(
        default_factory=list,
        description="Primary email recipients",
    )
    cc: list[str] = Field(
        default_factory=list,
        description="Carbon-copy email recipients",
    )
    bcc: list[str] = Field(
        default_factory=list,
        description="Blind-carbon-copy email recipients",
    )


class SlackChannelDestinationConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    channel_id: str = Field(
        ...,
        min_length=1,
        description="Slack channel identifier",
    )


class TeamsConversationDestinationConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    service_url: str = Field(
        ...,
        min_length=1,
        description="Microsoft Bot Framework service URL",
    )
    conversation_id: str = Field(
        ...,
        min_length=1,
        description="Microsoft Teams conversation identifier",
    )


DestinationType = Literal["email", "channel", "conversation"]
DestinationConfig = (
    EmailDestinationConfig
    | SlackChannelDestinationConfig
    | TeamsConversationDestinationConfig
)
