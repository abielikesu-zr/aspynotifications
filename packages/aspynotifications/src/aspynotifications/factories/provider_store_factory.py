import structlog
from aspyadapters.config.storage_adapter_config import StorageAdapterConfig
from aspyplugs.templates.typed_plugin_factory import TypedPluginFactory

from aspynotifications.ports.notification_provider_store import (
    NotificationProviderStore,
)

logger = structlog.get_logger(__name__)


class NotificationProviderStoreFactory(
    TypedPluginFactory[
        NotificationProviderStore,
        StorageAdapterConfig,
    ]
):
    """
    Factory class for creating NotificationProviderStore instances.

    Instantiates NotificationProviderStore implementations based on
    configuration.
    """

    plugin_group = "notification_provider_store"

    config_model_cls = StorageAdapterConfig

    union_field = "adapter"
    discrimination_field = "type"
    config_field = "config"


def create_notification_provider_store(
    config: dict,
) -> NotificationProviderStore:
    """
    Create a NotificationProviderStore instance from configuration.
    """
    logger.debug(
        "Creating notification provider store from config",
        config=config,
    )

    factory = NotificationProviderStoreFactory()
    client = factory.create(config)

    logger.debug(
        "Notification provider store adapter created",
        client_type=type(client).__name__,
    )

    return client
