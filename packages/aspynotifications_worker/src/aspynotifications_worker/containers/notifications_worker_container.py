from aspynotifications import get_notification_facade
from dependency_injector import containers, providers

from aspynotifications_worker.workers.notifications_worker import NotificationsWorker


class AspyNotificationsWorkerContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    notifications_facade = providers.Singleton(
        get_notification_facade,
    )

    notifications_worker = providers.Singleton(
        NotificationsWorker,
        config=config.aspynotifications_worker.nats_worker,
        notifications_facade=notifications_facade,
    )
