from abc import ABC, abstractmethod

from aspynotifications_dtos.notify_request import CreateNotifyRequest


class NotificationsFacade(ABC):
    @abstractmethod
    async def notify(self, request: CreateNotifyRequest) -> str:
        """Send a notification."""
        ...
