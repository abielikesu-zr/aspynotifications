from typing import Literal

from aspyadapters.adapters.http_client_config import HttpClientConfig
from aspyadapters.config.storage_adapter_config import StorageAdapterConfig
from pydantic import BaseModel, ConfigDict, Field

from aspynotifications.config.cloud_template import (
    TemplateServiceConfig,
)
from aspynotifications.config.notification_config import NotificationPolicyServiceConfig
from aspynotifications.config.notification_facade_config import NotificationFacadeConfig
from aspynotifications.config.notification_provider_config import (
    NotificationProviderServiceConfig,
)


class DestinationsServiceConfig(BaseModel):
    """Typed configuration for DestinationsService."""

    model_config = ConfigDict(extra="forbid")

    keep: Literal["keep"] = "keep"


class AspynotificationsAppParams(BaseModel):
    policy_store: StorageAdapterConfig
    policy_service: NotificationPolicyServiceConfig

    destinations_store: StorageAdapterConfig
    destinations_service: DestinationsServiceConfig = Field(
        default_factory=DestinationsServiceConfig
    )

    template_store: StorageAdapterConfig
    template_service: TemplateServiceConfig

    notification_provider_store: StorageAdapterConfig
    notification_provider_service: NotificationProviderServiceConfig = Field(
        default_factory=NotificationProviderServiceConfig
    )
    notification_sender_http_client: HttpClientConfig = Field(
        default_factory=HttpClientConfig
    )

    notification_facade: NotificationFacadeConfig = Field(
        default_factory=NotificationFacadeConfig
    )


class AspyNotificationAppConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")

    aspynotifications: AspynotificationsAppParams
