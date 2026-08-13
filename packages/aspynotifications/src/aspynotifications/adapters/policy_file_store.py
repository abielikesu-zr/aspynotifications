import structlog
from aspyadapters.adapters.generic_local_fs import GenericLocalFSAdapter
from aspyplugs.registry import register_plugin
from pydantic import BaseModel, ValidationError

from aspynotifications.entities.notification_policy import NotificationPolicy
from aspynotifications.ports.policies_store import NotificationPolicyStore

logger = structlog.get_logger(__name__)


@register_plugin("notification_policy_store", "LOCALFS")
class NotificationPolicyFileStoreAdapter(
    NotificationPolicyStore,
    GenericLocalFSAdapter,
):
    """
    Interface for a notification policy store (DB or other persistence).
    Pure persistence — no business logic.
    All methods are async.
    """

    def get_model_class(self) -> type[BaseModel]:  # type: ignore[override]
        """Specify the Pydantic model used by this adapter."""
        return NotificationPolicy

    def get_index_declarations(self) -> dict:
        return {
            "by_name": ["name"],
        }

    async def save_notification_policy(
        self,
        policy: NotificationPolicy,
    ) -> None:
        """
        Persist a notification policy.
        Can be used for both creation and update.
        """
        filename = f"{policy.id}.json"

        try:
            await self.save(filename, policy)
        except Exception as e:
            logger.debug(
                "Persistence error saving notification policy to FS",
                policy_id=policy.id,
                error=str(e),
                exc_info=e,
            )
            raise Exception(  # noqa: TRY002
                f"Error saving notification policy {policy.id} to FS: {e!s}"
            ) from e

    async def get_notification_policy_by_id(
        self,
        policy_id: str,
    ) -> NotificationPolicy | None:
        """
        Retrieve a notification policy by canonical ID.
        """
        filename = f"{policy_id}.json"

        try:
            return await self.load(filename)
        except FileNotFoundError:
            return None
        except ValidationError as e:
            logger.debug(
                "Corrupted data found for notification policy on FS",
                policy_id=policy_id,
                error=str(e),
                exc_info=e,
            )
            raise ValueError(
                f"Corrupted data in notification policy {policy_id} on FS: {e!s}"
            ) from e
        except Exception as e:
            logger.debug(
                "Persistence error retrieving notification policy from FS",
                policy_id=policy_id,
                error=str(e),
                exc_info=e,
            )
            raise Exception(  # noqa: TRY002
                f"Error retrieving notification policy {policy_id} from FS: {e!s}"
            ) from e

    async def get_notification_policy_by_name(
        self,
        name: str,
    ) -> NotificationPolicy | None:
        """
        Retrieve a notification policy by name.
        """
        criteria = {"name": name}

        try:
            policies = await self.find(
                index_name="by_name",
                criteria=criteria,
            )

            if not policies:
                return None

            return policies[0]
        except ValidationError as e:
            logger.debug(
                "Corrupted data found for notification policy on FS",
                name=name,
                error=str(e),
                exc_info=e,
            )
            raise ValueError(
                f"Corrupted data in notification policy {name} on FS: {e!s}"
            ) from e
        except Exception as e:
            logger.debug(
                "Persistence error retrieving notification policy by name",
                name=name,
                error=str(e),
                exc_info=e,
            )
            raise Exception(  # noqa: TRY002
                f"Error retrieving notification policy {name} from FS: {e!s}"
            ) from e

    async def list_notification_policies(
        self,
    ) -> list[NotificationPolicy]:
        """
        List all notification policies.
        """
        try:
            return await self.find()
        except Exception as e:
            logger.debug(
                "Persistence error listing notification policies",
                error=str(e),
                exc_info=e,
            )
            raise Exception(f"Error listing notification policies: {e!s}") from e  # noqa: TRY002

    async def delete_notification_policy(
        self,
        policy_id: str,
    ) -> None:
        """
        Delete a notification policy by canonical ID.
        """
        filename = f"{policy_id}.json"

        try:
            await self.delete(filename)
        except Exception as e:
            logger.debug(
                "Persistence error deleting notification policy from FS",
                policy_id=policy_id,
                error=str(e),
                exc_info=e,
            )
            raise Exception(  # noqa: TRY002
                f"Error deleting notification policy {policy_id} from FS: {e!s}"
            ) from e

    async def ping(self) -> bool:
        """
        Bridge the abstract requirement from the Port to the
        implementation in the Generic adapter.
        """
        return await self.ping_resource()
