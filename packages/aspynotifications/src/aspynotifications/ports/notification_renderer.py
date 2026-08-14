from abc import ABC, abstractmethod
from typing import Any

from aspynotifications.entities.template import Template


class NotificationRendererPort(ABC):
    @abstractmethod
    def render(
        self,
        template: Template,
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Render a notification template."""
        ...
