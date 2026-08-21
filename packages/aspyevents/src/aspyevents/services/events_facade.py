from abc import ABC, abstractmethod

from aspyevents_dtos.save_event_request import SaveEventRequest


class EventsFacade(ABC):
    @abstractmethod
    async def save_event(self, request: SaveEventRequest) -> str:
        """Send a notification."""
        ...
