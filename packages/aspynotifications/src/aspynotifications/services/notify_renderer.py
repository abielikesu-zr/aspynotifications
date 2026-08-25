from typing import Any

from aspynotifications.entities.destination import Destination
from aspynotifications.entities.template import Template
from aspynotifications.factories.notification_renderer_factory import (
    NotificationRendererFactory,
)
from aspynotifications.services.admin_url_generator import AdminUrlGenerator


class NotificationTemplateRenderer:
    """Selects the appropriate provider adapter and renders a template."""

    def __init__(
        self,
        admin_url_generator: AdminUrlGenerator,
        renderer_factory: NotificationRendererFactory,
    ) -> None:
        self.admin_url_generator = admin_url_generator
        self.renderer_factory = renderer_factory

    def render(
        self,
        destination: Destination,
        template: Template,
        context: dict[str, Any],
    ) -> Any:
        adapter = self.renderer_factory.create(destination.type)

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
