from typing import Any, cast

from aspyadapters.adapters.http_client import AspyHttpClient
from aspyplugs.registry import register_plugin

from aspynotifications.entities.delivery_result import DeliveryResult
from aspynotifications.entities.destination import Destination
from aspynotifications.entities.notification_provider import (
    NotificationProvider,
    SlackProviderConfig,
)
from aspynotifications.notification_senders.sender_base import (
    SimulatedNotificationSender,
)


@register_plugin("notification_sender", "SLACK")
class SlackNotificationSender(SimulatedNotificationSender):
    """Slack Incoming Webhook delivery adapter."""

    def __init__(self, http_client: AspyHttpClient) -> None:
        self._http = http_client

    async def send(
        self,
        provider: NotificationProvider,
        destination: Destination,
        message: Any,
    ) -> DeliveryResult:
        provider_config = cast(SlackProviderConfig, provider.provider).config

        response = await self._http.post(
            provider_config.webhook_url,
            headers={"Content-Type": "application/json"},
            payload=message,
        )

        print(
            f"Slack accepted the message for provider {provider.name}: "
            f"HTTP {response.status_code}."
        )
        return DeliveryResult(
            status="simulated",
            provider_name=provider.name,
            provider_type=provider.provider.type,
            sender_name=self.__class__.__name__,
        )
