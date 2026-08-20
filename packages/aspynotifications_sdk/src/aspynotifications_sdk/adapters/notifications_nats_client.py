import json
from typing import Any, Dict

import nats
import structlog

from aspynats.config.nats_client_config import NatsClientConfig
from aspynotifications_dtos.cloud_event_dto import CloudEventDTO
from aspynotifications_dtos.notify_request import CreateNotifyRequest
from aspyplugs.registry import register_plugin
from aspynats.workers.manager_worker import ensure_stream
from nats.js import JetStreamContext
from nats.aio.client import Client as NATS

logger = structlog.get_logger(__name__)

@register_plugin("notifications_client", "NATS")
class NotificationsNatsClient:
    def __init__(self, config: Dict[str, Any]):
        self._config = NatsClientConfig.model_validate(config)
        self._nats_url = self._config.connection.nats_url
        self.js: JetStreamContext | None = None
        self.nc: NATS | None = None

    async def connect(self) -> None:
        self.nc = await nats.connect(self._nats_url)
        self.js = self.nc.jetstream()
        await ensure_stream(js=self.js, config=self._config.stream)

    # async def disconect(self) -> None:
    #     await self.nc.close()

    async def ensure_connection(self) -> None:
        if not self.js or not self.nc:
            await self.connect()

    async def publish(self, event: CloudEventDTO) -> None:
        await self.ensure_connection()
        subject = f"notify.{event.type}"
        payload = json.dumps(event.model_dump(mode="json")).encode()
        await self.js.publish(subject, payload)  # type: ignore[union-attr]

    async def notify(self, request: CreateNotifyRequest) -> str:
        await self.publish(request.event)
        return "published"
