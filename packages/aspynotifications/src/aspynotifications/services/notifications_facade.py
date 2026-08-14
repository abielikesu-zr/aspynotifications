from abc import ABC, abstractmethod

from aspynotifications_dtos.cloud_event_dto import CloudEventDTO


class NotificationsFacade(ABC):
    @abstractmethod
    async def notify(self, requestDTO: CloudEventDTO) -> None:
        """Send a notification."""
        ...
