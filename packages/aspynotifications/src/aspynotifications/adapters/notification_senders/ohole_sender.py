from typing import Any

from aspyplugs.registry import register_plugin
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from aspynotifications.entities.delivery_result import DeliveryResult
from aspynotifications.entities.destination import Destination
from aspynotifications.entities.notification_provider import NotificationProvider
from aspynotifications.ports.notification_provider_sender import (
    INotificationProviderSender,
)


@register_plugin("notification_sender", "SHOLE")
class OutputHoleNotificationSender(INotificationProviderSender):
    """Console delivery adapter for output-hole notifications."""

    def __init__(self) -> None:
        self._console = Console()

    async def send(
        self,
        provider: NotificationProvider,
        destination: Destination,
        message: Any,
    ) -> DeliveryResult:
        content = (
            message.get("content", message) if isinstance(message, dict) else message
        )

        self._console.print()

        self._console.print(
            Panel(
                Text(str(content)),
                title="[bold magenta]💀 NOTIFICATION HOLE 💀[/bold magenta]",
                subtitle="[dim]delivery accepted[/dim]",
                border_style="magenta",
                padding=(1, 2),
            )
        )

        self._console.print()

        return DeliveryResult(
            status="accepted",
            provider_name=provider.name,
            provider_type=provider.provider.type,
            sender_name=self.__class__.__name__,
        )
