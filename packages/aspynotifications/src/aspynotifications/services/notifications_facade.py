from abc import ABC, abstractmethod

from aspynotifications_dtos.notifications_dtos import NotificationSubscriptionsDTO
from aspynotifications_dtos.notify_request import CreateNotifyRequest


class NotificationsFacade(ABC):
    @abstractmethod
    async def notify(self, request: CreateNotifyRequest) -> str:
        """Send a notification."""
        ...

    @abstractmethod
    async def get_subscriptions(self) -> NotificationSubscriptionsDTO:
        """Get notification subscription subjects."""
        ...
