from aspyplugs.factory import PluginFactory

from aspynotifications.ports.notification_provider_sender import (
    INotificationProviderSender,
)


class NotificationProviderSenderFactory:
    """Selects a delivery adapter from a provider's type discriminator."""

    def __init__(self) -> None:
        self._plugin_factory = PluginFactory("notification_sender")

    def create(self, provider_type: str) -> INotificationProviderSender:
        return self._plugin_factory.create(provider_type)
