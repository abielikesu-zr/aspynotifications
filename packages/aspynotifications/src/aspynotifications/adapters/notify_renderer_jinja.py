from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader


class Jinja2TemplateRenderer:
    """Generic Jinja2 template renderer."""

    def __init__(self, template_root: str | Path):
        self._environment = Environment(
            loader=FileSystemLoader(template_root),
            autoescape=False,
        )

    def render(
        self,
        template_path: str,
        context: dict[str, Any],
    ) -> str:
        template = self._environment.get_template(template_path)
        return template.render(**context)

    def render_inline(
        self,
        content: str,
        context: dict[str, Any],
    ) -> str:
        template = self._environment.from_string(content)
        return template.render(**context)
