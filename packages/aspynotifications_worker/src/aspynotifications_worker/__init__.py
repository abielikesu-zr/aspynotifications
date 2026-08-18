import structlog
from aspyconfig import get_config as aspy_get_config

from aspynotifications_worker.config.notification_worker_config import (
    AspynotificationsWorkerAppConfig,
)
from aspynotifications_worker.containers.notifications_worker_container import (
    AspyNotificationsWorkerContainer,
)
from aspynotifications_worker.workers.notifications_worker import NotificationsWorker

logger = structlog.get_logger(__name__)

# Singleton instances for the DI container and config.

_notifications_worker_container: AspyNotificationsWorkerContainer | None = None
_notifications_worker_app_config: AspynotificationsWorkerAppConfig | None = None


def get_notifications_worker_config() -> AspynotificationsWorkerAppConfig:
    """
    Provides the initialized AspynotificationsWorkerAppConfig Pydantic model,
    loading configuration only once.
    """
    global _notifications_worker_app_config

    if _notifications_worker_app_config is None:
        config = aspy_get_config()

        model = config.to_pydantic(AspynotificationsWorkerAppConfig)

        if not isinstance(model, AspynotificationsWorkerAppConfig):
            raise TypeError(
                "Expected AspynotificationsWorkerAppConfig from configuration system."
            )

        _notifications_worker_app_config = model
        logger.debug("Notifications worker configuration loaded and validated")

    return _notifications_worker_app_config


def _initialize_container() -> AspyNotificationsWorkerContainer:
    """
    Initializes the AspyNotificationsWorkerContainer with the validated
    configuration.
    """
    global _notifications_worker_container

    if _notifications_worker_container is None:
        config = get_notifications_worker_config()

        _notifications_worker_container = AspyNotificationsWorkerContainer()

        dict_config = config.model_dump()

        logger.debug(
            "Wiring AspyNotificationsWorkerContainer with validated configuration"
        )

        _notifications_worker_container.config.from_dict(dict_config)

        logger.info("Notifications worker container initialized and wired via DI")

    return _notifications_worker_container


def get_notifications_worker() -> NotificationsWorker:
    """Return the NotificationsWorker singleton."""
    return _initialize_container().notifications_worker()
