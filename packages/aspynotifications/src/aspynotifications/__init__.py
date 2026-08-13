from aspyconfig import get_config

from aspynotifications.config.app_config import AspynotificationsAppConfig


_aspynotifications_app_config: AspynotificationsAppConfig | None = None


def get_aspynotifications_config() -> AspynotificationsAppConfig:
    """Return the validated configuration for aspynotifications."""

    global _aspynotifications_app_config

    if _aspynotifications_app_config is None:
        config = get_config()
        _aspynotifications_app_config = config.to_pydantic(
            AspynotificationsAppConfig
        )

    return _aspynotifications_app_config
