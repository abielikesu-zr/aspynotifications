import structlog
from aspyplugs.templates.typed_plugin_factory import TypedPluginFactory
from aspyplugs.z_plug_resolver import PluginDependencyResolver

from aspyevents_sdk.entities.config import EventClientConfig
from aspyevents_sdk.ports.events_client_port import (
    IEventsClientPort,
)

logger = structlog.get_logger(__name__)


class EventsClientFactory(TypedPluginFactory[IEventsClientPort, EventClientConfig]):
    plugin_group = "events_client"
    config_model_cls = EventClientConfig
    union_field = "adapter"
    discrimination_field = "type"
    config_field = "config"


def create_events_client(
    config: dict, resolver: PluginDependencyResolver
) -> IEventsClientPort:
    logger.debug("Creating event store repository from config", config=config)
    factory = EventsClientFactory(resolver=resolver)
    client = factory.create(config)
    logger.debug("event store adapter created", client_type=type(client).__name__)
    return client
