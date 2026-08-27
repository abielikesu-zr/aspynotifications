from typing import Literal

from aspyadapters.adapters.http_client_config import HttpClientConfig
from aspynats.config.nats_client_config import NatsClientAdapterConfig
from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class RestClientConfig(BaseModel):
    base_url: HttpUrl


class RestClientAdapterConfig(BaseModel):
    type: Literal["REST"] = "REST"
    config: RestClientConfig = Field(...)


class NopClientConfig(BaseModel):
    status: str = "ok"


class NopClientAdapterConfig(BaseModel):
    type: Literal["NOP"] = "NOP"
    config: NopClientConfig = Field(...)


class EventClientConfig(BaseModel):
    adapter: (
        NopClientAdapterConfig | RestClientAdapterConfig | NatsClientAdapterConfig
    ) = Field(..., discriminator="type")


class EventsSdkParams(BaseModel):
    http_client: HttpClientConfig | None = Field(default=None)
    events_client: EventClientConfig


class EventsSdkConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    events_sdk: EventsSdkParams
