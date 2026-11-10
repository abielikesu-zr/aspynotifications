from aspynotifications.services.notifications_facade import NotificationsFacade
from aspynotifications_dtos.exceptions import ResourceAlreadyExistsError
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
    UpdateNotificationPolicyByNameRequest,
    UpdateNotificationPolicyRequest,
    UpdateTemplateRequest,
)
from aspynotifications_dtos.notify_event_request import CreateNotifyRequest
from aspynotifications_dtos.providers_dtos import (
    CreateNotificationProviderRequest,
    NotificationProviderDTO,
    UpdateNotificationProviderRequest,
)
from aspyplugs.registry import register_plugin

from aspynotifications_sdk.entities.config import FacadeClientConfig
from aspynotifications_sdk.errors import ConflictError
from aspynotifications_sdk.ports.notifications_client_port import (
    INotificationsClientPort,
)


@register_plugin("notifications_client", "FACADE")
class NotificationsFacadeClient(INotificationsClientPort):
    """Delegate notification operations directly to the application facade."""

    def __init__(self, config: dict, facade: NotificationsFacade):
        self.config = FacadeClientConfig.model_validate(config)
        self._facade = facade

    async def notify(self, request: CreateNotifyRequest) -> str:
        return await self._facade.notify(request)

    async def create_notification_policy(
        self, request: CreateNotificationPolicyRequest
    ) -> NotificationPolicyDTO:
        try:
            return await self._facade.create_notification_policy(request)
        except ResourceAlreadyExistsError as exc:
            raise ConflictError(str(exc)) from exc

    async def update_notification_policy(
        self, request: UpdateNotificationPolicyRequest
    ) -> NotificationPolicyDTO:
        return await self._facade.update_notification_policy(request)

    async def update_notification_policy_by_name(
        self, request: UpdateNotificationPolicyByNameRequest
    ) -> NotificationPolicyDTO:
        return await self._facade.update_notification_policy_by_name(request)

    async def activate_notification_policy(
        self, request: ActivateNotificationPolicyRequest
    ) -> NotificationPolicyDTO:
        return await self._facade.activate_notification_policy(request)

    async def deactivate_notification_policy(
        self, request: DeactivateNotificationPolicyRequest
    ) -> NotificationPolicyDTO:
        return await self._facade.deactivate_notification_policy(request)

    async def create_template(self, request: CreateTemplateRequest) -> TemplateDTO:
        try:
            return await self._facade.create_template(request)
        except ResourceAlreadyExistsError as exc:
            raise ConflictError(str(exc)) from exc

    async def update_template(self, request: UpdateTemplateRequest) -> TemplateDTO:
        return await self._facade.update_template(request)

    async def create_destination(
        self, request: CreateDestinationRequest
    ) -> DestinationDTO:
        try:
            return await self._facade.create_destination(request)
        except ResourceAlreadyExistsError as exc:
            raise ConflictError(str(exc)) from exc

    async def update_destination(
        self, request: UpdateDestinationRequest
    ) -> DestinationDTO:
        return await self._facade.update_destination(request)

    async def create_notification_provider(
        self, request: CreateNotificationProviderRequest
    ) -> NotificationProviderDTO:
        try:
            return await self._facade.create_notification_provider(request)
        except ResourceAlreadyExistsError as exc:
            raise ConflictError(str(exc)) from exc

    async def update_notification_provider(
        self, request: UpdateNotificationProviderRequest
    ) -> NotificationProviderDTO:
        return await self._facade.update_notification_provider(request)
