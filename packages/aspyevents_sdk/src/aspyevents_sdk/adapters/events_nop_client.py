from typing import Any

import structlog
from aspyevents_dtos.publish_event_request import PublishEventRequest
from aspyplugs.registry import register_plugin

from aspyevents_sdk.entities.config import NopClientConfig

from aspyevents_sdk.ports.events_client_port import (
    IEventsClientPort,
)

logger = structlog.get_logger(__name__)


@register_plugin("events_client", "NOP")
class EventsNopClient(IEventsClientPort):
    def __init__(self, config: dict[str, Any]):
        self.config = NopClientConfig.model_validate(config)

    async def publish(self, request: PublishEventRequest) -> str:
        logger.debug("Publish Nop", request=request, status=self.config.status)
        return "EventNop"
