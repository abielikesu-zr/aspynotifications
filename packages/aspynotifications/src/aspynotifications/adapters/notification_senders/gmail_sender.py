from typing import Any

from aspyadapters.adapters.http_client import AspyHttpClient
from aspyplugs.registry import register_plugin

from aspynotifications.entities.delivery_result import DeliveryResult
from aspynotifications.entities.destination import Destination
from aspynotifications.entities.notification_provider import NotificationProvider
from aspynotifications.adapters.notification_senders.sender_base import (
    SimulatedNotificationSender,
)


@register_plugin("notification_sender", "GMAIL")
class GmailNotificationSender(SimulatedNotificationSender):
    """Simulated Gmail delivery adapter."""

    def __init__(self, http_client: AspyHttpClient) -> None:
        self._http = http_client

    async def send(
        self,
        provider: NotificationProvider,
        destination: Destination,
        message: Any,
    ) -> DeliveryResult:
        print(
            "Aquí enviaré el mensaje por Gmail; "
            f"soy el provider {provider.name} para el destino {destination.name}."
        )
        return DeliveryResult(
            status="simulated",
            provider_name=provider.name,
            provider_type=provider.provider.type,
            sender_name=self.__class__.__name__,
        )
