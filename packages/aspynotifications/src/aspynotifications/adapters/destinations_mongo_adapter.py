import structlog
from aspyadapters.adapters.generic_mongo_db_adapter import (
    GenericMongoAdapter,
    NotFoundError,
)
from aspyplugs.registry import register_plugin
from pydantic import BaseModel, ValidationError

from aspynotifications.entities.destination import Destination
from aspynotifications.ports.destinations_store_port import IDestinationStorePort

logger = structlog.get_logger(__name__)


@register_plugin("destinations_store", "MONGODB")
class DestinationsMongoStoreAdapter(IDestinationStorePort, GenericMongoAdapter):
    """MongoDB persistence adapter for destinations."""

    def get_model_class(self) -> type[BaseModel]:  # type: ignore[override]
        return Destination

    def get_collection_name(self) -> str:
        return "destinations"

    async def save_destination(self, destination: Destination) -> None:
        try:
            await self.save(destination.id, destination)
        except Exception as error:
            logger.error(
                "Persistence error saving destination to MongoDB",
                destination_id=destination.id,
                error=str(error),
                exc_info=error,
            )
            raise Exception(  # noqa: TRY002
                f"Error saving destination {destination.id} to MongoDB"
            ) from error

    async def get_destination(self, destination_id: str) -> Destination | None:
        try:
            return await self.load(destination_id)
        except NotFoundError:
            return None
        except ValidationError as error:
            logger.error(
                "Corrupted destination data in MongoDB",
                destination_id=destination_id,
                error=str(error),
                exc_info=error,
            )
            raise ValueError(
                f"Corrupted destination data for {destination_id}"
            ) from error
        except Exception as error:
            logger.error(
                "Persistence error retrieving destination from MongoDB",
                destination_id=destination_id,
                error=str(error),
                exc_info=error,
            )
            raise Exception(  # noqa: TRY002
                f"Error retrieving destination {destination_id} from MongoDB"
            ) from error

    async def get_destination_by_name(
        self,
        destination_name: str,
    ) -> Destination | None:
        try:
            return await self.find_one(criteria={"name": destination_name})  # type: ignore[func-returns-value]
        except ValidationError as error:
            logger.error(
                "Corrupted destination data in MongoDB",
                destination_name=destination_name,
                error=str(error),
                exc_info=error,
            )
            raise ValueError(
                f"Corrupted destination data for {destination_name}"
            ) from error
        except Exception as error:
            logger.error(
                "Persistence error retrieving destination by name from MongoDB",
                destination_name=destination_name,
                error=str(error),
               exc_info=error,
            )
            raise Exception(  # noqa: TRY002
                "Error retrieving destination by name from MongoDB"
            ) from error

    async def list_destinations(self) -> list[Destination]:
        try:
            return await self.find()
        except Exception as error:
            logger.error(
                "Persistence error listing destinations from MongoDB",
                error=str(error),
                exc_info=error,
            )
            raise Exception("Error listing destinations from MongoDB") from error  # noqa: TRY002

    async def delete_destination(self, destination_id: str) -> None:
        try:
            await self.delete(destination_id)
        except Exception as error:
            logger.error(
                "Persistence error deleting destination from MongoDB",
                destination_id=destination_id,
                error=str(error),
                exc_info=error,
            )
            raise Exception(  # noqa: TRY002
                f"Error deleting destination {destination_id} from MongoDB"
            ) from error

    async def ping(self) -> bool:
        return await self.ping_resource()
