from typing import Any

import structlog
from aspyevents_dtos.cloud_event_dto import CloudEventDTO
from aspyevents_worker.config.cloud_events_worker_config import CloudEventsWorkerConfig
from aspyevents_worker.workers.cloud_events_worker import CloudEventsWorker
from aspynotifications.services.notifications_facade import NotificationsFacade
from aspynotifications_dtos.notify_event_request import CreateNotifyRequest

logger = structlog.get_logger(__name__)


class NotificationsWorker(CloudEventsWorker):
    def __init__(
        self,
        config: dict[str, Any],
        notifications_facade: NotificationsFacade,
    ) -> None:
        cfg = CloudEventsWorkerConfig.model_validate(config)
        super().__init__(name=cfg.name, config=cfg)
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

        request = CreateNotifyRequest(event=cloud_event)
        await self.notifications_facade.notify(request)

        logger.info(
            "CloudEvent processed",
            worker=self.name,
            event_type=cloud_event.type,
            source=cloud_event.source,
            subject=cloud_event.subject,
        )
