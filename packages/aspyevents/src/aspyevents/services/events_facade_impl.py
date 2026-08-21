from typing import Any

import structlog
from aspyevents_dtos.notify_request import CreateNotifyRequest

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

    async def notify(self, request: CreateNotifyRequest) -> str:
        logger.debug("Processing notification request")

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

        existing_event = await self._cloud_event_service.get_cloud_event_by_id(
            cloud_event.id
        )

        logger.debug(
            "Checked for existing CloudEvent",
            event_id=cloud_event.id,
            exists=existing_event is not None,
        )

        if existing_event is not None:
            logger.info(
                "Notification already processed",
                event_id=cloud_event.id,
            )
            return "ok"

        await self._cloud_event_service.create_cloud_event(cloud_event)

        logger.debug(
            "CloudEvent persisted",
            event_id=cloud_event.id,
        )

        event = cloud_event.model_dump(exclude_none=True)

        logger.debug(
            "Building notification policy context",
            event_id=cloud_event.id,
        )

        context = self._event_transformer.transform(event)

        logger.debug(
            "Notification policy context built",
            event_id=cloud_event.id,
            context=context,
        )

        logger.debug(
            "Finding matching notification policies",
            event_id=cloud_event.id,
            event_type=cloud_event.type,
            subject=cloud_event.subject,
        )

        return "ok"
