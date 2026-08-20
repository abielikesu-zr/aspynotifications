from typing import Any

from aspyplugs.registry import register_plugin

from aspynotifications.entities.delivery_result import DeliveryResult
from aspynotifications.entities.destination import Destination
from aspynotifications.entities.notification_provider import NotificationProvider
from aspynotifications.ports.notification_provider_sender import (
    INotificationProviderSender,
)


@register_plugin("notification_sender", "SHOLE")
class OutputHoleNotificationSender(INotificationProviderSender):
    """Console delivery adapter for output-hole notifications."""

    async def send(
        self,
        provider: NotificationProvider,
        destination: Destination,
        message: Any,
    ) -> DeliveryResult:
        print(message)

        return DeliveryResult(
            status="accepted",
            provider_name=provider.name,
            provider_type=provider.provider.type,
            sender_name=self.__class__.__name__,
        )
