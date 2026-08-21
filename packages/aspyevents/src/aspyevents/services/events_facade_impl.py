from typing import Any

import structlog
from aspyevents_dtos.save_event_request import SaveEventRequest

from aspyevents.config.events_facade_config import EventsFacadeConfig
from aspyevents.entities.cloud_event import CloudEvent
from aspyevents.services.cloud_event_context_transformer import (
    CloudEventPolicyContextTransformer,
)
from aspyevents.services.cloud_event_service import CloudEventService
from aspyevents.services.events_facade import EventsFacade

logger = structlog.get_logger(__name__)


class EventsFacadeImpl(EventsFacade):
    def __init__(
        self,
        cloud_event_service: CloudEventService,
        event_transformer: CloudEventPolicyContextTransformer,
        config: dict[str, Any],
    ) -> None:
        self.config = EventsFacadeConfig.model_validate(config)
        self._event_transformer = event_transformer
        self._cloud_event_service = cloud_event_service

    async def save_event(self, request: SaveEventRequest) -> str:
        logger.debug("Processing save event request")

        cloud_event = CloudEvent.model_validate(
            request.event.model_dump(exclude_none=True)
        )

        logger.debug(
            "CloudEvent validated",
            event_id=cloud_event.id,
            event_type=cloud_event.type,
            source=cloud_event.source,
            subject=cloud_event.subject,
        )

        await self._cloud_event_service.create_cloud_event(cloud_event)

        logger.debug(
            "CloudEvent persisted",
            event_id=cloud_event.id,
        )

        return "ok"
