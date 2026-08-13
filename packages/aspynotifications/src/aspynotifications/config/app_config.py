from aspyadapters.config.storage_adapter_config import (
    LocalFSAdapterConfig,
    MongoDBAdapterConfig,
    StorageAdapterConfig,  # Reusing the base adapter config
)
from pydantic import BaseModel, ConfigDict, Field

from aspynotifications.config.notification_config import NotificationPolicyServiceConfig


class DestinationsStoreAdapterConfig(BaseModel):
    """Discriminated configuration for destination store adapters."""

    model_config = ConfigDict(extra="forbid")

    adapter: LocalFSAdapterConfig | MongoDBAdapterConfig = Field(
        ...,
        discriminator="type",
        description="Configuration for the selected destination store adapter",
    )


class DestinationsServiceConfig(BaseModel):
    """Typed configuration for DestinationsService."""

    model_config = ConfigDict(extra="forbid")


class AspynotificationsAppParams(BaseModel):
    policy_store: StorageAdapterConfig
    policy_service: NotificationPolicyServiceConfig

    destinations_store: DestinationsStoreAdapterConfig
    destinations_service: DestinationsServiceConfig = Field(
        default_factory=DestinationsServiceConfig
    )


class AspynotificationsAppConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")

    aspynotifications: AspynotificationsAppParams
