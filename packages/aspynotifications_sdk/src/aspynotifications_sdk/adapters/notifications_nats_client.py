import json
from typing import Any, Dict

import nats
import structlog

from aspynotifications_dtos.cloud_event_dto import CloudEventDTO
from aspynotifications_dtos.notify_request import CreateNotifyRequest
from aspynats.config.nats_connection_config import NatsConnectionConfig
from aspynats.config.nats_worker_config import NatsStreamConfig
from aspyplugs.registry import register_plugin
from aspynats.workers.manager_worker import ensure_stream

logger = structlog.get_logger(__name__)


@register_plugin("notification_event_store", "NATS")
class NotificationsNatsClient:
    def __init__(self, config: Dict[str, Any]):
        self._config = NatsConnectionConfig.model_validate(config)
        self._nats_url = self._config.nats_url

    async def publish(self, event: CloudEventDTO) -> None:
        subject = f"notify.{event.type}"
        nc = await nats.connect(self._nats_url)
        js = nc.jetstream()
        await ensure_stream(js=js, config=NatsStreamConfig(subject="notify.>"))

        payload = json.dumps(event.model_dump(mode="json")).encode()
        await js.publish(subject, payload)
        await nc.close()

    async def notify(self, request: CreateNotifyRequest) -> str:
        await self.publish(request.event)
        return "published"
