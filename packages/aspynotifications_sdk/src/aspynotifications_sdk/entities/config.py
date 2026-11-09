from typing import Literal

from aspyadapters.adapters.http_client_config import HttpClientConfig
from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class RestClientConfig(BaseModel):
    base_url: HttpUrl


class RestClientAdapterConfig(BaseModel):
    type: Literal["REST"] = "REST"
    config: RestClientConfig = Field(...)


class FacadeClientConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    keep: Literal["keep"] = "keep"


class FacadeClientAdapterConfig(BaseModel):
    type: Literal["FACADE"] = "FACADE"
    config: FacadeClientConfig = Field(default_factory=FacadeClientConfig)


class NotificationClientConfig(BaseModel):
    adapter: RestClientAdapterConfig | FacadeClientAdapterConfig = Field(
        ..., discriminator="type"
    )


class NotificationsSdkParams(BaseModel):
    http_client: HttpClientConfig | None = Field(default=None)
    notification_client: NotificationClientConfig


class NotificationsSdkConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    notifications_sdk: NotificationsSdkParams
