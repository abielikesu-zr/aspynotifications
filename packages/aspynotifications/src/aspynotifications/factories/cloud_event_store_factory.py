import structlog
from aspyadapters.config.storage_adapter_config import StorageAdapterConfig
from aspyplugs.templates.typed_plugin_factory import TypedPluginFactory

from aspynotifications.ports.cloud_event_port import ICloudEventStorePort

logger = structlog.get_logger(__name__)


class CloudEventStoreFactory(
    TypedPluginFactory[ICloudEventStorePort, StorageAdapterConfig]
):
    plugin_group = "cloud_event_store"
    config_model_cls = StorageAdapterConfig
    union_field = "adapter"
    discrimination_field = "type"
    config_field = "config"


def create_cloud_event_store(config: dict) -> ICloudEventStorePort:
    logger.debug("Creating cloud event store repository from config", config=config)
    factory = CloudEventStoreFactory()
    client = factory.create(config)
    logger.debug("Cloud event store adapter created", client_type=type(client).__name__)
    return client
