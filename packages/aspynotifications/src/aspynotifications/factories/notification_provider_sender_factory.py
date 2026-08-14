from aspyplugs.factory import PluginFactory
from aspyadapters.adapters.http_client import AspyHttpClient

from aspynotifications.ports.notification_provider_sender import (
    INotificationProviderSender,
)


class NotificationProviderSenderFactory:
    """Selects a delivery adapter from a provider's type discriminator."""

    def __init__(self, http_client: AspyHttpClient) -> None:
        self._http_client = http_client
        self._plugin_factory = PluginFactory("notification_sender")

    def create(self, provider_type: str) -> INotificationProviderSender:
        return self._plugin_factory.create(
            provider_type,
            http_client=self._http_client,
        )
