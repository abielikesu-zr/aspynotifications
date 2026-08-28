from typing import Literal

from aspyadapters.adapters.http_client_config import HttpClientConfig
from aspynats.config.nats_client_config import NatsClientAdapterConfig
from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class RestClientConfig(BaseModel):
    base_url: HttpUrl


class RestClientAdapterConfig(BaseModel):
    type: Literal["REST"] = "REST"
    config: RestClientConfig = Field(...)


class NoopClientConfig(BaseModel):
    status: str = "ok"


class NoopClientAdapterConfig(BaseModel):
    type: Literal["NOOP"] = "NOOP"
    config: NoopClientConfig = Field(...)


class EventClientConfig(BaseModel):
    adapter: (
        NoopClientAdapterConfig | RestClientAdapterConfig | NatsClientAdapterConfig
    ) = Field(..., discriminator="type")


class EventsSdkParams(BaseModel):
    http_client: HttpClientConfig | None = Field(default=None)
    events_client: EventClientConfig


class EventsSdkConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    events_sdk: EventsSdkParams
