import structlog
from aspyevents_dtos.notify_request import CreateNotifyRequest
from aspyevents_sdk.ports.events_client_port import IEventsClientPort

logger = structlog.get_logger(__name__)


class EventsSDK:
    def __init__(self, events_client: IEventsClientPort):
        self._client = events_client

    async def notify(self, request: CreateNotifyRequest) -> str:
        logger.debug("event sdk request", request=request)
        return await self._client.notify(request)
