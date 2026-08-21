import structlog
from aspyconfig import get_config as aspy_get_config

from aspyevents.config.app_config import AspyEventsAppConfig
from aspyevents.containers.events_container import AspyEventsContainer
from aspyevents.services.events_facade import EventsFacade

logger = structlog.get_logger(__name__)

# Singleton instances for the DI container and config.

_events_container: AspyEventsContainer | None = None
_events_app_config: AspyEventsAppConfig | None = None


def get_events_config() -> AspyEventsAppConfig:
    """
    Provides the initialized AspyEventsAppConfig Pydantic model,
    loading configuration only once.
    """
    global _events_app_config

    if _events_app_config is None:
        config = aspy_get_config()

        model = config.to_pydantic(AspyEventsAppConfig)

        if not isinstance(model, AspyEventsAppConfig):
            raise TypeError("Expected AspyEventsAppConfig from configuration system.")

        _events_app_config = model
        logger.debug("AspyEvents configuration loaded and validated")

    return _events_app_config


def _initialize_container() -> AspyEventsContainer:
    """
    Initializes the AspyEventsContainer with the validated configuration.
    """
    global _events_container

    if _events_container is None:
        config = get_events_config()

        _events_container = AspyEventsContainer()

        dict_config = config.model_dump()

        logger.debug("Wiring AspyEventsContainer with validated configuration")

        _events_container.config.from_dict(dict_config)

        logger.info("AspyEventsContainer container initialized and wired via DI")

    return _events_container


def get_events_facade() -> EventsFacade:
    """Return the EventsService singleton."""
    return _initialize_container().events_facade()
