import structlog
from aspyconfig import get_config as aspy_get_config

from aspyevents_archive.config.archive_worker_config import ArchiveWorkerAppConfig
from aspyevents_archive.containers.archive_worker_container import (
    ArchiveWorkerContainer,
)
from aspyevents_archive.workers.event_archive_worker import EventsArchiveWorker

logger = structlog.get_logger(__name__)

# Singleton instances for the DI container and config.

_archive_worker_container: ArchiveWorkerContainer | None = None
_archive_worker_app_config: ArchiveWorkerAppConfig | None = None


def get_events_archive_worker_config() -> ArchiveWorkerAppConfig:
    """
    Provides the initialized ArchiveWorkerAppConfig Pydantic model,
    loading configuration only once.
    """
    global _archive_worker_app_config

    if _archive_worker_app_config is None:
        config = aspy_get_config()

        model = config.to_pydantic(ArchiveWorkerAppConfig)

        if not isinstance(model, ArchiveWorkerAppConfig):
            raise TypeError(
                "Expected ArchiveWorkerAppConfig from configuration system."
            )

        _archive_worker_app_config = model
        logger.debug("Archive worker configuration loaded and validated")

    return _archive_worker_app_config


def _initialize_container() -> ArchiveWorkerContainer:
    """
    Initializes the ArchiveWorkerContainer with the validated
    configuration.
    """
    global _archive_worker_container

    if _archive_worker_container is None:
        config = get_events_archive_worker_config()

        _archive_worker_container = ArchiveWorkerContainer()

        dict_config = config.model_dump()

        logger.debug("Wiring ArchiveWorkerContainer with validated configuration")

        _archive_worker_container.config.from_dict(dict_config)

        logger.info("Archive worker container initialized and wired via DI")

    return _archive_worker_container


def get_events_archive_worker() -> EventsArchiveWorker:
    """Return the EventsArchiveWorker singleton."""
    return _initialize_container().events_archive_worker()
