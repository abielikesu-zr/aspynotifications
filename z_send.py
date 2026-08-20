import asyncio

import structlog
from aspyadapters.adapters.http_client import AspyHttpClient
from aspyconfig import get_config
from aspylogger.services.logging_setup import bootstrap_logging, configure_logging
from aspynotifications import (
    _initialize_container,
    get_notification_provider_service,
    get_notifications_config,
)
from aspynotifications.containers.notifications_container import (
    AspyNotificationsContainer,
)

logger = structlog.get_logger(__name__)


async def main() -> None:
    bootstrap_logging(verbose=0)
    config = get_config()
    config.register_files("mono", ["monoconfig/default/aspynotifications_rest"])
    config.load()
    configure_logging()

    logger.info("Starting notification provider creation test")

    # ---------------------------------------------------------------
    # 1. Load and inspect the validated application configuration
    # ---------------------------------------------------------------
    config = get_notifications_config()

    logger.info(
        "Notifications configuration loaded",
        notification_provider_store=config.aspynotifications.notification_provider_store,
    )

    # ---------------------------------------------------------------
    # 2. Initialize the REAL DI container
    # ---------------------------------------------------------------
    container: AspyNotificationsContainer = _initialize_container()

    logger.info("Notifications container initialized")

    # ---------------------------------------------------------------
    # 3. Inspect the HTTP client provider before resolving it
    # ---------------------------------------------------------------
    http_client_provider = container.notification_sender_http_client

    logger.info(
        "Notification sender HTTP client provider obtained",
        provider_type=type(http_client_provider).__name__,
    )

    # ---------------------------------------------------------------
    # 4. Resolve the actual HTTP client
    # ---------------------------------------------------------------
    http_client = http_client_provider()

    logger.info(
        "Notification sender HTTP client created",
        client_type=type(http_client).__name__,
        client_config=getattr(http_client, "config", None),
    )

    # ---------------------------------------------------------------
    # 5. Resolve the plugin dependency resolver
    # ---------------------------------------------------------------
    resolver = container.provider_sender_resolver()

    logger.info(
        "Provider sender resolver created",
        resolver_type=type(resolver).__name__,
    )
    dependency = resolver._dependencies[AspyHttpClient]

    logger.info(
        "Inspecting registered resolver dependency",
        dependency=dependency,
        dependency_type=type(dependency).__name__,
        same_provider=dependency is container.notification_sender_http_client,
    )

    logger.info(
        "Inspecting container provider",
        provider=container.notification_sender_http_client,
        provider_type=type(container.notification_sender_http_client).__name__,
    )
    # ---------------------------------------------------------------
    # 6. Resolve AspyHttpClient THROUGH the plugin resolver
    # ---------------------------------------------------------------
    resolved_http_client = resolver.resolve(type(http_client))

    logger.info(
        "AspyHttpClient resolved through PluginDependencyResolver",
        resolved_type=type(resolved_http_client).__name__,
        resolved_config=getattr(resolved_http_client, "config", None),
        same_instance=resolved_http_client is http_client,
    )

    # ---------------------------------------------------------------
    # 7. Resolve the real sender factory
    # ---------------------------------------------------------------
    sender_factory = container.notification_provider_sender_factory()

    logger.info(
        "NotificationProviderSenderFactory created",
        factory_type=type(sender_factory).__name__,
        resolver_type=type(sender_factory.resolver).__name__,
    )

    # ---------------------------------------------------------------
    # 8. Resolve the real provider service
    # ---------------------------------------------------------------
    provider_service = get_notification_provider_service()

    logger.info(
        "NotificationProviderService created",
        service_type=type(provider_service).__name__,
    )

    logger.info("Notification provider creation test completed")


if __name__ == "__main__":
    asyncio.run(main())
