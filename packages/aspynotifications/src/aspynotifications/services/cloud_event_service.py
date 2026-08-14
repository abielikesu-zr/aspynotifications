import structlog

from aspynotifications.config.cloud_template import CloudEventServiceConfig
from aspynotifications.entities.cloud_event import CloudEvent
from aspynotifications.ports.cloud_event_port import ICloudEventStorePort

logger = structlog.get_logger(__name__)


class CloudEventService:
    def __init__(self, config: dict, store: ICloudEventStorePort):
        self._config = CloudEventServiceConfig.model_validate(config)
        self._store = store

    async def create_cloud_event(self, cloud_event: CloudEvent) -> CloudEvent:
        log = logger.bind(function="create_cloud_event")
        try:
            await self._store.save_cloud_event(cloud_event)

            log.debug(
                "Cloud event created",
                event_id=cloud_event.id,
                event_type=cloud_event.type,
            )
            return cloud_event

        except Exception as e:
            log.error(
                "Failed to create cloud event",
                event_id=cloud_event.id,
                error=str(e),
                exc_info=e,
            )
            raise

    async def get_cloud_event_by_id(
        self,
        event_id: str,
    ) -> CloudEvent | None:
        log = logger.bind(function="get_cloud_event_by_id")
        try:
            cloud_event = await self._store.get_cloud_event(event_id)

            if cloud_event:
                log.debug("Cloud event found", event_id=event_id)
            else:
                log.debug("Cloud event not found", event_id=event_id)

            return cloud_event

        except Exception as e:
            log.error(
                "Failed to get cloud event",
                event_id=event_id,
                error=str(e),
                exc_info=e,
            )
            raise

    async def list_cloud_events(self) -> list[CloudEvent]:
        log = logger.bind(function="list_cloud_events")
        try:
            cloud_events = await self._store.list_cloud_events()

            log.debug(
                "Cloud events listed",
                count=len(cloud_events),
            )
            return cloud_events

        except Exception as e:
            log.error(
                "Failed to list cloud events",
                error=str(e),
                exc_info=e,
            )
            raise

    async def ping(self) -> bool:
        log = logger.bind(function="ping")
        try:
            ping_resource = await self._store.ping()

            log.debug(
                "Ping store",
                ping_resource=ping_resource,
            )
            return ping_resource

        except Exception as e:
            log.error(
                "Failed to ping",
                error=str(e),
                exc_info=e,
            )
            raise
