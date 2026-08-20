from typing import Literal, Union

from pydantic import BaseModel, Field, HttpUrl

from aspyadapters.adapters.http_client_config import HttpClientConfig
from aspynats.config.nats_connection_config import NatsConnectionConfig


class RestClientParams(BaseModel):
    base_url: HttpUrl


class RestClientConfig(BaseModel):
    type: Literal["REST"]
    config: RestClientParams = Field(...)


class NatsClientConfig(BaseModel):
    type: Literal["NATS"] = "NATS"
    config: NatsConnectionConfig = Field(default_factory=NatsConnectionConfig)

class NotificationsSdkParams(BaseModel):
    http_client: HttpClientConfig
    client: Union[RestClientConfig, NatsClientConfig] = Field(
        default_factory=NatsClientConfig, discriminator="type"
    )


class NotificationsSdkConfig(BaseModel):
    notifications_sdk: NotificationsSdkParams
