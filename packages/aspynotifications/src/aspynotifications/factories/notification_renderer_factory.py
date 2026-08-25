from aspyplugs.templates.simple_plugin_factory import SimplePluginFactory

from aspynotifications.ports.notification_renderer import NotificationRendererPort


class NotificationRendererFactory(SimplePluginFactory[NotificationRendererPort]):
    """Creates template renderers registered for destination types."""

    plugin_group = "notification_renderer"
