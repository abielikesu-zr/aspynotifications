from typing import Union

from aspyadapters.config.storage_adapter_config import (
    LocalFSAdapterConfig,
    MongoDBAdapterConfig,
)
from pydantic import BaseModel, ConfigDict, Field


class DestinationsStoreAdapterConfig(BaseModel):
    """Discriminated configuration for destination store adapters."""

    model_config = ConfigDict(extra="forbid")

    adapter: Union[LocalFSAdapterConfig, MongoDBAdapterConfig] = Field(
        ...,
        discriminator="type",
        description="Configuration for the selected destination store adapter",
    )


class DestinationsServiceConfig(BaseModel):
    """Typed configuration for DestinationsService."""

    model_config = ConfigDict(extra="forbid")


class AppConfigParams(BaseModel):
    destinations_store: DestinationsStoreAdapterConfig
    destinations_service: DestinationsServiceConfig


class AppConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")

    destinations: AppConfigParams
