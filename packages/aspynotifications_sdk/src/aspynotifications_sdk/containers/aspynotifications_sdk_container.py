from dependency_injector import containers, providers
from aspyplugs.z_plug_resolver import PluginDependencyResolver

from aspynotifications_sdk.aspynotifications_sdk import NotificationsSDK
from aspyadapters.adapters.http_client import AspyHttpClient
from aspynotifications_sdk.factories.notification_client_factory import (
    create_notification_client,
)

class NotificationsSdkContainer(containers.DeclarativeContainer):

    config = providers.Configuration()

    http_client = providers.Singleton(
        AspyHttpClient, config=config.notification_sdk.http_client
    )

    notification_client_resolver = providers.Singleton(
        PluginDependencyResolver,
        dependencies=providers.Dict({AspyHttpClient: http_client}),
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
