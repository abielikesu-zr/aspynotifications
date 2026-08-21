from dependency_injector import containers, providers
from aspyevents_sdk.aspyevents_sdk import EventsSDK
from aspyplugs.z_plug_resolver import PluginDependencyResolver

from aspyadapters.adapters.http_client import AspyHttpClient
from aspyevents_sdk.factories.events_client_factory import (
    create_events_client,
)

class EventsSdkContainer(containers.DeclarativeContainer):

    config = providers.Configuration()

    http_client = providers.Singleton(
        AspyHttpClient, config=config.events_sdk.http_client
    )

    events_client_resolver = providers.Singleton(
        PluginDependencyResolver,
        dependencies=providers.Dict({AspyHttpClient: http_client}),
    )

    events_client = providers.Singleton(
        create_events_client,
        config=config.events_sdk.events_client,
        resolver=events_client_resolver,
    )

    events_sdk = providers.Singleton(
        EventsSDK,
        events_client=events_client,
    )
