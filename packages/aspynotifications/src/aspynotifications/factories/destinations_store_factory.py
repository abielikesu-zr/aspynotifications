import structlog
from aspyadapters.config.storage_adapter_config import StorageAdapterConfig
from aspyplugs.templates.typed_plugin_factory import TypedPluginFactory

from aspynotifications.ports.destinations_store_port import IDestinationStorePort

logger = structlog.get_logger(__name__)


class DestinationStoreFactory(
    TypedPluginFactory[IDestinationStorePort, StorageAdapterConfig]
):
    """Creates destination store adapters from typed configuration."""

    plugin_group = "destinations_store"
    config_model_cls = StorageAdapterConfig
    union_field = "adapter"
    discrimination_field = "type"
    config_field = "config"


def create_destinations_store(config: dict) -> IDestinationStorePort:
    """Create the configured destination store adapter."""

    logger.debug("Creating destinations store from configuration", config=config)
    factory = DestinationStoreFactory()
    store = factory.create(config)
    logger.debug("Destinations store adapter created", store_type=type(store).__name__)
    return store
