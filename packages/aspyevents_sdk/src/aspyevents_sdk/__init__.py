from typing import Optional

import structlog
from aspyconfig import get_config as aspy_get_config

from aspyevents_sdk.aspyevents_sdk import EventsSDK
from aspyevents_sdk.containers.aspyevents_sdk_container import EventsSdkContainer
from aspyevents_sdk.entities.config import EventsSdkConfig

logger = structlog.get_logger(__name__)

_events_sdk_container: EventsSdkContainer | None = None
_events_sdk_config: EventsSdkConfig | None = None


def get_events_sdk_config() -> EventsSdkConfig:
    global _events_sdk_config

    if _events_sdk_config is None:
        config = aspy_get_config()

        model = config.to_pydantic(EventsSdkConfig)
        if not isinstance(model, EventsSdkConfig):
            raise TypeError("Expected EventsSdkConfig from config")

        _events_sdk_config = model
        logger.debug("Events SDK configuration loaded")

    return _events_sdk_config


def _initialize_container() -> EventsSdkContainer:
    global _events_sdk_container

    if _events_sdk_container is None:
        config = get_events_sdk_config()
        _events_sdk_container = EventsSdkContainer()
        dict_config = config.model_dump()
        logger.debug("Wiring EventsSdkContainer with configuration")
        _events_sdk_container.config.from_dict(dict_config)
        logger.info("Events SDK container initialized and wired via DI container.")

    return _events_sdk_container


def get_events_sdk() -> EventsSDK:
    container = _initialize_container()
    return container.events_sdk()
