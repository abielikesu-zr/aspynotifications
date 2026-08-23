import structlog
from aspyconfig import get_config

from aspynotifications_rest.domain.config.rest_server_config import (
    AspyNotificationsRestAppConfig,
)

logger = structlog.get_logger(__name__)

_notifications_rest_app_config: AspyNotificationsRestAppConfig | None = None


def get_notifications_rest_config() -> AspyNotificationsRestAppConfig:
    global _notifications_rest_app_config

    if _notifications_rest_app_config is None:
        config = get_config()
        model = config.to_pydantic(AspyNotificationsRestAppConfig)

        _notifications_rest_app_config = model
        logger.debug("Notifications REST configuration loaded and validated")

    return _notifications_rest_app_config  # type: ignore
