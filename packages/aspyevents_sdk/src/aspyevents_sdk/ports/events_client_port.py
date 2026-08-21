from typing import Protocol
from aspyevents_dtos.publish_event_request import PublishEventRequest

class IEventsClientPort(Protocol):
    async def publish(self, request: PublishEventRequest) -> str: ...
