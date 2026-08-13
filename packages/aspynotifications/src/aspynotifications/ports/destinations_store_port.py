from abc import ABC, abstractmethod

from aspynotifications.entities.destination import Destination


class IDestinationStorePort(ABC):
    """Persistence contract for destinations."""

    @abstractmethod
    async def save_destination(self, destination: Destination) -> None:
        """Persist a destination record for creation or update."""

    @abstractmethod
    async def get_destination(self, destination_id: str) -> Destination | None:
        """Retrieve a destination by its canonical identifier."""

    @abstractmethod
    async def get_destination_by_name(
        self,
        destination_name: str,
    ) -> Destination | None:
        """Retrieve a destination by name."""

    @abstractmethod
    async def list_destinations(self) -> list[Destination]:
        """List all destinations."""

    @abstractmethod
    async def delete_destination(self, destination_id: str) -> None:
        """Delete a destination by its canonical identifier."""

    @abstractmethod
    async def ping(self) -> bool:
        """Verify that the underlying store is healthy and reachable."""
