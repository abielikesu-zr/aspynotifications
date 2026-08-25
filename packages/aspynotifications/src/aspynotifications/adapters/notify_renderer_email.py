import uuid
from pathlib import Path
from typing import Any

import yaml
from aspyplugs.registry import register_plugin

from aspynotifications.adapters.notify_renderer_jinja import Jinja2TemplateRenderer
from aspynotifications.entities.template import Template
from aspynotifications.ports.notification_renderer import NotificationRendererPort


@register_plugin("notification_renderer", "email")
class EmailNotificationAdapter(NotificationRendererPort):
    """Renders notification templates for email destinations."""

    def __init__(self, renderer: Jinja2TemplateRenderer):
        self._renderer = renderer
        output_dir: str | Path = "var/rendered"
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)

    def render(
        self,
        template: Template,
        context: dict[str, Any],
    ) -> dict[str, str | None]:
        if template.email is None:
            raise ValueError(f"Template '{template.name}' has no email configuration")

        subject = None
        html = None
        text = None

        if template.email.subject is not None:
            source = template.email.subject

            if source.inline is not None:
                subject = self._renderer.render_inline(
                    source.inline,
                    context,
                )
            elif source.file is not None:
                subject = self._renderer.render(
                    source.file,
                    context,
                )

        if template.email.html is not None:
            source = template.email.html

            if source.file is not None:
                html = self._renderer.render(
                    source.file,
                    context,
                )

        if template.email.text is not None:
            source = template.email.text

            if source.file is not None:
                text = self._renderer.render(
                    source.file,
                    context,
                )

        result = {
            "subject": subject,
            "html": html,
            "text": text,
        }

        # --- UUID suffix + single YAML file ---
        suffix = str(uuid.uuid4())[:8]
        out_file = self._output_dir / f"{template.name}-{suffix}.yaml"
        with out_file.open("w", encoding="utf-8") as f:
            yaml.dump(
                result, f, default_flow_style=False, sort_keys=False, allow_unicode=True
            )
        print(f"[Email] saved → {out_file}")

        return result
