import structlog

from aspynotifications_dtos.cloud_event_dto import CloudEventDTO
from aspynotifications_dtos.notify_request import CreateNotifyRequest
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