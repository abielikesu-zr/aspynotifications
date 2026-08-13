from dependency_injector import containers, providers

from aspynotifications.factories.template_store_factory import create_template_store
from aspynotifications.services.template_service import TemplateService


class TemplateContainer(containers.DeclarativeContainer):

    config = providers.Configuration()

    template_store = providers.Singleton(
        create_template_store,
        config=config.template.template_store,
    )

    template_service = providers.Singleton(
        TemplateService,
        store=template_store,
        config=config.template.template_service,
    )
