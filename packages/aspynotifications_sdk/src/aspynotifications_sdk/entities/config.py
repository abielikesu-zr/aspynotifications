from typing import Literal

from aspyadapters.adapters.http_client_config import HttpClientConfig
from aspynats.config.nats_client_config import NatsClientAdapterConfig
from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class RestClientConfig(BaseModel):
    base_url: HttpUrl


class RestClientAdapterConfig(BaseModel):
    type: Literal["REST"] = "REST"
    config: RestClientConfig = Field(...)


class NotificationClientConfig(BaseModel):
    adapter: RestClientAdapterConfig | NatsClientAdapterConfig = Field(
        ..., discriminator="type"
    )


class NotificationsSdkParams(BaseModel):
    http_client: HttpClientConfig | None = Field(default=None)
    notification_client: NotificationClientConfig


class NotificationsSdkConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    notifications_sdk: NotificationsSdkParams
