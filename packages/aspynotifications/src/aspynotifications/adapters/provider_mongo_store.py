import structlog
from aspyadapters.adapters.generic_mongo_db_adapter import (
    GenericMongoAdapter,
    NotFoundError,
)
from aspyplugs.registry import register_plugin
from pydantic import BaseModel, ValidationError

from aspynotifications.entities.notification_provider import NotificationProvider
from aspynotifications.ports.notification_provider_store import (
    NotificationProviderStore,
)

logger = structlog.get_logger()


@register_plugin("notification_provider_store", "MONGODB")
class NotificationProviderStoreMongoAdapter(
    NotificationProviderStore,
    GenericMongoAdapter,
):
    """
    Asynchronous persistence adapter for NotificationProvider entities,
    using MongoDB.
    """

    def get_model_class(self) -> type[BaseModel]:  # type: ignore[override]
        """Specify the Pydantic model used by this adapter."""
        return NotificationProvider

    def get_collection_name(self) -> str:
        """Return the MongoDB collection name."""
        return "notification_providers"

    async def save_notification_provider(
        self,
        provider: NotificationProvider,
    ) -> None:
        """
        Save a notification provider.

        Handles both creation and updating.
        """
        key = f"{provider.id}"

        try:
            await self.save(key, provider)
        except Exception as e:
            logger.error(
                "Persistence error saving notification provider",
                provider_id=provider.id,
                error=str(e),
            )
            raise Exception(  # noqa: TRY002
                f"Error saving notification provider {provider.id}: {e!s}"
            ) from e

    async def get_notification_provider_by_id(
        self,
        provider_id: str,
    ) -> NotificationProvider | None:
        """
        Retrieve a notification provider by its canonical ID.
        """
        key = f"{provider_id}"

        try:
            return await self.load(key)
        except NotFoundError:
            return None
        except ValidationError as e:
            logger.error(
                "Corrupted data found for notification provider",
                provider_id=provider_id,
                error=str(e),
            )
            raise ValueError(
                f"Corrupted data in notification provider {provider_id}: {e!s}"
            ) from e
        except Exception as e:
            logger.error(
                "Persistence error retrieving notification provider",
                provider_id=provider_id,
                error=str(e),
            )
            raise Exception(  # noqa: TRY002
                f"Error retrieving notification provider {provider_id}: {e!s}"
            ) from e

    async def get_notification_provider_by_name(
        self,
        name: str,
    ) -> NotificationProvider | None:
        """
        Retrieve a notification provider by name.
        """
        criteria = {"name": name}

        try:
            result = await self.find_one(criteria=criteria)  # type: ignore[func-returns-value]
        except NotFoundError:
            return None
        except ValidationError as e:
            logger.error(
                "Corrupted data found while retrieving notification provider by name",
                name=name,
                error=str(e),
            )
            raise ValueError(
                f"Corrupted data in notification provider with name {name}: {e!s}"
            ) from e
        except Exception as e:
            logger.error(
                "Persistence error retrieving notification provider by name",
                name=name,
                error=str(e),
            )
            raise Exception(  # noqa: TRY002
                f"Error retrieving notification provider with name {name}: {e!s}"
            ) from e

        return result

    async def list_notification_providers(
        self,
    ) -> list[NotificationProvider]:
        """
        Retrieve all notification providers.
        """
        try:
            return await self.find()
        except ValidationError as e:
            logger.error(
                "Corrupted data found while listing notification providers",
                error=str(e),
            )
            raise ValueError(f"Corrupted data in notification providers: {e!s}") from e
        except Exception as e:
            logger.error(
                "Persistence error listing notification providers",
                error=str(e),
            )
            raise Exception(f"Error listing notification providers: {e!s}") from e

    async def delete_notification_provider(
        self,
        provider_id: str,
    ) -> None:
        """
        Delete a notification provider by canonical ID.
        """
        key = f"{provider_id}"

        try:
            await self.delete(key)
        except NotFoundError:
            return
        except Exception as e:
            logger.error(
                "Persistence error deleting notification provider",
                provider_id=provider_id,
                error=str(e),
            )
            raise Exception(  # noqa: TRY002
                f"Error deleting notification provider {provider_id}: {e!s}"
            ) from e

    async def ping(self) -> bool:
        """
        Bridge the abstract requirement from the Port to the
        implementation in the Generic adapter.
        """
        return await self.ping_resource()
