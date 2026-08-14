from typing import Any, Dict, List, Optional

import structlog

from aspyconfig import get_config
from aspynotifications_rest.domain.config.rest_server_config import (
    AspyNotificationsRestAppConfig,
)

logger = structlog.get_logger(__name__)

_notifications_rest_app_config: Optional[AspyNotificationsRestAppConfig] = None


def load_notifications_rest_config(
    *,
    cli_config: Optional[Dict[str, Any]] = None,
    user_config_paths: Optional[List[str]] = None,
    local_package_monoconfig: Optional[List[str]] = None,
    app_defaults: Optional[Dict[str, Any]] = None,
) -> None:
    config = get_config()
    config.register_common_config(
        cli_config=cli_config,
        local_config_paths=local_package_monoconfig,
        user_config_paths=user_config_paths,
        app_defaults=app_defaults,
    )
    config.load()


def get_notifications_rest_config() -> AspyNotificationsRestAppConfig:
    global _notifications_rest_app_config

    if _notifications_rest_app_config is None:
        config = get_config()
        model = config.to_pydantic(AspyNotificationsRestAppConfig)

        _notifications_rest_app_config = model
        logger.debug("Notifications REST configuration loaded and validated")

    return _notifications_rest_app_config
