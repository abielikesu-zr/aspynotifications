from dependency_injector import containers, providers

from aspyadapters.adapters.http_client import AspyHttpClient
from aspynotifications_sdk.adapters.notifications_rest_client import (
    NotificationsRestClient,
)
from aspynotifications_sdk.aspynotifications_sdk import NotificationsSDK
from aspynotifications_sdk.ports.notifications_client_port import (
    INotificationsClientPort,
)


class NotificationsSdkContainer(containers.DeclarativeContainer):

    config = providers.Configuration()

    http_client = providers.Singleton(
        AspyHttpClient,
        config=config.notifications_sdk.http_client,
    )

    notifications_client: providers.Provider[INotificationsClientPort] = providers.Singleton(
        NotificationsRestClient,
        http_client=http_client,
        config=config.notifications_sdk.notifications_client,
    )

    notifications_sdk = providers.Singleton(
        NotificationsSDK,
        notifications_client=notifications_client,
    )
