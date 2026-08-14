import structlog
from aspyconfig import get_config as aspy_get_config

from aspynotifications.config.app_config import AspynotificationsAppConfig
from aspynotifications.containers.notifications_container import (
    AspyNotificationsContainer,
)
from aspynotifications.services.cloud_event_service import CloudEventService
from aspynotifications.services.destinations_service import DestinationsService
from aspynotifications.services.notification_provider_service import (
    NotificationProviderService,
)
from aspynotifications.services.notifications_facade import NotificationsFacade
from aspynotifications.services.policy_service import NotificationPolicyService
from aspynotifications.services.template_service import TemplateService

logger = structlog.get_logger(__name__)

# Singleton instances for the DI container and config.

_notifications_container: AspyNotificationsContainer | None = None
_notifications_app_config: AspynotificationsAppConfig | None = None


def get_notifications_config() -> AspynotificationsAppConfig:
    """
    Provides the initialized AspynotificationsAppConfig Pydantic model,
    loading configuration only once.
    """
    global _notifications_app_config

    if _notifications_app_config is None:
        config = aspy_get_config()

        model = config.to_pydantic(AspynotificationsAppConfig)

        if not isinstance(model, AspynotificationsAppConfig):
            raise TypeError(
                "Expected AspynotificationsAppConfig from configuration system."
            )

        _notifications_app_config = model
        logger.debug("Notifications configuration loaded and validated")

    return _notifications_app_config


def _initialize_container() -> AspyNotificationsContainer:
    """
    Initializes the AspyNotificationsContainer with the validated configuration.
    """
    global _notifications_container

    if _notifications_container is None:
        config = get_notifications_config()

        _notifications_container = AspyNotificationsContainer()

        dict_config = config.model_dump()

        logger.debug("Wiring AspyNotificationsContainer with validated configuration")

        _notifications_container.config.from_dict(dict_config)

        logger.info("Notifications container initialized and wired via DI")

    return _notifications_container


def get_cloud_event_service() -> CloudEventService:
    """Return the CloudEventService singleton."""
    return _initialize_container().cloud_event_service()


def get_template_service() -> TemplateService:
    """Return the TemplateService singleton."""
    return _initialize_container().template_service()


def get_notification_policy_service() -> NotificationPolicyService:
    """Return the NotificationPolicyService singleton."""
    return _initialize_container().notification_policy_service()


def get_destinations_service() -> DestinationsService:
    """Return the DestinationsService singleton."""
    return _initialize_container().destinations_service()


def get_notification_provider_service() -> NotificationProviderService:
    """Return the NotificationProviderService singleton."""
    return _initialize_container().notification_provider_service()


def get_notification_facade() -> NotificationsFacade:
    """Return the NotificationProviderService singleton."""
    return _initialize_container().notifications_facade()
