import structlog
from aspyadapters.config.storage_adapter_config import StorageAdapterConfig
from aspyplugs.templates.typed_plugin_factory import TypedPluginFactory
from aspyevents_sdk.ports.events_client_port import IEventsClientPort

logger = structlog.get_logger(__name__)


class EventsStoreFactory(TypedPluginFactory[IEventsClientPort, StorageAdapterConfig]):
    plugin_group = "aspyevents_store"
    config_model_cls = StorageAdapterConfig
    union_field = "adapter"
    discrimination_field = "type"
    config_field = "config"


def create_event_store(config: dict) -> IEventsClientPort:
    logger.debug("Creating event store repository from config", config=config)
    factory = EventsStoreFactory()
    client = factory.create(config)
    logger.debug("event store adapter created", client_type=type(client).__name__)
    return client
