import structlog
from aspyconfig import get_config as aspy_get_config

from aspyevents_archive.config.archive_worker_config import ArchiveWorkerAppConfig
from aspyevents_archive.containers.notifications_worker_container import (
    ArchiveWorkerContainer,
)
from aspyevents_archive.workers.event_archive_worker import EventsArchiveWorker

logger = structlog.get_logger(__name__)

# Singleton instances for the DI container and config.

_notifications_worker_container: ArchiveWorkerContainer | None = None
_notifications_worker_app_config: ArchiveWorkerAppConfig | None = None


def get_notifications_worker_config() -> ArchiveWorkerAppConfig:
    """
    Provides the initialized ArchiveWorkerAppConfig Pydantic model,
    loading configuration only once.
    """
    global _notifications_worker_app_config

    if _notifications_worker_app_config is None:
        config = aspy_get_config()

        model = config.to_pydantic(ArchiveWorkerAppConfig)

        if not isinstance(model, ArchiveWorkerAppConfig):
            raise TypeError(
                "Expected ArchiveWorkerAppConfig from configuration system."
            )

        _notifications_worker_app_config = model
        logger.debug("Notifications worker configuration loaded and validated")

    return _notifications_worker_app_config


def _initialize_container() -> ArchiveWorkerContainer:
    """
    Initializes the ArchiveWorkerContainer with the validated
    configuration.
    """
    global _notifications_worker_container

    if _notifications_worker_container is None:
        config = get_notifications_worker_config()

        _notifications_worker_container = ArchiveWorkerContainer()

        dict_config = config.model_dump()

        logger.debug("Wiring ArchiveWorkerContainer with validated configuration")

        _notifications_worker_container.config.from_dict(dict_config)

        logger.info("Notifications worker container initialized and wired via DI")

    return _notifications_worker_container


def get_events_archive_worker() -> EventsArchiveWorker:
    """Return the EventsArchiveWorker singleton."""
    return _initialize_container().notifications_worker()
