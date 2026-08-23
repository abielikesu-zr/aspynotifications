import structlog
from aspyevents_dtos.publish_event_request import PublishEventRequest

from aspyevents_sdk.ports.events_client_port import IEventsClientPort

logger = structlog.get_logger(__name__)


class EventsSDK:
    def __init__(self, events_client: IEventsClientPort):
        self._client = events_client

    async def publish(self, request: PublishEventRequest) -> str:
        logger.debug("publish event sdk request", request=request)
        return await self._client.publish(request)
