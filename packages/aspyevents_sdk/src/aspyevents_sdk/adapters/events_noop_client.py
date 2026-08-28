from typing import Any

import structlog
from aspyevents_dtos.publish_event_request import PublishEventRequest
from aspyplugs.registry import register_plugin

from aspyevents_sdk.entities.config import NoopClientConfig

from aspyevents_sdk.ports.events_client_port import (
    IEventsClientPort,
)

logger = structlog.get_logger(__name__)


@register_plugin("events_client", "NOOP")
class EventsNopClient(IEventsClientPort):
    def __init__(self, config: dict[str, Any]):
        self.config = NoopClientConfig.model_validate(config)

    async def publish(self, request: PublishEventRequest) -> str:
        logger.debug("Publish Noop", request=request, status=self.config.status)
        return "EventNoop"
