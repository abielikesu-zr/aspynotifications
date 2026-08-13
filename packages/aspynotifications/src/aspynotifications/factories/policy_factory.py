import structlog
from aspyadapters.config.storage_adapter_config import StorageAdapterConfig
from aspyplugs.templates.typed_plugin_factory import TypedPluginFactory

from aspynotifications.ports.policies_store import NotificationPolicyStore

logger = structlog.get_logger(__name__)


class NotificationPolicyStoreFactory(
    TypedPluginFactory[
        NotificationPolicyStore,
        StorageAdapterConfig,
    ]
):
    """
    Factory class for creating NotificationPolicyStore instances.

    Instantiates NotificationPolicyStore implementations based on
    configuration.
    """

    # Matches the @register_plugin group name used by the
    # NotificationPolicyStore adapters.
    plugin_group = "notification_policy_store"

    # Uses the shared storage configuration model.
    config_model_cls = StorageAdapterConfig

    # Fields for the TypedPluginFactory to locate the adapter configuration.
    union_field = "adapter"
    discrimination_field = "type"
    config_field = "config"


def create_notification_policy_store(
    config: dict,
) -> NotificationPolicyStore:
    """
    Create a NotificationPolicyStore instance from configuration.
    """
    logger.debug(
        "Creating notification policy store from config",
        config=config,
    )

    factory = NotificationPolicyStoreFactory()
    client = factory.create(config)

    logger.debug(
        "Notification policy store adapter created",
        client_type=type(client).__name__,
    )

    return client
