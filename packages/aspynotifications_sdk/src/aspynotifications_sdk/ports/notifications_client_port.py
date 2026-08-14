from typing import Protocol

from aspynotifications_dtos.cloud_event_dto import CloudEventDTO
from aspynotifications_dtos.notify_request import CreateNotifyRequest


class INotificationsClientPort(Protocol):
    async def notify(self, request: CreateNotifyRequest) -> str: ...
