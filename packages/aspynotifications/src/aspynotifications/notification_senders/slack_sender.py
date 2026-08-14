from typing import Any, cast

import httpx
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

    async def send(
        self,
        provider: NotificationProvider,
        destination: Destination,
        message: Any,
    ) -> DeliveryResult:
        provider_config = cast(SlackProviderConfig, provider.provider).config

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                provider_config.webhook_url,
                headers={"Content-Type": "application/json"},
                json=message,
            )
            response.raise_for_status()

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
