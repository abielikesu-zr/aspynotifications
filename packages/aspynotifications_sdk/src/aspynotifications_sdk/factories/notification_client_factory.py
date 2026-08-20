import structlog
from aspynotifications_sdk.entities.config import NotificationClientConfig
from aspynotifications_sdk.ports.notifications_client_port import (
    INotificationsClientPort,
)
from aspyplugs.templates.typed_plugin_factory import TypedPluginFactory
from aspyplugs.z_plug_resolver import PluginDependencyResolver

logger = structlog.get_logger(__name__)


class NotificationClientFactory(
    TypedPluginFactory[INotificationsClientPort, NotificationClientConfig]
):
    plugin_group = "notifications_client"
    config_model_cls = NotificationClientConfig
    union_field = "adapter"
    discrimination_field = "type"
    config_field = "config"


def create_notification_client(
    config: dict, resolver: PluginDependencyResolver
) -> INotificationsClientPort:
    logger.debug(
        "Creating notification event store repository from config", config=config
    )
    factory = NotificationClientFactory(resolver=resolver)
    client = factory.create(config)
    logger.debug(
        "notification event store adapter created", client_type=type(client).__name__
    )
    return client
