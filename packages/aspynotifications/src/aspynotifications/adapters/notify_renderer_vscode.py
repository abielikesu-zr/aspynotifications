from typing import Any

from aspyplugs.registry import register_plugin

from aspynotifications.adapters.notify_renderer_jinja import Jinja2TemplateRenderer
from aspynotifications.entities.source import TemplateSource
from aspynotifications.entities.template import Template
from aspynotifications.ports.notification_renderer import NotificationRendererPort


@register_plugin("notification_renderer", "vscode")
class VSCodeNotificationRenderer(NotificationRendererPort):
    """Renders the title, message, and severity expected by the VS Code relay."""

    def __init__(self, renderer: Jinja2TemplateRenderer) -> None:
        self._renderer = renderer

    def render(self, template: Template, context: dict[str, Any]) -> dict[str, str]:
        if template.vscode is None:
            raise ValueError(f"Template '{template.name}' has no VS Code configuration")

        return {
            "title": self._render_source(template.vscode.title, context),
            "message": self._render_source(template.vscode.message, context),
            "severity": template.vscode.severity,
        }

    def _render_source(self, source: TemplateSource, context: dict[str, Any]) -> str:
        if source.inline is not None:
            return self._renderer.render_inline(source.inline, context)
        if source.file is not None:
            return self._renderer.render(source.file, context)
        raise ValueError("VS Code template source must define inline or file")
