from typing import Protocol

from aspynotifications_dtos.notifications_dtos import (
    ActivateNotificationPolicyRequest,
    CreateDestinationRequest,
    CreateNotificationPolicyRequest,
    CreateTemplateRequest,
    DeactivateNotificationPolicyRequest,
    DestinationDTO,
    NotificationPolicyDTO,
    TemplateDTO,
    UpdateDestinationRequest,
    UpdateNotificationPolicyRequest,
    UpdateTemplateRequest,
)
from aspynotifications_dtos.notify_event_request import CreateNotifyRequest
from aspynotifications_dtos.providers_dtos import (
    CreateNotificationProviderRequest,
    NotificationProviderDTO,
    UpdateNotificationProviderRequest,
)


class INotificationsClientPort(Protocol):
    async def notify(self, request: CreateNotifyRequest) -> str: ...

    async def create_notification_policy(
        self,
        request: CreateNotificationPolicyRequest,
    ) -> NotificationPolicyDTO: ...

    async def update_notification_policy(
        self,
        request: UpdateNotificationPolicyRequest,
    ) -> NotificationPolicyDTO: ...

    async def activate_notification_policy(
        self,
        request: ActivateNotificationPolicyRequest,
    ) -> NotificationPolicyDTO: ...

    async def deactivate_notification_policy(
        self,
        request: DeactivateNotificationPolicyRequest,
    ) -> NotificationPolicyDTO: ...

    async def create_template(
        self,
        request: CreateTemplateRequest,
    ) -> TemplateDTO: ...

    async def update_template(
        self,
        request: UpdateTemplateRequest,
    ) -> TemplateDTO: ...

    async def create_destination(
        self,
        request: CreateDestinationRequest,
    ) -> DestinationDTO: ...

    async def update_destination(
        self,
        request: UpdateDestinationRequest,
    ) -> DestinationDTO: ...

    async def create_notification_provider(
        self,
        request: CreateNotificationProviderRequest,
    ) -> NotificationProviderDTO: ...

    async def update_notification_provider(
        self,
        request: UpdateNotificationProviderRequest,
    ) -> NotificationProviderDTO: ...
