import structlog
from aspyadapters.adapters.generic_mongo_db_adapter import (
    GenericMongoAdapter,
    NotFoundError,
)
from aspyplugs.registry import register_plugin
from pydantic import BaseModel, ValidationError

from aspyevents.entities.cloud_event import CloudEvent
from aspyevents.ports.cloud_event_port import ICloudEventStorePort

logger = structlog.get_logger(__name__)


@register_plugin("cloud_event_store", "MONGODB")
class CloudEventMongoStoreAdapter(ICloudEventStorePort, GenericMongoAdapter):
    def get_model_class(self) -> type[BaseModel]:  # type: ignore[override]
        return CloudEvent

    def get_collection_name(self) -> str:
        return "cloud_events"

    async def save_cloud_event(self, cloud_event: CloudEvent) -> None:
        try:
            await self.save(cloud_event.id, cloud_event)
        except Exception as e:
            logger.error(
                "Persistence error saving cloud event to Mongo",
                event_id=cloud_event.id,
                error=str(e),
                exc_info=e,
            )
            raise

    async def get_cloud_event(self, event_id: str) -> CloudEvent | None:
        try:
            return await self.load(event_id)
        except NotFoundError:
            return None
        except ValidationError as e:
            logger.error(
                "Corrupted cloud event data found in Mongo",
                event_id=event_id,
                error=str(e),
                exc_info=e,
            )
            raise

    async def list_cloud_events(self) -> list[CloudEvent]:
        try:
            return await self.find()
        except Exception as e:
            logger.error(
                "Persistence error listing cloud events",
                error=str(e),
                exc_info=e,
            )
            raise Exception(f"Error listing cloud events: {e!s}") from e

    async def ping(self) -> bool:
        try:
            return await self.ping_resource()
        except Exception as e:
            logger.error("PING error", error=str(e), exc_info=e)
            return False
