from abc import ABC, abstractmethod

from aspynotifications_dtos.notifications_dtos import (
    CreateDestinationRequest,
    CreateNotificationPolicyRequest,
    CreateTemplateRequest,
    DestinationDTO,
    NotificationPolicyDTO,
    NotificationSubscriptionsDTO,
    TemplateDTO,
    UpdateDestinationRequest,
    UpdateTemplateRequest,
)
from aspynotifications_dtos.notify_event_request import CreateNotifyRequest
from aspynotifications_dtos.providers_dtos import (
    CreateNotificationProviderRequest,
    NotificationProviderDTO,
    UpdateNotificationProviderRequest,
)


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
    async def update_template(self, request: UpdateTemplateRequest) -> TemplateDTO:
        """Update a notification template."""
        ...

    @abstractmethod
    async def create_destination(
        self,
        request: CreateDestinationRequest,
    ) -> DestinationDTO:
        """Create a notification destination."""
        ...

    @abstractmethod
    async def update_destination(
        self,
        request: UpdateDestinationRequest,
    ) -> DestinationDTO:
        """Update a notification destination."""
        ...

    @abstractmethod
    async def create_notification_provider(
        self,
        request: CreateNotificationProviderRequest,
    ) -> NotificationProviderDTO:
        """Create a notification provider."""
        ...

    @abstractmethod
    async def update_notification_provider(
        self,
        request: UpdateNotificationProviderRequest,
    ) -> NotificationProviderDTO:
        """Update a notification provider."""
        ...
