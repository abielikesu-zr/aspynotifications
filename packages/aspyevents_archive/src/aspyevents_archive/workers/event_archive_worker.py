from typing import Any

import structlog
from aspyevents.services.events_facade import EventsFacade
from aspyevents_dtos.cloud_event_dto import CloudEventDTO
from aspyevents_dtos.save_event_request import SaveEventRequest
from aspyevents_worker.config.cloud_events_worker_config import CloudEventsWorkerConfig
from aspyevents_worker.workers.cloud_events_worker import CloudEventsWorker

logger = structlog.get_logger(__name__)


class EventsArchiveWorker(CloudEventsWorker):
    def __init__(
        self,
        config: dict[str, Any],
        events_facade: EventsFacade,
    ) -> None:
        self.config = CloudEventsWorkerConfig.model_validate(config)
        self.name = self.config.name
        super().__init__(name=self.name, config=self.config)
        self.events_facade = events_facade

    async def handle(self, cloud_event: CloudEventDTO) -> None:
        logger.info(
            "Processing CloudEvent",
            worker=self.name,
            event_type=cloud_event.type,
            source=cloud_event.source,
            subject=cloud_event.subject,
        )

        try:
            request = SaveEventRequest(event=cloud_event)
            await self.events_facade.save_event(request)

            logger.info(
                "CloudEvent processed",
                worker=self.name,
                event_type=cloud_event.type,
                source=cloud_event.source,
                subject=cloud_event.subject,
            )

        except Exception:
            logger.exception(
                "CloudEvent processing failed",
                worker=self.name,
                event_type=cloud_event.type,
                source=cloud_event.source,
                subject=cloud_event.subject,
            )
            raise
