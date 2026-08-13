from typing import Any

from aspynotifications.adapters.notify_renderer_email import EmailNotificationAdapter
from aspynotifications.adapters.notify_renderer_jinja import Jinja2TemplateRenderer
from aspynotifications.adapters.notify_renderer_slack import SlackNotificationAdapter
from aspynotifications.entities.destination import Destination
from aspynotifications.entities.template import Template


class NotificationTemplateRenderer:
    """Selects the appropriate provider adapter and renders a template."""

    def __init__(self, template_root: str):
        renderer = Jinja2TemplateRenderer(template_root)

        self._adapters = {
            "smtp": EmailNotificationAdapter(renderer),
            "slack": SlackNotificationAdapter(renderer),
        }

    def render(
        self,
        destination: Destination,
        template: Template,
        context: dict[str, Any],
    ) -> Any:
        adapter = self._adapters.get(destination.provider)

        if adapter is None:
            raise ValueError(
                f"Unsupported notification provider: {destination.provider}"
            )

        return adapter.render(
            template=template,
            context=context,
        )
