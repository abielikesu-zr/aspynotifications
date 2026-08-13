import structlog

from aspyadapters.config.storage_adapter_config import StorageAdapterConfig
from aspyplugs.templates.typed_plugin_factory import TypedPluginFactory
from aspynotifications.ports.template_port import ITemplateStorePort

logger = structlog.get_logger(__name__)


class TemplateStoreFactory(
    TypedPluginFactory[ITemplateStorePort, StorageAdapterConfig]
):
    plugin_group = "template_store"
    config_model_cls = StorageAdapterConfig
    union_field = "adapter"
    discrimination_field = "type"
    config_field = "config"


def create_template_store(config: dict) -> ITemplateStorePort:
    logger.debug("Creating template store repository from config", config=config)
    factory = TemplateStoreFactory()
    client = factory.create(config)
    logger.debug("Template store adapter created", client_type=type(client).__name__)
    return client
