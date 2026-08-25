import uuid

from aspynotifications.config.app_config import DestinationsServiceConfig
from aspynotifications.config.destination_config import DestinationConfig
from aspynotifications.entities.destination import Destination
from aspynotifications.entities.exceptions import DestinationAlreadyExistsError
from aspynotifications.ports.destinations_store_port import IDestinationStorePort


class DestinationsService:
    """Business service for destination CRUD operations."""

    def __init__(self, config: dict, store: IDestinationStorePort):
        self._config = DestinationsServiceConfig.model_validate(config)
        self._store = store

    async def ping(self) -> bool:
        return await self._store.ping()

    async def create_destination(
        self,
        name: str,
        provider: str,
        template: str,
        config: DestinationConfig,
    ) -> Destination:
        destination = Destination(
            id=str(uuid.uuid4()),
            name=name,
            provider=provider,
            type=config.type,
            template=template,
            config=config,
        )

        existing = await self.get_destination_by_name(destination.name)
        if existing is not None:
            raise DestinationAlreadyExistsError(
                f"Destination name already exists: {name}"
            )

        await self._store.save_destination(destination)
        return destination

    async def get_destination_by_id(self, destination_id: str) -> Destination | None:
        return await self._store.get_destination(destination_id)

    async def get_destination_by_name(
        self,
        destination_name: str,
    ) -> Destination | None:
        return await self._store.get_destination_by_name(destination_name)

    async def list_destinations(self) -> list[Destination]:
        return await self._store.list_destinations()

    async def update_destination(self, destination: Destination) -> Destination:
        existing = await self.get_destination_by_id(destination.id)
        if existing is None:
            raise ValueError(f"Destination not found: {destination.id}")

        duplicate = await self.get_destination_by_name(destination.name)
        if duplicate is not None and duplicate.id != destination.id:
            raise ValueError(f"Destination name already exists: {destination.name}")

        await self._store.save_destination(destination)
        return destination

    async def delete_destination(self, destination_id: str) -> None:
        destination = await self.get_destination_by_id(destination_id)
        if destination is None:
            raise ValueError(f"Destination not found: {destination_id}")

        await self._store.delete_destination(destination_id)
