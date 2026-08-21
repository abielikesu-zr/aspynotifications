from typing import Protocol

from aspynotifications_dtos.notifications_dtos import (
    CreateDestinationRequest,
    CreateNotificationPolicyRequest,
    CreateTemplateRequest,
    DestinationDTO,
    NotificationPolicyDTO,
    TemplateDTO,
)
from aspynotifications_dtos.notify_event_request import CreateNotifyRequest
from aspynotifications_dtos.providers_dtos import (
    CreateNotificationProviderRequest,
    NotificationProviderDTO,
)


class INotificationsClientPort(Protocol):
    async def notify(self, request: CreateNotifyRequest) -> str: ...

    async def create_notification_policy(
        self,
        request: CreateNotificationPolicyRequest,
    ) -> NotificationPolicyDTO: ...

    async def create_template(
        self,
        request: CreateTemplateRequest,
    ) -> TemplateDTO: ...

    async def create_destination(
        self,
        request: CreateDestinationRequest,
    ) -> DestinationDTO: ...

    async def create_notification_provider(
        self,
        request: CreateNotificationProviderRequest,
    ) -> NotificationProviderDTO: ...
