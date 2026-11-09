from aspyadapters.adapters.http_client import AspyHttpClient
from aspynotifications import get_notification_facade
from aspynotifications.services.notifications_facade import NotificationsFacade
from aspyplugs.z_plug_resolver import PluginDependencyResolver
from dependency_injector import containers, providers

from aspynotifications_sdk.aspynotifications_sdk import NotificationsSDK
from aspynotifications_sdk.factories.notification_client_factory import (
    create_notification_client,
)


class NotificationsSdkContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    http_client = providers.Singleton(
        AspyHttpClient, config=config.notifications_sdk.http_client
    )

    notifications_facade = providers.Singleton(get_notification_facade)

    notification_client_resolver = providers.Singleton(
        PluginDependencyResolver,
        dependencies=providers.Dict(
            {
                AspyHttpClient: http_client.provider,
                NotificationsFacade: notifications_facade.provider,
            }
        ),
    )

    notifications_client = providers.Singleton(
        create_notification_client,
        config=config.notifications_sdk.notification_client,
        resolver=notification_client_resolver,
    )

    notifications_sdk = providers.Singleton(
        NotificationsSDK,
        notifications_client=notifications_client,
    )
