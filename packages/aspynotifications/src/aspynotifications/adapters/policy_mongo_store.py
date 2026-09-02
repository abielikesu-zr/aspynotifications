import structlog
from aspyadapters.adapters.generic_mongo_db_adapter import (
    GenericMongoAdapter,
    NotFoundError,
)
from aspyplugs.registry import register_plugin
from pydantic import BaseModel, ValidationError

from aspynotifications.entities.notification_policy import NotificationPolicy
from aspynotifications.ports.policies_store import NotificationPolicyStore

logger = structlog.get_logger(__name__)


@register_plugin("notification_policy_store", "MONGODB")
class NotificationPolicyStoreMongoAdapter(
    NotificationPolicyStore,
    GenericMongoAdapter,
):
    """
    Asynchronous persistence adapter for NotificationPolicy entities,
    using MongoDB.
    """

    def get_model_class(self) -> type[BaseModel]:  # type: ignore[override]
        """Specify the Pydantic model used by this adapter."""
        return NotificationPolicy

    def get_collection_name(self) -> str:
        """Return the MongoDB collection name."""
        return "notification_policies"

    async def save_notification_policy(
        self,
        policy: NotificationPolicy,
    ) -> None:
        """
        Save a notification policy.

        Handles both creation and updating.
        """
        key = f"{policy.id}"

        try:
            await self.save(key, policy)
        except Exception as e:
            logger.error(
                "Persistence error saving notification policy",
                policy_id=policy.id,
                error=str(e),
                exc_info=e,
            )
            raise Exception(  # noqa: TRY002
                f"Error saving notification policy {policy.id}: {e!s}"
            ) from e

    async def get_notification_policy_by_id(
        self,
        policy_id: str,
    ) -> NotificationPolicy | None:
        """
        Retrieve a notification policy by its canonical ID.
        """
        key = f"{policy_id}"

        try:
            return await self.load(key)
        except NotFoundError:
            return None
        except ValidationError as e:
            logger.error(
                "Corrupted data found for notification policy",
                policy_id=policy_id,
                error=str(e),
                exc_info=e,
            )
            raise ValueError(
                f"Corrupted data in notification policy {policy_id}: {e!s}"
            ) from e
        except Exception as e:
            logger.error(
                "Persistence error retrieving notification policy",
                policy_id=policy_id,
                error=str(e),
                exc_info=e,
            )
            raise Exception(  # noqa: TRY002
                f"Error retrieving notification policy {policy_id}: {e!s}"
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
            result = await self.find_one(criteria=criteria)  # type: ignore[func-returns-value]
        except NotFoundError:
            return None
        except ValidationError as e:
            logger.error(
                "Corrupted data found while retrieving notification policy by name",
                name=name,
                error=str(e),
                exc_info=e,
            )
            raise ValueError(
                f"Corrupted data in notification policy with name {name}: {e!s}"
            ) from e
        except Exception as e:
            logger.error(
                "Persistence error retrieving notification policy by name",
                name=name,
                error=str(e),
                exc_info=e,
            )
            raise Exception(  # noqa: TRY002
                f"Error retrieving notification policy with name {name}: {e!s}"
            ) from e

        return result

    async def list_notification_policies(
        self,
    ) -> list[NotificationPolicy]:
        """
        Retrieve all notification policies.
        """
        try:
            return await self.find()
        except ValidationError as e:
            logger.error(
                "Corrupted data found while listing notification policies",
                error=str(e),
                exc_info=e,
            )
            raise ValueError(f"Corrupted data in notification policies: {e!s}") from e
        except Exception as e:
            logger.error(
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
        key = f"{policy_id}"

        try:
            await self.delete(key)
        except NotFoundError:
            return
        except Exception as e:
            logger.error(
                "Persistence error deleting notification policy",
                policy_id=policy_id,
                error=str(e),
                exc_info=e,
            )
            raise Exception(  # noqa: TRY002
                f"Error deleting notification policy {policy_id}: {e!s}"
            ) from e

    async def ping(self) -> bool:
        """
        Bridge the abstract requirement from the Port to the
        implementation in the Generic adapter.
        """
        return await self.ping_resource()
