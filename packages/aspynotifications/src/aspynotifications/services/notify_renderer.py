from typing import Any

from aspynotifications.adapters.notify_renderer_email import EmailNotificationAdapter
from aspynotifications.adapters.notify_renderer_jinja import Jinja2TemplateRenderer
from aspynotifications.adapters.notify_renderer_slack import SlackNotificationAdapter
from aspynotifications.entities.destination import Destination
from aspynotifications.entities.template import Template
from aspynotifications.ports.notification_renderer import NotificationRendererPort


class NotificationTemplateRenderer:
    """Selects the appropriate provider adapter and renders a template."""

    def __init__(self, template_root: str):
        renderer = Jinja2TemplateRenderer(template_root)

        self._adapters: dict[str, NotificationRendererPort] = {
            "email": EmailNotificationAdapter(renderer),
            "slack_channel": SlackNotificationAdapter(renderer),
        }

    def render(
        self,
        destination: Destination,
        template: Template,
        context: dict[str, Any],
    ) -> Any:
        adapter = self._adapters.get(destination.type)

        if adapter is None:
            raise ValueError(f"Unsupported notification provider: {destination.type}")

        return adapter.render(
            template=template,
            context=context,
        )
