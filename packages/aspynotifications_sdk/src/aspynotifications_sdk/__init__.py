from typing import Optional

import structlog
from aspyconfig import get_config as aspy_get_config

from aspynotifications_sdk.aspynotifications_sdk import NotificationsSDK
from aspynotifications_sdk.containers.aspynotifications_sdk_container import (
    NotificationsSdkContainer,
)
from aspynotifications_sdk.entities.config import NotificationsSdkConfig

logger = structlog.get_logger(__name__)

_notifications_sdk_container: Optional[NotificationsSdkContainer] = None
_notifications_sdk_config: Optional[NotificationsSdkConfig] = None


def get_notifications_sdk_config() -> NotificationsSdkConfig:
    global _notifications_sdk_config

    if _notifications_sdk_config is None:
        config = aspy_get_config()

        model = config.to_pydantic(NotificationsSdkConfig)
        if not isinstance(model, NotificationsSdkConfig):
            raise TypeError("Expected NotificationsSdkConfig from config")

        _notifications_sdk_config = model
        logger.debug("Notifications SDK configuration loaded")

    return _notifications_sdk_config


def _initialize_container() -> NotificationsSdkContainer:
    global _notifications_sdk_container

    if _notifications_sdk_container is None:
        config = get_notifications_sdk_config()
        _notifications_sdk_container = NotificationsSdkContainer()
        dict_config = config.model_dump()
        logger.debug("Wiring NotificationsSdkContainer with configuration")
        _notifications_sdk_container.config.from_dict(dict_config)
        logger.info("Notifications SDK container initialized and wired via DI container.")

    return _notifications_sdk_container


def get_notifications_sdk() -> NotificationsSDK:
    container = _initialize_container()
    return container.notifications_sdk()
