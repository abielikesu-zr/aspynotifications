import structlog
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

from aspynotifications_sdk.ports.notifications_client_port import (
    INotificationsClientPort,
)

logger = structlog.get_logger(__name__)


class NotificationsSDK:
    def __init__(self, notifications_client: INotificationsClientPort):
        self._client = notifications_client

    async def notify(self, request: CreateNotifyRequest) -> str:
        logger.debug("notify sdk request", request=request)
        return await self._client.notify(request)

    async def create_notification_policy(
        self,
        request: CreateNotificationPolicyRequest,
    ) -> NotificationPolicyDTO:
        logger.debug("create notification policy sdk request", request=request)
        return await self._client.create_notification_policy(request)

    async def create_template(self, request: CreateTemplateRequest) -> TemplateDTO:
        logger.debug("create template sdk request", request=request)
        return await self._client.create_template(request)

    async def create_destination(
        self,
        request: CreateDestinationRequest,
    ) -> DestinationDTO:
        logger.debug("create destination sdk request", request=request)
        return await self._client.create_destination(request)

    async def create_notification_provider(
        self,
        request: CreateNotificationProviderRequest,
    ) -> NotificationProviderDTO:
        logger.debug("create notification provider sdk request", request=request)
        return await self._client.create_notification_provider(request)
