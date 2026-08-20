from aspyplugs.factory import PluginFactory
from aspyadapters.adapters.http_client import AspyHttpClient
from aspyplugs.z_plug_resolver import PluginDependencyResolver
from aspyplugs.templates.simple_plugin_factory import SimplePluginFactory

from aspynotifications.ports.notification_provider_sender import (
    INotificationProviderSender,
)

class NotificationProviderSenderFactory(SimplePluginFactory[INotificationProviderSender]):
    plugin_group="notification_sender"

