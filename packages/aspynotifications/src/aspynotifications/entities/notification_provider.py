from typing import Literal

from pydantic import BaseModel, Field


class ZeptoMailCredentials(BaseModel):
    """
    Credentials for authenticating with the ZeptoMail API.
    """

    send_mail_token: str = Field(
        ...,
        description="ZeptoMail Send Mail Token",
    )


class ZeptoMailProviderSettings(BaseModel):
    """
    Configuration specific to the ZeptoMail notification provider.
    """

    from_address: str = Field(..., description="Email address to send from")
    from_name: str | None = Field(None, description="Display name to send from")
    credentials: ZeptoMailCredentials = Field(
        ..., description="ZeptoMail authentication credentials"
    )


class ZeptoMailProvider(BaseModel):
    """
    Wrapper for ZeptoMail notification provider configuration.
    """

    type: Literal["ZEPTOMAIL"] = Field(
        "ZEPTOMAIL", description="Type of notification provider"
    )
    config: ZeptoMailProviderSettings = Field(
        ...,
        description="ZeptoMail-specific configuration",
    )


class SlackProviderSettings(BaseModel):
    """
    Configuration specific to the Slack notification provider.
    """

    webhook_url: str = Field(..., description="Slack incoming webhook URL")


class SlackProvider(BaseModel):
    """
    Wrapper for Slack notification provider configuration.
    """

    type: Literal["SLACK"] = Field("SLACK", description="Type of notification provider")
    config: SlackProviderSettings = Field(
        ...,
        description="Slack-specific configuration",
    )


class NotificationProvider(BaseModel):
    """
    Configured notification provider.
    """

    id: str = Field(..., description="Unique provider identifier")
    name: str = Field(..., description="Provider name")

    provider: ZeptoMailProvider | SlackProvider = (
        Field(
            ...,
            discriminator="type",
            description="Notification provider configuration",
        )
    )
