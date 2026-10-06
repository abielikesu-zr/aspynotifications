from __future__ import annotations

import asyncio
import ssl
from typing import Any

import structlog
from aspynats.config.nats_client_config import NatsClientConfig
from aspynats.config.nats_connection_config import NatsConnectionConfig
from aspynats.workers.manager_worker import ensure_stream
from nats import connect
from nats.aio.client import Client
from nats.js import JetStreamContext

from aspyevents_worker.workers.cloud_events_worker import CloudEventsWorker

logger = structlog.get_logger(__name__)


class BareWorkerRunner:
    """
    Base class containing the common worker startup sequence.

    Caller is responsible for calling load_config before run.

    Subclasses must define DEFAULT_CONFIG, CONFIG_ROOT and PACKAGE_NAME.
    """

    def __init__(self, worker: CloudEventsWorker, config: dict[str, Any]) -> None:
        self.worker = worker
        self.nc: Client | None = None
        self.js: JetStreamContext | None = None
        self._worker_task: asyncio.Task | None = None

        self.config = NatsClientConfig.model_validate(config)

    def _create_ssl_context(
        self,
        config: NatsConnectionConfig,
    ) -> ssl.SSLContext | None:
        if not any(
            (
                config.tls_ca_file,
                config.tls_cert_file,
                config.tls_key_file,
            )
        ):
            return None

        ssl_context = ssl.create_default_context(
            cafile=config.tls_ca_file,
        )

        if config.tls_cert_file or config.tls_key_file:
            if not config.tls_cert_file or not config.tls_key_file:
                raise ValueError(
                    "Both tls_cert_file and tls_key_file must be configured "
                    "when using a client certificate."
                )

            ssl_context.load_cert_chain(
                certfile=config.tls_cert_file,
                keyfile=config.tls_key_file,
            )

        return ssl_context

    async def start(self) -> None:
        logger.info(
            "Worker starting",
            worker=self.worker.name,
        )

        ssl_context = self._create_ssl_context(self.config.connection)

        self.nc = await connect(
            self.config.connection.nats_url,
            user=self.config.connection.username,
            password=self.config.connection.password,
            tls=ssl_context,
        )

        self.js = self.nc.jetstream()

        await ensure_stream(js=self.js, config=self.config.stream)

        logger.info(
            "NATS JetStream connection established",
            worker=self.worker.name,
        )

        self._worker_task = asyncio.create_task(
            self.worker.run(self.js, stream_config=self.config.stream),
            name=f"{self.worker.name}-worker",
        )

        logger.info(
            "Starting worker",
            worker=self.worker.name,
        )

    async def stop(self) -> None:
        """Gracefully cancels worker task and closes NATS connection."""
        logger.info("Stopping worker", worker=self.worker.name)

        if self._worker_task and not self._worker_task.done():
            self._worker_task.cancel()
            await asyncio.gather(self._worker_task, return_exceptions=True)

        if self.nc is not None:
            await self.nc.drain()
            await self.nc.close()

        logger.info("Worker stopped")
