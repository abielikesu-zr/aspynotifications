from dependency_injector import containers, providers
from aspynotifications_sdk.adapters.notifications_nats_client import (
    NotificationsNatsClient,
)
from aspynotifications_sdk.aspynotifications_sdk import NotificationsSDK


class NotificationsSdkContainer(containers.DeclarativeContainer):

    config = providers.Configuration()

    notifications_client = providers.Singleton(
        NotificationsNatsClient,
        config=config.notifications_sdk.client
    )

    notifications_sdk = providers.Singleton(
        NotificationsSDK,
        notifications_client=notifications_client,
    )
