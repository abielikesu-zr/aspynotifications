from typing import Any

import structlog
from aspyevents_worker.config.cloud_events_worker_config import CloudEventsWorkerConfig
from aspyevents_worker.workers.cloud_events_worker import CloudEventsWorker
from aspynotifications.services.notifications_facade import NotificationsFacade
from aspynotifications_dtos.cloud_event_dto import CloudEventDTO

logger = structlog.get_logger(__name__)


class NotificationsWorker(CloudEventsWorker):
    def __init__(
        self,
        name: str,
        config: dict[str, Any],
        notifications_facade: NotificationsFacade,
    ) -> None:
        self.config = CloudEventsWorkerConfig.model_validate(config)
        super().__init__(name, self.config)
        self.notifications_facade = notifications_facade

    async def get_subscriptions(self) -> list[str]:
        response = await self.notifications_facade.get_subscriptions()
        return response.subscriptions

    async def handle(self, cloud_event: CloudEventDTO) -> None:
        logger.info(
            "Processing CloudEvent",
            worker=self.name,
            event_type=cloud_event.type,
            source=cloud_event.source,
            subject=cloud_event.subject,
        )

        try:
            await self.notifications_facade.notify(cloud_event)

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
