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


class VSCodeUserAudience(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["user"] = "user"
    recipient_user_id: str = Field(..., min_length=1)


class VSCodeGroupAudience(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["group"] = "group"
    group_id: str = Field(..., min_length=1)


class VSCodeAllAudience(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["all"] = "all"


VSCodeAudience = Annotated[
    VSCodeUserAudience | VSCodeGroupAudience | VSCodeAllAudience,
    Field(discriminator="type"),
]


class VSCodeDestinationConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["vscode"] = "vscode"
    audience: VSCodeAudience = Field(...)


DestinationType = Literal[
    "email",
    "slack_channel",
    "vscode",
    "output_hole",
]
DestinationConfig = Annotated[
    EmailDestinationConfig
    | SlackChannelDestinationConfig
    | VSCodeDestinationConfig
    | OutputHoleDestinationConfig,
    Field(discriminator="type"),
]
