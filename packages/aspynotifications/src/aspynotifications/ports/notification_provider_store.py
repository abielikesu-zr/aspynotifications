from abc import ABC, abstractmethod

from aspynotifications.entities.notification_provider import NotificationProvider


class NotificationProviderStore(ABC):
    """
    Interface for notification provider persistence.
    Pure persistence — no business logic.
    All methods are async.
    """

    @abstractmethod
    async def ping(self) -> bool:
        """
        Check whether the notification provider store is available.
        """

    @abstractmethod
    async def save_notification_provider(
        self,
        provider: NotificationProvider,
    ) -> None:
        """
        Persist a notification provider.
        Can be used for both creation and update.
        """

    @abstractmethod
    async def get_notification_provider_by_id(
        self,
        provider_id: str,
    ) -> NotificationProvider | None:
        """
        Retrieve a notification provider by canonical ID.
        """

    @abstractmethod
    async def get_notification_provider_by_name(
        self,
        name: str,
    ) -> NotificationProvider | None:
        """
        Retrieve a notification provider by name.
        """

    @abstractmethod
    async def list_notification_providers(
        self,
    ) -> list[NotificationProvider]:
        """
        List all notification providers.
        """

    @abstractmethod
    async def delete_notification_provider(
        self,
        provider_id: str,
    ) -> None:
        """
        Delete a notification provider by canonical ID.
        """
