import structlog
from aspyadapters.config.storage_adapter_config import StorageAdapterConfig
from aspynotifications_sdk.ports.notifications_client_port import INotificationsClientPort
from aspyplugs.templates.typed_plugin_factory import TypedPluginFactory

logger = structlog.get_logger(__name__)


class NotificationStoreFactory(
    TypedPluginFactory[INotificationsClientPort, StorageAdapterConfig]
):
    plugin_group = "notification_event_store"
    config_model_cls = StorageAdapterConfig
    union_field = "adapter"
    discrimination_field = "type"
    config_field = "config"


def create_notification_event_store(config: dict) -> INotificationsClientPort:
    logger.debug("Creating notification event store repository from config", config=config)
    factory = NotificationStoreFactory()
    client = factory.create(config)
    logger.debug("notification event store adapter created", client_type=type(client).__name__)
    return client
