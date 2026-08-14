import structlog
from aspyadapters.adapters.generic_local_fs import GenericLocalFSAdapter
from aspyplugs.registry import register_plugin
from pydantic import BaseModel, ValidationError

from aspynotifications.entities.notification_provider import NotificationProvider
from aspynotifications.ports.notification_provider_store import (
    NotificationProviderStore,
)

logger = structlog.get_logger(__name__)


@register_plugin("notification_provider_store", "LOCALFS")
class NotificationProviderFileStoreAdapter(
    NotificationProviderStore,
    GenericLocalFSAdapter,
):
    """
    Interface for a notification provider store (DB or other persistence).
    Pure persistence — no business logic.
    All methods are async.
    """

    def get_model_class(self) -> type[BaseModel]:  # type: ignore[override]
        """Specify the Pydantic model used by this adapter."""
        return NotificationProvider

    def get_index_declarations(self) -> dict:
        return {
            "by_name": ["name"],
        }

    async def save_notification_provider(
        self,
        provider: NotificationProvider,
    ) -> None:
        """
        Persist a notification provider.
        Can be used for both creation and update.
        """
        filename = f"{provider.id}.json"

        try:
            await self.save(filename, provider)
        except Exception as e:
            logger.debug(
                "Persistence error saving notification provider to FS",
                provider_id=provider.id,
                error=str(e),
                exc_info=e,
            )
            raise Exception(  # noqa: TRY002
                f"Error saving notification provider {provider.id} to FS: {e!s}"
            ) from e

    async def get_notification_provider_by_id(
        self,
        provider_id: str,
    ) -> NotificationProvider | None:
        """
        Retrieve a notification provider by canonical ID.
        """
        filename = f"{provider_id}.json"

        try:
            return await self.load(filename)
        except FileNotFoundError:
            return None
        except ValidationError as e:
            logger.debug(
                "Corrupted data found for notification provider on FS",
                provider_id=provider_id,
                error=str(e),
                exc_info=e,
            )
            raise ValueError(
                f"Corrupted data in notification provider {provider_id} on FS: {e!s}"
            ) from e
        except Exception as e:
            logger.debug(
                "Persistence error retrieving notification provider from FS",
                provider_id=provider_id,
                error=str(e),
                exc_info=e,
            )
            raise Exception(  # noqa: TRY002
                f"Error retrieving notification provider {provider_id} from FS: {e!s}"
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
            providers = await self.find(
                index_name="by_name",
                criteria=criteria,
            )

            if not providers:
                return None

            return providers[0]
        except ValidationError as e:
            logger.debug(
                "Corrupted data found for notification provider on FS",
                name=name,
                error=str(e),
                exc_info=e,
            )
            raise ValueError(
                f"Corrupted data in notification provider {name} on FS: {e!s}"
            ) from e
        except Exception as e:
            logger.debug(
                "Persistence error retrieving notification provider by name",
                name=name,
                error=str(e),
                exc_info=e,
            )
            raise Exception(  # noqa: TRY002
                f"Error retrieving notification provider by name {name} from FS: {e!s}"
            ) from e

    async def list_notification_providers(
        self,
    ) -> list[NotificationProvider]:
        """
        List all notification providers.
        """
        try:
            return await self.find()
        except Exception as e:
            logger.debug(
                "Persistence error listing notification providers",
                error=str(e),
                exc_info=e,
            )
            raise Exception(  # noqa: TRY002
                f"Error listing notification providers: {e!s}"
            ) from e

    async def delete_notification_provider(
        self,
        provider_id: str,
    ) -> None:
        """
        Delete a notification provider by canonical ID.
        """
        filename = f"{provider_id}.json"

        try:
            await self.delete(filename)
        except Exception as e:
            logger.debug(
                "Persistence error deleting notification provider from FS",
                provider_id=provider_id,
                error=str(e),
                exc_info=e,
            )
            raise Exception(  # noqa: TRY002
                f"Error deleting notification provider {provider_id} from FS: {e!s}"
            ) from e

    async def ping(self) -> bool:
        """
        Bridge the abstract requirement from the Port to the
        implementation in the Generic adapter.
        """
        return await self.ping_resource()
