from typing import Any

from aspynotifications.adapters.notify_renderer_email import EmailNotificationAdapter
from aspynotifications.adapters.notify_renderer_jinja import Jinja2TemplateRenderer
from aspynotifications.adapters.notify_renderer_ohooe import (
    OutputHoleNotificationAdapter,
)
from aspynotifications.adapters.notify_renderer_slack import SlackNotificationAdapter
from aspynotifications.config.notification_renderer_config import (
    NotificationTemplateRendererConfig,
)
from aspynotifications.entities.destination import Destination
from aspynotifications.entities.template import Template
from aspynotifications.ports.notification_renderer import NotificationRendererPort
from aspynotifications.services.admin_url_generator import AdminUrlGenerator


class NotificationTemplateRenderer:
    """Selects the appropriate provider adapter and renders a template."""

    def __init__(
        self,
        config: dict[str, Any],
        admin_url_generator: AdminUrlGenerator,
    ) -> None:
        self.config = NotificationTemplateRendererConfig.model_validate(config)
        self.admin_url_generator = admin_url_generator

        renderer = Jinja2TemplateRenderer(self.config.template_root)

        self._adapters: dict[str, NotificationRendererPort] = {
            "email": EmailNotificationAdapter(renderer),
            "slack_channel": SlackNotificationAdapter(renderer),
            "output_hole": OutputHoleNotificationAdapter(renderer),
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

        subject = context["envelope"]["subject"]
        entity_type, _ = subject.split("/", 1)

        admin_url = self.admin_url_generator.generate_url(
            entity_type=entity_type,
            context=context["context"],
        )

        if admin_url is not None:
            system_name, url = admin_url

            context["context"]["admin_url"] = url
            context["context"].setdefault("links", {})[system_name] = url

        return adapter.render(
            template=template,
            context=context,
        )
