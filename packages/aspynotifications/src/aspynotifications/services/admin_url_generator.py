from typing import Any

from aspynotifications.config.admin_url_config import AdminUrlGeneratorConfig


class AdminUrlGenerator:
    """
    Generates navigation URLs for the configured admin UI.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = AdminUrlGeneratorConfig.model_validate(config)
        self.system_name: str = self.config.system_name
        self.base_url: str = self.config.base_url.rstrip("/")

    def generate_url(
        self,
        entity_type: str,
        context: dict[str, str],
    ) -> tuple[str, str] | None:
        """
        Generate an admin UI URL for an entity.

        Returns None when the entity type is not supported.
        """
        routes = {
            "tenant": lambda c: f"/admin/tenant/{c['tenant_id']}?tab=overview",
            "bot": lambda c: f"/admin/tenant/{c['tenant_id']}?tab=bots",
            "bot_installation": lambda c: (
                f"/admin/tenant/{c['tenant_id']}?tab=installations"
            ),
        }

        generator = routes.get(entity_type)

        if generator is None:
            return None

        return (
            self.system_name,
            f"{self.base_url}{generator(context)}",
        )
