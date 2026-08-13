from aspynotifications.services.cloud_event_service import CloudEventService
from dependency_injector import containers, providers

from aspynotifications.factories.cloud_event_store_factory import (
    create_cloud_event_store,
)


class AspyNotificationsContainer(containers.DeclarativeContainer):

    config = providers.Configuration()

    cloud_event_store = providers.Singleton(
        create_cloud_event_store,
        config=config.cloud_event.cloud_event_store,
    )

    cloud_event_service = providers.Singleton(
        CloudEventService,
        store=cloud_event_store,
        config=config.excuses.excuses_service,
    )
    