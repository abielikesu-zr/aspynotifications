from abc import ABC, abstractmethod

from aspyevents_dtos.notify_request import CreateNotifyRequest


class EventsFacade(ABC):
    @abstractmethod
    async def notify(self, request: CreateNotifyRequest) -> str:
        """Send a notification."""
        ...
