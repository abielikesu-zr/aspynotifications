from typing import Any, Protocol

from aspynotifications.entities.delivery_result import DeliveryResult
from aspynotifications.entities.destination import Destination
from aspynotifications.entities.notification_provider import NotificationProvider


class INotificationProviderSender(Protocol):
    """Port implemented by each notification-provider delivery adapter."""

    async def send(
        self,
        provider: NotificationProvider,
        destination: Destination,
        message: Any,
    ) -> DeliveryResult:
        """Deliver a rendered message to a destination."""
        ...
