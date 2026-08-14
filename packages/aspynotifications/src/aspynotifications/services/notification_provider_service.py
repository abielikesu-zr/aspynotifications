from typing import Any
from uuid import uuid4

import structlog

from aspynotifications.config.notification_provider_config import (
    NotificationProviderServiceConfig,
)
from aspynotifications.entities.notification_provider import NotificationProvider
from aspynotifications.ports.notification_provider_store import (
    NotificationProviderStore,
)

logger = structlog.get_logger(__name__)


class NotificationProviderService:
    """
    Domain service for the NotificationProvider lifecycle.

    Handles notification provider CRUD operations and delegates persistence
    to the NotificationProviderStore port.
    """

    def __init__(
        self,
        notification_provider_store: NotificationProviderStore,
        config: dict[str, Any],
    ):
        self.notification_provider_store = notification_provider_store
        self.config = NotificationProviderServiceConfig.model_validate(config)

        logger.debug("NotificationProviderService initialized")

    async def ping(self) -> bool:
        """
        Verifies that the underlying notification provider storage is healthy.
        """
        return await self.notification_provider_store.ping()

    async def create_notification_provider(
        self,
        name: str,
        provider_type: str,
        config: dict[str, Any],
    ) -> NotificationProvider:
        """
        Creates a new notification provider.
        """
        provider = NotificationProvider.model_validate(
            {
                "id": str(uuid4()),
                "name": name,
                "provider": {
                    "type": provider_type,
                    "config": config,
                },
            }
        )

        await self.notification_provider_store.save_notification_provider(provider)

        logger.info(
            "Notification provider created",
            provider_id=provider.id,
            name=provider.name,
        )

        return provider

    async def get_notification_provider(
        self,
        provider_id: str,
    ) -> NotificationProvider | None:
        """
        Retrieve a notification provider by ID.
        """
        provider = (
            await self.notification_provider_store.get_notification_provider_by_id(
                provider_id
            )
        )

        if not provider:
            logger.warning(
                "Notification provider not found",
                provider_id=provider_id,
            )

        return provider

    async def get_notification_provider_by_name(
        self,
        name: str,
    ) -> NotificationProvider | None:
        """
        Retrieve a notification provider by name.
        """
        provider = (
            await self.notification_provider_store.get_notification_provider_by_name(
                name
            )
        )

        if not provider:
            logger.warning(
                "Notification provider not found",
                name=name,
            )

        return provider

    async def update_notification_provider(
        self,
        provider_id: str,
        name: str | None = None,
        provider_type: str | None = None,
        config: dict[str, Any] | None = None,
    ) -> NotificationProvider:
        """
        Updates an existing notification provider.
        """
        existing_provider = await self._get_notification_provider_or_raise(provider_id)

        provider_data = existing_provider.model_dump()

        if name is not None:
            provider_data["name"] = name

        if provider_type is not None:
            provider_data["provider"]["type"] = provider_type

        if config is not None:
            provider_data["provider"]["config"] = config

        provider = NotificationProvider.model_validate(provider_data)

        await self.notification_provider_store.save_notification_provider(provider)

        logger.info(
            "Notification provider updated",
            provider_id=provider.id,
            name=provider.name,
        )

        return provider

    async def delete_notification_provider(
        self,
        provider_id: str,
    ) -> bool:
        """
        Deletes a notification provider by ID.
        """
        provider = await self.get_notification_provider(provider_id)

        if not provider:
            return False

        await self.notification_provider_store.delete_notification_provider(provider_id)

        logger.info(
            "Notification provider deleted",
            provider_id=provider_id,
            name=provider.name,
        )

        return True

    async def list_notification_providers(
        self,
    ) -> list[NotificationProvider]:
        """
        List all notification providers.
        """
        providers = await self.notification_provider_store.list_notification_providers()

        logger.debug(
            "Listed notification providers",
            count=len(providers),
        )

        return providers

    async def _get_notification_provider_or_raise(
        self,
        provider_id: str,
    ) -> NotificationProvider:
        """
        Retrieve a notification provider or raise if it does not exist.
        """
        provider = await self.get_notification_provider(provider_id)

        if not provider:
            raise LookupError(f"NotificationProvider {provider_id} not found")

        return provider
