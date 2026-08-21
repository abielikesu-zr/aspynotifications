from dependency_injector import containers, providers

from aspyevents.factories.cloud_event_store_factory import (
    create_cloud_event_store,
)
from aspyevents.services.cloud_event_context_transformer import (
    CloudEventPolicyContextTransformer,
)
from aspyevents.services.cloud_event_service import CloudEventService
from aspyevents.services.events_facade_impl import EventsFacadeImpl


class AspyEventsContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    # --- 1. Infrastructure / Stores ---
    cloud_event_store = providers.Singleton(
        create_cloud_event_store,
        config=config.aspyevents.cloud_event_store,
    )

    cloud_event_service = providers.Singleton(
        CloudEventService,
        store=cloud_event_store,
        config=config.aspyevents.cloud_event_service,
    )

    context_transformer = providers.Singleton(
        CloudEventPolicyContextTransformer,
    )

    events_facade = providers.Singleton(
        EventsFacadeImpl,
        cloud_event_service=cloud_event_service,
        event_transformer=context_transformer,
        config=config.aspyevents.events_facade,
    )
