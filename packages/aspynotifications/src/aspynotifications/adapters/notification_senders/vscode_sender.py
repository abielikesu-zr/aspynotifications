from typing import Any

import structlog
from aspyadapters.adapters.http_client import AspyHttpClient
from aspyplugs.registry import register_plugin

from aspynotifications.config.destination_config import (
    VSCodeDestinationConfig,
    VSCodeUserAudience,
)
from aspynotifications.entities.delivery_result import DeliveryResult
from aspynotifications.entities.destination import Destination
from aspynotifications.entities.notification_provider import (
    NotificationProvider,
    VSCodeProvider,
)
from aspynotifications.ports.notification_provider_sender import (
    INotificationProviderSender,
)

logger = structlog.get_logger(__name__)


@register_plugin("notification_sender", "VSCODE")
class VSCodeNotificationSender(INotificationProviderSender):
    """Delivers rendered notifications to the HTTP relay consumed by VS Code."""

    def __init__(self, http_client: AspyHttpClient) -> None:
        self._http = http_client

    async def send(
        self,
        provider: NotificationProvider,
        destination: Destination,
        message: Any,
    ) -> DeliveryResult:
        provider_config = provider.provider
        if not isinstance(provider_config, VSCodeProvider):
            raise TypeError("VSCodeNotificationSender requires a VSCodeProvider")

        destination_config = destination.config
        if not isinstance(destination_config, VSCodeDestinationConfig):
            raise TypeError("VSCodeNotificationSender requires a VSCodeDestinationConfig")
        if not isinstance(message, dict):
            raise TypeError("VSCodeNotificationSender requires a dictionary message")

        payload = {**message, "audience": destination_config.audience.model_dump()}
        if isinstance(destination_config.audience, VSCodeUserAudience):
            payload["recipient_user_id"] = destination_config.audience.recipient_user_id
        logger.debug(
            "vscode_notification_delivery_requested",
            provider_name=provider.name,
            destination_name=destination.name,
            audience_type=destination_config.audience.type,
        )
        response = await self._http.post(
            provider_config.config.relay_url,
            headers={"Content-Type": "application/json"},
            payload=payload,
        )
        logger.info(
            "vscode_notification_delivery_accepted",
            provider_name=provider.name,
            destination_name=destination.name,
            status_code=response.status_code,
        )
        return DeliveryResult(
            status="accepted",
            provider_name=provider.name,
            provider_type=provider.provider.type,
            sender_name=self.__class__.__name__,
        )
