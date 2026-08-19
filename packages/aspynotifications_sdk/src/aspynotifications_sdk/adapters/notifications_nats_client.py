import json
from typing import Any, Dict

import nats
import structlog

from aspynotifications_dtos.cloud_event_dto import CloudEventDTO
from aspynotifications_dtos.notify_request import CreateNotifyRequest
from aspynotifications_sdk.entities.config import NatsClientParams

logger = structlog.get_logger(__name__)


class NotificationsNatsClient:
    def __init__(self, config: Dict[str, Any]):
        self._config = NatsClientParams.model_validate(config)
        self._nats_url = self._config.nats_url

    async def publish(self, event: CloudEventDTO) -> None:
        subject = f"notify.{event.type}"
        nc = await nats.connect(self._nats_url)
        js = nc.jetstream()
        payload = json.dumps(event.model_dump(mode="json")).encode()
        await js.publish(subject, payload)
        await nc.close()

    async def notify(self, request: CreateNotifyRequest) -> str:
        await self.publish(request.event)
        return "published"
