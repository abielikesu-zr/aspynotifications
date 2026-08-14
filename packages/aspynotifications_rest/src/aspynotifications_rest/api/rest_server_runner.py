import structlog
from aspyrest.runner.base_rest_server_runner import BaseRestServerRunner
from aspynotifications_rest.domain.config.rest_server_config import (
    AspyNotificationsRestServerConfig,
)

logger = structlog.get_logger(__name__)


class AspyNotificationsRestServerRunner(BaseRestServerRunner):
    DEFAULT_CONFIG = AspyNotificationsRestServerConfig().model_dump()
    CONFIG_ROOT = "aspynotifications_rest"
    PACKAGE_NAME = __package__ or ""
