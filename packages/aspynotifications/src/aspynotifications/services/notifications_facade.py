from abc import ABC, abstractmethod

from aspynotifications_dtos.notifications_dtos import (
    CreateDestinationRequest,
    CreateNotificationPolicyRequest,
    CreateTemplateRequest,
    DestinationDTO,
    NotificationPolicyDTO,
    NotificationSubscriptionsDTO,
    TemplateDTO,
)
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

    @abstractmethod
    async def create_notification_policy(
        self,
        request: CreateNotificationPolicyRequest,
    ) -> NotificationPolicyDTO:
        """Create a notification policy."""
        ...

    @abstractmethod
    async def create_template(self, request: CreateTemplateRequest) -> TemplateDTO:
        """Create a notification template."""
        ...

    @abstractmethod
    async def create_destination(
        self,
        request: CreateDestinationRequest,
    ) -> DestinationDTO:
        """Create a notification destination."""
        ...
