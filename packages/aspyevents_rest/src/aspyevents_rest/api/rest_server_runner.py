import structlog
from aspyrest.runner.base_rest_server_runner import BaseRestServerRunner

from aspyevents_rest.domain.config.rest_server_config import (
    AspyEventsRestServerConfig,
)

logger = structlog.get_logger(__name__)


class AspyEventsRestServerRunner(BaseRestServerRunner):
    DEFAULT_CONFIG = AspyEventsRestServerConfig().model_dump()
    CONFIG_ROOT = "aspyevents_rest"
    PACKAGE_NAME = __package__ or ""
