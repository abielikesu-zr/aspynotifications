from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

from aspynotifications_dtos.noop_dtos import AHoleProviderDTO


class ZeptoMailCredentialsDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    send_mail_token: str = Field(
        ...,
        description="ZeptoMail Send Mail Token",
    )


class ZeptoMailProviderSettingsDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    from_address: str = Field(
        ...,
        description="Email address to send from",
    )
    from_name: str | None = Field(
        None,
        description="Display name to send from",
    )
    credentials: ZeptoMailCredentialsDTO = Field(
        ...,
        description="ZeptoMail authentication credentials",
    )


class ZeptoMailProviderDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["ZEPTOMAIL"] = "ZEPTOMAIL"
    config: ZeptoMailProviderSettingsDTO


class SlackProviderSettingsDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    webhook_url: str = Field(
        ...,
        description="Slack incoming webhook URL",
    )


class SlackProviderDTO(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["SLACK"] = "SLACK"
    config: SlackProviderSettingsDTO


NotificationProviderConfigDTO = Annotated[
    ZeptoMailProviderDTO | SlackProviderDTO | AHoleProviderDTO,
    Field(discriminator="type"),
]


class CreateNotificationProviderRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=1)
    provider: NotificationProviderConfigDTO


class NotificationProviderDTO(CreateNotificationProviderRequest):
    id: str = Field(..., min_length=1)
