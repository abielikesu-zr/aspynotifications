from typing import Any

from aspyplugs.registry import register_plugin

from aspynotifications.adapters.notify_renderer_jinja import Jinja2TemplateRenderer
from aspynotifications.entities.template import Template
from aspynotifications.ports.notification_renderer import NotificationRendererPort


@register_plugin("notification_renderer", "output_hole")
class OutputHoleNotificationAdapter(NotificationRendererPort):
    """Renders notification templates for output-hole destinations."""

    def __init__(self, renderer: Jinja2TemplateRenderer):
        self._renderer = renderer

    def render(
        self,
        template: Template,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        if template.output_hole is None:
            raise ValueError(
                f"Template '{template.name}' has no output-hole configuration"
            )

        source = template.output_hole.dumpster

        if source is None:
            raise ValueError(
                f"Template '{template.name}' has no output-hole dumpster configuration"
            )

        if source.inline is not None:
            return {
                "content": self._renderer.render_inline(
                    source.inline,
                    context,
                )
            }

        if source.file is not None:
            return {
                "content": self._renderer.render(
                    source.file,
                    context,
                )
            }

        raise ValueError(f"Template '{template.name}' has no output-hole source")
