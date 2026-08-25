import uuid
from pathlib import Path
from typing import Any

import yaml
from aspyplugs.registry import register_plugin

from aspynotifications.adapters.notify_renderer_jinja import Jinja2TemplateRenderer
from aspynotifications.entities.template import Template
from aspynotifications.ports.notification_renderer import NotificationRendererPort


@register_plugin("notification_renderer", "slack_channel")
class SlackNotificationAdapter(NotificationRendererPort):
    """Renders notification templates for Slack destinations."""

    def __init__(self, renderer: Jinja2TemplateRenderer):
        self._renderer = renderer
        output_dir: str | Path = "var/rendered"
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)

    def render(
        self,
        template: Template,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        if template.slack is None or template.slack.blocks is None:
            raise ValueError(
                f"Template '{template.name}' has no Slack blocks configuration"
            )

        source = template.slack.blocks

        if source.file is not None:
            rendered = self._renderer.render(
                source.file,
                context,
            )
        elif source.inline is not None:
            rendered = self._renderer.render_inline(
                source.inline,
                context,
            )
        else:
            raise ValueError(f"Template '{template.name}' has no Slack blocks source")

        rendered_blocks = yaml.safe_load(rendered)
        result = {"blocks": rendered_blocks.get("blocks")}

        # --- UUID suffix + save ---
        suffix = str(uuid.uuid4())[:8]
        out_file = self._output_dir / f"{template.name}-{suffix}.yaml"
        with out_file.open("w", encoding="utf-8") as f:
            yaml.dump(result, f, default_flow_style=False, sort_keys=False)
        print(f"[Slack] saved → {out_file}")

        return result
