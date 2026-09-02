import structlog
from aspyadapters.adapters.generic_local_fs import GenericLocalFSAdapter
from aspyplugs.registry import register_plugin
from pydantic import BaseModel, ValidationError

from aspynotifications.entities.destination import Destination
from aspynotifications.ports.destinations_store_port import IDestinationStorePort

logger = structlog.get_logger(__name__)


@register_plugin("destinations_store", "LOCALFS")
class DestinationsStoreAdapter(IDestinationStorePort, GenericLocalFSAdapter):
    """Local-file persistence adapter for destinations."""

    def get_model_class(self) -> type[BaseModel]:  # type: ignore[override]
        return Destination

    def get_index_declarations(self) -> dict[str, list[str]]:
        return {"by_name": ["name"]}

    async def save_destination(self, destination: Destination) -> None:
        try:
            await self.save(filename=f"{destination.id}.json", data=destination)
        except Exception as error:
            logger.error(
                "Persistence error saving destination to local filesystem",
                destination_id=destination.id,
                error=str(error),
                exc_info=error,
            )
            raise Exception(
                f"Error saving destination {destination.id} to local filesystem"
            ) from error

    async def get_destination(self, destination_id: str) -> Destination | None:
        try:
            return await self.load(f"{destination_id}.json")
        except FileNotFoundError:
            return None
        except ValidationError as error:
            logger.error(
                "Corrupted destination data in local filesystem",
                destination_id=destination_id,
                error=str(error),
                exc_info=error,
            )
            raise ValueError(
                f"Corrupted destination data for {destination_id}"
            ) from error
        except Exception as error:
            logger.error(
                "Persistence error retrieving destination from local filesystem",
                destination_id=destination_id,
                error=str(error),
                exc_info=error,
            )
            raise Exception(
                f"Error retrieving destination {destination_id} from local filesystem"
            ) from error

    async def get_destination_by_name(
        self,
        destination_name: str,
    ) -> Destination | None:
        try:
            return await self.find_one(
                index_name="by_name",
                criteria={"name": destination_name},
            )  # type: ignore[func-returns-value]
        except ValidationError as error:
            logger.error(
                "Corrupted destination data in local filesystem",
                destination_name=destination_name,
                error=str(error),
                exc_info=error,
            )
            raise ValueError(
                f"Corrupted destination data for {destination_name}"
            ) from error
        except Exception as error:
            logger.error(
                "Persistence error retrieving destination by name from local filesystem",
                destination_name=destination_name,
                error=str(error),
                exc_info=error,
            )
            raise Exception(
                "Error retrieving destination by name from local filesystem"
            ) from error

    async def list_destinations(self) -> list[Destination]:
        try:
            return await self.find()
        except ValidationError as error:
            logger.error(
                "Corrupted destination data in local filesystem",
                error=str(error),
                exc_info=error,
            )
            raise ValueError("Corrupted destination data") from error
        except Exception as error:
            logger.error(
                "Persistence error listing destinations from local filesystem",
                error=str(error),
                exc_info=error,
            )
            raise Exception(
                "Error listing destinations from local filesystem"
            ) from error

    async def delete_destination(self, destination_id: str) -> None:
        try:
            await self.delete(f"{destination_id}.json")
        except FileNotFoundError:
            return
        except Exception as error:
            logger.error(
                "Persistence error deleting destination from local filesystem",
                destination_id=destination_id,
                error=str(error),
                exc_info=error,
            )
            raise Exception(
                f"Error deleting destination {destination_id} from local filesystem"
            ) from error

    async def ping(self) -> bool:
        return await self.ping_resource()
