from typing import Any

from aspyadapters.adapters.http_client import AspyHttpClient
from aspyplugs.registry import register_plugin

from aspynotifications.entities.delivery_result import DeliveryResult
from aspynotifications.entities.destination import Destination
from aspynotifications.entities.notification_provider import (
    NotificationProvider,
    SlackProvider,
)
from aspynotifications.ports.notification_provider_sender import (
    INotificationProviderSender,
)


@register_plugin("notification_sender", "SLACK")
class SlackNotificationSender(INotificationProviderSender):
    """Slack Incoming Webhook delivery adapter."""

    def __init__(self, http_client: AspyHttpClient) -> None:
        self._http = http_client

    async def send(
        self,
        provider: NotificationProvider,
        destination: Destination,
        message: Any,
    ) -> DeliveryResult:
        provider_config = provider.provider
        if not isinstance(provider_config, SlackProvider):
            raise TypeError("SlackNotificationSender requires a SlackProvider")

        response = await self._http.post(
            provider_config.config.webhook_url,
            headers={"Content-Type": "application/json"},
            payload=message,
        )

        print(
            f"Slack accepted the message for provider {provider.name}: "
            f"HTTP {response.status_code}."
        )
        return DeliveryResult(
            status="accepted",
            provider_name=provider.name,
            provider_type=provider.provider.type,
            sender_name=self.__class__.__name__,
        )
