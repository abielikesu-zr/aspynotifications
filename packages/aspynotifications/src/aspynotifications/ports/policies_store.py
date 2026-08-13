from abc import ABC, abstractmethod

from aspynotifications.entities.notification_policy import NotificationPolicy


class NotificationPolicyStore(ABC):
    """
    Interface for notification policy persistence.
    Pure persistence — no business logic.
    All methods are async.
    """

    @abstractmethod
    async def ping(self) -> bool:
        """
        Check whether the notification policy store is available.
        """

    @abstractmethod
    async def save_notification_policy(
        self,
        policy: NotificationPolicy,
    ) -> None:
        """
        Persist a notification policy.
        Can be used for both creation and update.
        """

    @abstractmethod
    async def get_notification_policy_by_id(
        self,
        policy_id: str,
    ) -> NotificationPolicy | None:
        """
        Retrieve a notification policy by canonical ID.
        """

    @abstractmethod
    async def get_notification_policy_by_name(
        self,
        name: str,
    ) -> NotificationPolicy | None:
        """
        Retrieve a notification policy by name.
        """

    @abstractmethod
    async def list_notification_policies(
        self,
    ) -> list[NotificationPolicy]:
        """
        List all notification policies.
        """

    @abstractmethod
    async def delete_notification_policy(
        self,
        policy_id: str,
    ) -> None:
        """
        Delete a notification policy by canonical ID.
        """
