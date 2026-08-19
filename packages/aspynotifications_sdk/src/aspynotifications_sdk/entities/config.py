from typing import Literal, Union

from pydantic import BaseModel, Field, HttpUrl, model_validator

from aspyadapters.adapters.http_client_config import HttpClientConfig


class RestClientParams(BaseModel):
    base_url: HttpUrl


class NatsClientParams(BaseModel):
    nats_url: str = Field(...)

    @model_validator(mode="before")
    def normalize_nats_url(cls, values):
        if "nats_url" in values and isinstance(values["nats_url"], str):
            values["nats_url"] = values["nats_url"].rstrip("/")
        return values


class RestClientConfig(BaseModel):
    type: Literal["REST"]
    config: RestClientParams = Field(...)


class NatsClientConfig(BaseModel):
    type: Literal["NATS"]
    config: NatsClientParams = Field(...)


class NotificationsClientConfig(BaseModel):
    client: Union[RestClientConfig, NatsClientConfig] = Field(
        ..., discriminator="type"
    )


class NotificationsSdkParams(BaseModel):
    http_client: HttpClientConfig
    client: NotificationsClientConfig


class NotificationsSdkConfig(BaseModel):
    notifications_sdk: NotificationsSdkParams
