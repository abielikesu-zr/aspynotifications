from typing import Literal

from pydantic import BaseModel, Field

from aspynats.config.nats_connection_config import NatsConnectionConfig
from aspynats.config.nats_stream_config import NatsStreamConfig


class NatsClientConfig(BaseModel):

    connection: NatsConnectionConfig = Field(
        default_factory=NatsConnectionConfig,
        description="Name of the JetStream stream used to store CloudEvents.",
    )
    stream: NatsStreamConfig = Field(
        default_factory=NatsStreamConfig,
        description="Subject pattern used by the stream to capture CloudEvents.",
    )


class NatsClientAdapterConfig(BaseModel):
    type: Literal["NATS"] = "NATS"
    config: NatsClientConfig = Field(default_factory=NatsClientConfig)
