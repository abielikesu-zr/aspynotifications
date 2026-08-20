import structlog
from aspyadapters.adapters.generic_local_fs import GenericLocalFSAdapter
from aspyplugs.registry import register_plugin
from pydantic import BaseModel, ValidationError

from aspynotifications.entities.cloud_event import CloudEvent
from aspynotifications.ports.cloud_event_port import ICloudEventStorePort

logger = structlog.get_logger(__name__)


@register_plugin("cloud_event_store", "LOCALFS")
class CloudEventFileStoreAdapter(ICloudEventStorePort, GenericLocalFSAdapter):
    def get_model_class(self) -> type[BaseModel]:  # type: ignore[override]
        return CloudEvent

    async def save_cloud_event(self, cloud_event: CloudEvent) -> None:
        filename = f"{cloud_event.id}.json"
        try:
            await self.save(filename, cloud_event)
        except Exception as e:
            logger.error(
                "Persistence error saving cloud event to FS",
                event_id=cloud_event.id,
                error=str(e),
                exc_info=e,
            )
            raise Exception(  # noqa: TRY002
                f"Error saving cloud event {cloud_event.id} to FS: {e!s}"
            ) from e

    async def get_cloud_event(self, event_id: str) -> CloudEvent | None:
        filename = f"{event_id}.json"
        try:
            return await self.load(filename)
        except FileNotFoundError:
            return None
        except ValidationError as e:
            logger.error(
                "Corrupted cloud event data found on FS",
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
