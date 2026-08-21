from typing import Protocol
from aspyevents_dtos.notify_request import CreateNotifyRequest

class IEventsClientPort(Protocol):
    async def notify(self, request: CreateNotifyRequest) -> str: ...
